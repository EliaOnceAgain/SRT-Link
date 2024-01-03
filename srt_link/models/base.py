from __future__ import annotations
from datetime import time
from typing import Iterator, TextIO
import logging
import sys

from .input_filter import SectionFilter
from .section import Section

LOG = logging.getLogger()


class SRTSections:
    def __init__(self):
        self.head = Section(sts=time(0), ets=time(0), body="", skip=True)
        self.tail = self.head

    def iter_sections(self) -> Iterator[Section]:
        runner = self.head.next
        while runner:
            yield runner
            runner = runner.next

    def add(self, section: str, section_filter: SectionFilter | None = None) -> None:
        """filter happens before insert"""
        section = Section.from_str(section)
        if section_filter:
            section_filter.apply(section)
        if not section.skip:
            self.tail = self.tail.insert_after(section)
        LOG.debug(f"Link Length: {len(list(self.iter_sections()))}\n")

    def dump_to_file(self, path: str) -> None:
        with open(path, 'w') as fd:
            self.dump(fd)

    def dump(self, fd: TextIO | None = None) -> None:
        fd = fd or sys.stdout
        for runner_id, section in enumerate(self.iter_sections(), start=1):
            fd.write(f"{runner_id}\n{section}\n\n")
