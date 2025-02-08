# SRT-Link
SRT-Link is a SubRip cleaner that allows to filter, merge, and order SRT file sections.
It is written in Python, requires only standard libraries and no 3rd party dependencies.

## Installation

*Tested and developed on python-3.10*

```shell
pip install srt-link
```

or git clone:
```shell
git clone https://github.com/EliaOnceAgain/SRT-Link.git
cd SRT-Link/
pip install .
```
## Usage

Provide a SubRip file as input to run with default configs and output to stdout
```shell
python -m srt_link input.srt
```

Check the `--help` section for more information and custom configs 
```shell
$ python -m srt_link --help

usage: srt_link [-h] [-o OUTPUT_FILE] [--parentheses] [--curly-brackets] [--angle-brackets] 
                [--square-brackets] [--max-digits MAX_DIGITS] [--min-duration MIN_DURATION] 
                [--faces FACES_TO_SKIP] [--text TEXT_TO_SKIP] [--debug] input_file

SRT-Link: filter, merge, and order SubRip file sections

positional arguments:
  input_file                            srt input file path

options:
  -h, --help                            show this help message and exit
  -o OUTPUT_FILE, --output OUTPUT_FILE  output file [default=stdout]
  --parentheses                         filter parentheses [default=True]
  --curly-brackets                      filter curly brackets [default=True]
  --angle-brackets                      filter angle brackets [default=True]
  --square-brackets                     filter square brackets [default=True]
  --max-digits MAX_DIGITS               max number of digits allowed [default=10]
  --min-duration MIN_DURATION           min section duration in seconds [default=0.3]
  --faces FACES_TO_SKIP                 comma separated faces to filter
  --text TEXT_TO_SKIP                   comma separates text to filter
  --debug                               print debug logs
```

#### Example usage
To filter a sections with face `face-1` or `face 2`, or contains the text `does not support`, 
and remove any and all parenthesis and brackets, run:
```shell
python3 -m srt_link input.srt --faces "face-1,face 2" --text "does not support"
```

Provided the following example `input.srt`
```text
$ cat input.srt
1
00:00:01,000 --> 00:00:02,000
<font face="face-1">Try 1</font>

2
00:00:02,000 --> 00:00:03,000
<font face="face 2">Try 2</font>

3
00:00:03,000 --> 00:00:04,000
<font face="pass">this media player does not support some media file</font>

4
00:00:04,000 --> 00:00:05,000
<font face="pass">{\an8}Lorem ipsum dolor sit amet(584.445,26.5,584.445,26.5)(0,240,\clip(562.797,8,606.094,45)</font>
```
The result would be:
```text
$ python3 -m srt_link --faces "face-1,face 2" --text "does not support" test.srt
1
00:00:04,000 --> 00:00:05,000
Lorem ipsum dolor sit amet
```

## Issues
Not working as expected? Open an issue and upload a minimal SubRip file that reproduces the issue and the output 
with debug logs using the cli flag `--debug`


## How it works
The solution is based on a doubly linked list, here's an overview of the steps to add a new section to the linked list:
- A new section is read from the input SubRip file
- The section is filtered based on the provided configs
- Add the section to the end of the linked list
- If the new section starts before the tail section ends (**tail = last section in the linked list**)
  - Resolve the overlap issue based on one of the cases below
  - If the new section begins *before* tail, delegate the new section to the previous section (see last case below)

In all cases below, (A) is tail, and (B) is the new section to be added.
```text
### New section starts at the same time as tail
# Case 1: Exact overlap
> Initial state
|-------------|     (A)
|-------------|     (B)
> Final state
|-------------|
     (A+B)

# Case 2: New section ends before tail
> Initial state
|-------------|     (A)
|--------|          (B)
> Final state:
|--------|----|
   (A+B)   (A)
   
# Case 3: new section ends after tail
> Initial state
|--------|          (A)
|-------------|     (B)
> Final state:
|--------|----|
   (A+B)   (B)

### New section starts before tail ends
# Case 1: same end
> Initial state
|-------------|     (A)
       |------|     (B)
> Final state
|------|------|
  (A)    (A+B)

# Case 2: new section ends after tail
> Initial state
|---------|         (A)
     |---------|    (B)
> Final state
|----|----|----|
 (A)  (A+B) (B)
 
# Case 3: new section ends before tail
> Initial state
|------------|      (A)
    |----|          (B)
> Final state
|---|----|---|
 (A) (A+B) (A)

### New section starts before tail
> Initial state
          |------------|    (A)
|--------------|            (B)
> Final state
|--------|------|-----|
 (prev+B)  (A+B)  (A)
```
