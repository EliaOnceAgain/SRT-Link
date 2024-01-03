from __future__ import annotations
import datetime
import logging
import re

LOG = logging.getLogger()

SEC_TO_MS: int = 1000
MIN_TO_MS: int = SEC_TO_MS * 60
HOUR_TO_MS: int = MIN_TO_MS * 60


class Section:
    HEADER_RE = re.compile(r"(?P<id>\d+)\n(?P<sts>\d{2}:\d{2}:\d{2},\d{3}) --> (?P<ets>\d{2}:\d{2}:\d{2},\d{3})")
    HEADER_TS_RE = re.compile(r'(?P<sts>\d{2}:\d{2}:\d{2},\d{3}) --> (?P<ets>\d{2}:\d{2}:\d{2},\d{3})')

    def __init__(
            self,
            sts: datetime.time,             # start timestamp
            ets: datetime.time,             # end timestamp
            body: str,                      # subtitles text
            skip: bool = False,             # ignore on dump
            _prev: Section | None = None,   # prev srt section
            _next: Section | None = None    # next srt section
    ):
        self.prev = _prev
        self.next = _next
        self.sts = sts
        self.ets = ets
        self.body = body.strip("\n")
        self.skip = skip

    @property
    def duration(self):
        ets_ms = (self.ets.hour * HOUR_TO_MS + self.ets.minute * MIN_TO_MS +
                  self.ets.second * SEC_TO_MS + self.ets.microsecond // 1000)
        sts_ms = (self.sts.hour * HOUR_TO_MS + self.sts.minute * MIN_TO_MS +
                  self.sts.second * SEC_TO_MS + self.sts.microsecond // 1000)
        return (ets_ms - sts_ms) / SEC_TO_MS

    def link_next(self, other: Section) -> Section:
        LOG.debug(f"Linking: {self.sts} --> {self.ets} to {other.sts} --> {other.ets}")
        if self.next:
            self.next.prev = other
            other.next = self.next
        self.next = other
        other.prev = self
        return other

    def insert_before(self, other: Section) -> Section:
        return self.prev.insert_after(other)

    def insert_after(self, other: Section) -> Section:
        LOG.debug(f"Self: {self.sts} --> {self.ets}")
        LOG.debug(f"Other: {other.sts} --> {other.ets}")
        if self.ets > other.sts:
            LOG.debug(f"Overlap: self.ets={self.ets} > other.sts={other.sts}")
            if self.sts > other.sts:
                LOG.debug(f"Delegating: self.sts={self.sts} > other.sts={other.sts}")
                forward_overlap = self._handle_starts_after(other)
                if forward_overlap is None:
                    return self
                other = forward_overlap
            if self.sts == other.sts:
                LOG.debug(f"Same start: self.sts={self.sts} == other.sts={other.sts}")
                return self._handle_same_start(other)
            elif self.sts < other.sts:
                LOG.debug(f"Forward overlap: self.sts={self.sts} < other.sts={other.sts}")
                return self._handle_start_before(other)
            else:
                raise ValueError("Unexpected error...")
        return self.link_next(other)

    def _handle_starts_after(self, other: Section) -> Section | None:
        """Handle a new section that starts before this section
        
        > Initial state
                  |------------|    (A) self
        |--------------|            (B) other

        > Split (B)
                 |------------|     (A)
        |--------|------|           (B)

        > Final state
        |--------|------|-----|
         (prev+B) (A+B)   (A)

        1. Create a new section that ends at the beginning of this section
        2. Insert the created section before this section
        3. Handle the remaining overlap with this section if any

        Param:
            other (Section):    a section that starts before this section
        Returns:
            The overlap with this section if any, otherwise None
        """

        delegated_section = Section(sts=other.sts, ets=min(self.sts, other.ets), body=other.body)
        delegated_section.next = self
        self.insert_before(delegated_section)
        if self.sts >= other.ets:
            return None
        other.sts = self.sts
        return other

    def _handle_same_start(self, other: Section) -> Section:
        """Handle a new section that starts at the same time as this section

        ############################################
        Case 1: exact overlap

        > Initial state
        |-------------|     (A)
        |-------------|     (B)
        
        > Final state
        |-------------|
            (A + B)

        ############################################
        Case 2: new section ends before this section

        > Initial state
        |-------------|     (A)
        |--------|          (B)

        > Decrease (A) and merge bodies, increase (B) and set it as (A)'s body
           (A+B)
        |--------|          (A)
                 |----|     (B)
                   (A) 
        
        > Final state:
           (A+B)   (A)
        |--------|----|

        ############################################
        Case 3: new section ends after this section
        
        > Initial state
        |--------|          (A)
        |-------------|     (B)

        > Merge bodies for (A) and (B), decrease (B)
           (A+B)
        |--------|          (A)
                 |----|     (B)
                   (B) 
        
        > Final state:
           (A+B)   (B)
        |--------|----|

        Param:
            other (Section):    a section that starts at the same time as this section
        Returns:
            The last section in the linked list. In case (1) it's `self`, otherwise `other`.
        """
        
        if self.ets == other.ets:
            LOG.debug(f"Same start case 1: self.ets={self.ets} == other.ets={other.ets}")
            self.body = self.get_merged_body(other)
            return self
        elif self.ets > other.ets:
            LOG.debug(f"Same start case 2: self.ets={self.ets} > other.ets={other.ets}")
            other.sts = other.ets
            self.ets, other.ets = other.ets, self.ets
            other.body, self.body = self.body, self.get_merged_body(other)
            return self.link_next(other)
        else:
            LOG.debug(f"Same start case 3: self.ets={self.ets} < other.ets={other.ets}")
            other.sts = self.ets
            self.body = self.get_merged_body(other)
            return self.link_next(other)

    def _handle_start_before(self, other: Section) -> Section:
        """Handle a new section that starts after this section

        ############################################
        Case 1: same end

        > Initial state
        |-------------|     (A)
               |------|     (B)

        > Decrease (A)
        |------|            (A)
               |------|     (B)

        > Final state
        |------|------|
          (A)    (A+B)

        ############################################
        Case 2: new section ends after this section

        > Initial state
        |---------|         (A)
             |---------|    (B)

        > Split (B)
        |---------|         (A)
             |----|         (B1)
                  |----|    (B2) (original B)

        > Final state
        |----|----|----|
         (A)  (A+B) (B)

        ############################################
        Case 3: new section ends before this section

        > Initial state
        |------------|      (A)
            |----|          (B)

        > Split (A)
        |--------|          (A1) (original A)
            |----|          (B)
                 |---|      (A2)

        > Final state
        |---|----|---|
         (A) (A+B) (A)

        Param:
            other (Section):    a section that starts after this section
        Returns:
            The last section in the linked list. In case (1) and (2) it's `other`, in case (3) it's a new section.
        """

        if self.ets == other.ets:
            LOG.debug(f"Forward overlap case 1: self.ets={self.ets} == other.ets={other.ets}")
            self.ets = other.sts
            other.body = self.body if other.body in self.body else '\n'.join([self.body, other.body])
            return self.link_next(other)
        elif self.ets < other.ets:
            LOG.debug(f"Forward overlap case 2: self.ets={self.ets} < other.ets={other.ets}")
            new_section = Section(sts=other.sts, ets=self.ets, body=other.body)
            other.sts = self.ets
            return self.insert_after(new_section).link_next(other)
        else:
            LOG.debug(f"Forward overlap case 3: self.ets={self.ets} > other.ets={other.ets}")
            new_section = Section(sts=other.ets, ets=self.ets, body=self.body)
            self.ets = other.ets
            return self.insert_after(other).link_next(new_section)

    def get_merged_body(self, other: Section) -> str:
        if other.body in self.body:
            LOG.debug("Same body, no merge")
            return self.body
        LOG.debug("Merged bodies")
        return '\n'.join([self.body, other.body])

    def __str__(self) -> str:
        return "{sts} --> {ets}\n{body}".format(
            sts=self.sts.isoformat(timespec="milliseconds").replace(".", ","),
            ets=self.ets.isoformat(timespec="milliseconds").replace(".", ","),
            body=self.body.lstrip("\n")
        )

    @classmethod
    def from_str(cls, section: str) -> Section:
        lines = section.split("\n")
        sts, ets = cls.HEADER_TS_RE.match(lines[1]).groups()
        return cls(
            sts=datetime.time.fromisoformat(sts.replace(",", ".")),
            ets=datetime.time.fromisoformat(ets.replace(",", ".")),
            body='\n'.join(lines[2:])
        )
