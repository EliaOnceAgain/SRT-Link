from __future__ import annotations
__version__ = "0.1.0"

from argparse import ArgumentParser, HelpFormatter
from itertools import pairwise
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from srt_link.models.section import Section
from srt_link.models.input_filter import SectionFilter
from srt_link.models.base import SRTSections

__all__ = [
    'Section',
    'SectionFilter',
    'SRTSections'
]

LOG_FORMATTER = '>>> %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.WARNING, format=LOG_FORMATTER)
LOG = logging.getLogger()


def parse():
    parser = ArgumentParser(
        description='SRT-Link: filter, merge, and order srt file sections',
        formatter_class=lambda prog: HelpFormatter(prog, max_help_position=50)
    )
    parser.add_argument('input_file', nargs=1, help="srt input file path")
    parser.add_argument('-o', '--output', dest='output_file', required=False, help='output file [default=stdout]')
    parser.add_argument('--parentheses', dest="filter_parentheses", default=True, action="store_true",
                        help="filter parentheses [default=True]")
    parser.add_argument('--curly-brackets', dest="filter_curly_brackets", default=True, action="store_true",
                        help="filter curly brackets [default=True]")
    parser.add_argument('--angle-brackets', dest="filter_angle_brackets", default=True, action="store_true",
                        help="filter angle brackets [default=True]")
    parser.add_argument('--square-brackets', dest="filter_square_brackets", default=True, action="store_true",
                        help="filter square brackets [default=True]")
    parser.add_argument('--max-digits', dest="max_digits", default=10, type=int,
                        help="max number of digits allowed [default=10]")
    parser.add_argument('--min-duration', dest="min_duration", default=0.3, type=float,
                        help="min section duration in seconds [default=0.3]")
    parser.add_argument('--faces', dest="faces_to_skip", default=None, type=str,
                        help="comma separated faces to filter")
    parser.add_argument('--text', dest="text_to_skip", default=None, type=str,
                        help="comma separates text to filter")
    parser.add_argument('--debug', dest='debug_mode', default=False, action="store_true", help="print debug logs")
    args = parser.parse_args()

    args.input_file = args.input_file[0]
    if args.output_file and not args.output_file.endswith(".srt"):
        args.output_file = args.output_file + ".srt"
    args.faces_to_skip = args.faces_to_skip.split(",") if args.faces_to_skip else None
    args.text_to_skip = args.text_to_skip.split(",") if args.text_to_skip else None
    if args.debug_mode:
        LOG.setLevel(logging.DEBUG)
        LOG.debug(">>> SRT-LINK DEBUG ENABLED <<<")
    return args


def run(input_file: str, output_file: str | None = None, input_filter: SectionFilter | None = None):
    sections = SRTSections()
    next_section = None
    with open(input_file, 'r', encoding='utf-8') as fd:
        contents = fd.read()
    for curr_section, next_section in pairwise(Section.HEADER_RE.finditer(contents)):
        section = contents[curr_section.start():next_section.start()]
        section_id = section.split("\n")[0]
        LOG.debug(f"Section: {section_id}")
        sections.add(section, section_filter=input_filter)
    if next_section:
        section = contents[next_section.start():]
        section_id = section.split("\n")[0]
        LOG.debug(f"Section: {section_id}")
        sections.add(section, section_filter=input_filter)
    sections.dump_to_file(output_file) if output_file else sections.dump()


def main():
    args = parse()
    input_filter = SectionFilter(**vars(args))
    return run(input_file=args.input_file, output_file=args.output_file, input_filter=input_filter)


if __name__ == "__main__":
    exit(main())
