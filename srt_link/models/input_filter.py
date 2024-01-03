from __future__ import annotations
from typing import List
import logging
import re

from .section import Section

LOG = logging.getLogger()


class SectionFilter:
    RE_FONT_FACE            = r'<font[^>]*\sface=["\']([^"\']+)["\'][^>]*>'
    RE_IGN_ANGLE_BRACKETS   = r'<[^>]*?>'
    RE_IGN_CURLY_BRACKETS   = r'{[^}]*?}'
    RE_IGN_SQUARE_BRACKETS  = r'\[[^\]]*?\]'
    RE_IGN_PARENTHESES      = r'\([^)]*?\)'

    def __init__(
            self,
            faces_to_skip: List[str] | None = None,
            text_to_skip: List[str] | None = None,
            filter_parentheses: bool = True,
            filter_curly_brackets: bool = True,
            filter_angle_brackets: bool = True,
            filter_square_brackets: bool = True,
            max_digits: int = 10,
            min_duration: float = 0.3,
            **kwargs
    ):
        self.max_digits = max_digits
        self.min_duration = min_duration
        self.faces_to_skip = faces_to_skip
        self.text_to_skip = text_to_skip
        filters = []
        if filter_parentheses:
            filters.append(self.RE_IGN_PARENTHESES)
        if filter_curly_brackets:
            filters.append(self.RE_IGN_CURLY_BRACKETS)
        if filter_angle_brackets:
            filters.append(self.RE_IGN_ANGLE_BRACKETS)
        if filter_square_brackets:
            filters.append(self.RE_IGN_SQUARE_BRACKETS)
        self.brackets_filter = '|'.join(filters)

    def font_filter(self, section: Section) -> bool:
        if not self.faces_to_skip:
            return False
        for face in re.compile(self.RE_FONT_FACE).findall(section.body):
            if face in self.faces_to_skip:
                LOG.debug(f"Skip - face filter matched: {face}")
                return True

    def text_filter(self, section: Section) -> bool:
        if not self.text_to_skip:
            return False
        for text in self.text_to_skip:
            if text in section.body:
                LOG.debug(f"Skip - text filter matched: {text}")
                return True

    def apply(self, section: Section) -> None:
        # Content filters
        if self.text_filter(section) or self.font_filter(section):
            section.skip = True
            return

        # Brackets filter
        section.body = re.compile(self.brackets_filter).sub('', section.body)

        # Digits count filter
        if len(re.sub("[^0-9]", "", section.body)) > self.max_digits:
            section.skip = True
            LOG.debug(f"Skip - max digits: {len(re.sub('[^0-9]', '', section.body))} > {self.max_digits}")
            return

        # Duration filter
        if section.duration < self.min_duration:
            section.skip = True
            LOG.debug(f"Skip - min duration: {section.duration} < {self.min_duration}")
            return
