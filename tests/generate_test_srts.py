from srt_link.models.section import Section
from srt_link.models.input_filter import SectionFilter
from srt_link.models.base import SRTSections


class SRTGenerator(SRTSections):
    def __init__(self):
        super().__init__()
        self.section_filter = SectionFilter(
            faces_to_skip=["FACE SKIP 1", ],
            text_to_skip=["TEXT-SKIP",],
            filter_parentheses=True,
            filter_curly_brackets=True,
            filter_angle_brackets=True,
            filter_square_brackets=True,
            max_digits=10,
            min_duration=0.3
        )
        self.raw_fd = open("raw.srt", "w")
        self.raw_id = 1

    def add(self, time: str, body: str) -> None:
        section = f"{self.raw_id}\n{time}\n{body}\n\n"
        section_obj = Section.from_str(section)
        self.raw_fd.write(f"{self.raw_id}\n{section_obj}\n\n")
        self.raw_id += 1
        super().add(section, self.section_filter)


srtgen = SRTGenerator()

srtgen.add(time="00:00:01,000 --> 00:00:02,000", body="Unchanged-1")
srtgen.add(time="00:00:02,000 --> 00:00:03,000", body="Unchanged-2")
srtgen.add(time="00:00:04,000 --> 00:00:05,000", body="Unchanged-3")

srtgen.add(time="00:00:06,000 --> 00:00:07,000", body="Same start case 1, same text")
srtgen.add(time="00:00:06,000 --> 00:00:07,000", body="Same start case 1, same text")
srtgen.add(time="00:00:07,000 --> 00:00:08,000", body="Same start case 1, text 1")
srtgen.add(time="00:00:07,000 --> 00:00:08,000", body="Same start case 1, text 2")

srtgen.add(time="00:00:10,000 --> 00:00:12,000", body="Same start case 2, same text")
srtgen.add(time="00:00:10,000 --> 00:00:11,000", body="Same start case 2, same text")
srtgen.add(time="00:00:15,000 --> 00:00:17,000", body="Same start case 2, text 1")
srtgen.add(time="00:00:15,000 --> 00:00:16,000", body="Same start case 2, text 2")

srtgen.add(time="00:00:20,000 --> 00:00:22,000", body="Same start case 3, same text")
srtgen.add(time="00:00:20,000 --> 00:00:24,000", body="Same start case 3, same text")
srtgen.add(time="00:00:25,000 --> 00:00:27,000", body="Same start case 3, text 1")
srtgen.add(time="00:00:25,000 --> 00:00:28,000", body="Same start case 3, text 2")

srtgen.add(time="00:00:30,000 --> 00:00:34,000", body="Start before case 1, same text")
srtgen.add(time="00:00:32,000 --> 00:00:34,000", body="Start before case 1, same text")
srtgen.add(time="00:00:35,000 --> 00:00:39,000", body="Start before case 1, text 1")
srtgen.add(time="00:00:37,000 --> 00:00:39,000", body="Start before case 1, text 2")

srtgen.add(time="00:00:40,000 --> 00:00:43,000", body="Start before case 2, same text")
srtgen.add(time="00:00:42,000 --> 00:00:44,000", body="Start before case 2, same text")
srtgen.add(time="00:00:45,000 --> 00:00:47,000", body="Start before case 2, text 1")
srtgen.add(time="00:00:46,000 --> 00:00:49,000", body="Start before case 2, text 2")

srtgen.add(time="00:00:50,000 --> 00:00:54,000", body="Start before case 3, same text")
srtgen.add(time="00:00:52,000 --> 00:00:53,000", body="Start before case 3, same text")
srtgen.add(time="00:00:55,000 --> 00:00:59,000", body="Start before case 3, text 1")
srtgen.add(time="00:00:56,000 --> 00:00:58,000", body="Start before case 3, text 2")

srtgen.add(time="00:01:15,000 --> 00:01:20,000", body="Start after end before, same text")
srtgen.add(time="00:01:12,000 --> 00:01:14,000", body="Start after end before, same text")
srtgen.add(time="00:01:25,000 --> 00:01:30,000", body="Start after end before, text 1")
srtgen.add(time="00:01:22,000 --> 00:01:24,000", body="Start after end before, text 2")

srtgen.add(time="00:01:35,000 --> 00:01:39,000", body="Start after with overlap, same text")
srtgen.add(time="00:01:32,000 --> 00:01:37,000", body="Start after with overlap, same text")
srtgen.add(time="00:01:45,000 --> 00:01:49,000", body="Start after with overlap, text 1")
srtgen.add(time="00:01:42,000 --> 00:01:47,000", body="Start after with overlap, text 2")

srtgen.add(time="00:02:05,000 --> 00:02:10,000", body="Start after and outreach, same text")
srtgen.add(time="00:02:02,000 --> 00:02:12,000", body="Start after and outreach, same text")
srtgen.add(time="00:02:15,000 --> 00:02:20,000", body="Start after and outreach, text 1")
srtgen.add(time="00:02:12,000 --> 00:02:22,000", body="Start after and outreach, text 2")

srtgen.add(time="00:03:00,000 --> 00:03:01,000", body="1 2 3 4 5 6 7 8 9 10")
srtgen.add(time="00:03:01,000 --> 00:03:01,200", body="short duration")
srtgen.add(time="00:03:02,000 --> 00:03:02,200", body="(hello world)")
srtgen.add(time="00:03:03,000 --> 00:03:03,200", body="<hello world>")
srtgen.add(time="00:03:04,000 --> 00:03:04,200", body="[hello world]")
srtgen.add(time="00:03:05,000 --> 00:03:05,200", body="{hello world}")
srtgen.add(time="00:03:06,000 --> 00:03:06,200", body="{[<(hello world)>]}")
srtgen.add(time="00:03:07,000 --> 00:03:08,200", body="<font face='FACE SKIP 1'>hello world</font>")
srtgen.add(time="00:03:07,000 --> 00:03:08,200", body="<font face='VALID-FACE'>hello world TEXT-SKIP hello world</font>")
srtgen.add(time="00:03:07,000 --> 00:03:08,200", body="<font face='VALID-FACE'>goodbye...</font>")

srtgen.dump_to_file("ref.srt")
