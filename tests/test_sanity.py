from pathlib import Path

from srt_link import __version__, run
from srt_link.models.input_filter import SectionFilter


def test_version():
    assert __version__ == "0.1.0"


def test_sanity():
    ref_path = Path(__file__).parent / "ref.srt"
    out_path = Path(__file__).parent / "out.srt"
    section_filter = SectionFilter(
        faces_to_skip=["FACE SKIP 1", ],
        text_to_skip=["TEXT-SKIP", ],
        filter_parentheses=True,
        filter_curly_brackets=True,
        filter_angle_brackets=True,
        filter_square_brackets=True,
        max_digits=10,
        min_duration=0.3
    )
    run(input_file=Path(__file__).parent / "raw.srt", output_file=out_path, input_filter=section_filter)
    with open(ref_path, "r") as ref_fd, open(out_path, "r") as out_fd:
        assert ref_fd.read() == out_fd.read()
    out_path.unlink()
