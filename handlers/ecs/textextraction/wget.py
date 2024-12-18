#!/usr/bin/env python
"""
Download utility as an easy way to get file from the net
 
  python -m wget <URL>
  python wget.py <URL>

Downloads: http://pypi.python.org/pypi/wget/
Development: http://bitbucket.org/techtonik/python-wget/

wget.py is not option compatible with Unix wget utility,
to make command line interface intuitive for new people.

Public domain by anatoly techtonik <techtonik@gmail.com>
Also available under the terms of MIT license
Copyright (c) 2010-2014 anatoly techtonik

** Modified by Ranjan Shrestha Line number 302 to make it work on aws lambda function **
"""


import math
import os
import shutil
import sys
import tempfile

PY3K = sys.version_info >= (3, 0)
if PY3K:
    import urllib.parse as urlparse
    import urllib.request as urllib
else:
    import urllib

    import urlparse


__version__ = "2.3-beta1"


def filename_from_url(url):
    """:return: detected filename or None"""
    fname = os.path.basename(urlparse.urlparse(url).path)
    if len(fname.strip(" \n\t.")) == 0:
        return None
    return fname


def filename_from_headers(headers):
    """Detect filename from Content-Disposition headers if present.
    http://greenbytes.de/tech/tc2231/

    :param: headers as dict, list or string
    :return: filename from content-disposition header or None
    """
    if type(headers) == str:
        headers = headers.splitlines()
    if type(headers) == list:
        headers = dict([x.split(":", 1) for x in headers])
    cdisp = headers.get("Content-Disposition")
    if not cdisp:
        return None
    cdtype = cdisp.split(";")
    if len(cdtype) == 1:
        return None
    if cdtype[0].strip().lower() not in ("inline", "attachment"):
        return None
    # several filename params is illegal, but just in case
    fnames = [x for x in cdtype[1:] if x.strip().startswith("filename=")]
    if len(fnames) > 1:
        return None
    name = fnames[0].split("=")[1].strip(' \t"')
    name = os.path.basename(name)
    if not name:
        return None
    return name


def filename_fix_existing(filename):
    """Expands name portion of filename with numeric ' (x)' suffix to
    return filename that doesn't exist already.
    """
    dirname = "."
    name, ext = filename.rsplit(".", 1)
    names = [x for x in os.listdir(dirname) if x.startswith(name)]
    names = [x.rsplit(".", 1)[0] for x in names]
    suffixes = [x.replace(name, "") for x in names]
    # filter suffixes that match ' (x)' pattern
    suffixes = [x[2:-1] for x in suffixes if x.startswith(" (") and x.endswith(")")]
    indexes = [int(x) for x in suffixes if set(x) <= set("0123456789")]
    idx = 1
    if indexes:
        idx += sorted(indexes)[-1]
    return "%s (%d).%s" % (name, idx, ext)


# --- terminal/console output helpers ---


def get_console_width():
    """Return width of available window area. Autodetection works for
    Windows and POSIX platforms. Returns 80 for others

    Code from http://bitbucket.org/techtonik/python-pager
    """

    if os.name == "nt":
        STD_INPUT_HANDLE = -10
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE = -12

        # get console handle
        from ctypes import Structure, byref, windll

        try:
            from ctypes.wintypes import DWORD, SHORT, WORD
        except ImportError:
            # workaround for missing types in Python 2.5
            from ctypes import c_short as SHORT
            from ctypes import c_ulong as DWORD
            from ctypes import c_ushort as WORD
        console_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

        # CONSOLE_SCREEN_BUFFER_INFO Structure
        class COORD(Structure):
            _fields_ = [("X", SHORT), ("Y", SHORT)]

        class SMALL_RECT(Structure):
            _fields_ = [
                ("Left", SHORT),
                ("Top", SHORT),
                ("Right", SHORT),
                ("Bottom", SHORT),
            ]

        class CONSOLE_SCREEN_BUFFER_INFO(Structure):
            _fields_ = [
                ("dwSize", COORD),
                ("dwCursorPosition", COORD),
                ("wAttributes", WORD),
                ("srWindow", SMALL_RECT),
                ("dwMaximumWindowSize", DWORD),
            ]

        sbi = CONSOLE_SCREEN_BUFFER_INFO()
        ret = windll.kernel32.GetConsoleScreenBufferInfo(console_handle, byref(sbi))
        if ret == 0:
            return 0
        return sbi.srWindow.Right + 1

    elif os.name == "posix":
        from array import array
        from fcntl import ioctl
        from termios import TIOCGWINSZ

        winsize = array("H", [0] * 4)
        try:
            ioctl(sys.stdout.fileno(), TIOCGWINSZ, winsize)
        except IOError:
            pass
        return (winsize[1], winsize[0])[0]

    return 80


def bar_thermometer(current, total, width=80):
    """Return thermometer style progress bar string. `total` argument
    can not be zero. The minimum size of bar returned is 3. Example:

        [..........            ]

    Control and trailing symbols (\r and spaces) are not included.
    See `bar_adaptive` for more information.
    """
    # number of dots on thermometer scale
    avail_dots = width - 2
    shaded_dots = int(math.floor(float(current) / total * avail_dots))
    return "[" + "." * shaded_dots + " " * (avail_dots - shaded_dots) + "]"


def bar_adaptive(current, total, width=80):
    """Return progress bar string for given values in one of three
    styles depending on available width:

        [..  ] downloaded / total
        downloaded / total
        [.. ]

    if total value is unknown or <= 0, show bytes counter using two
    adaptive styles:

        %s / unknown
        %s

    if there is not enough space on the screen, do not display anything

    returned string doesn't include control characters like \r used to
    place cursor at the beginning of the line to erase previous content.

    this function leaves one free character at the end of string to
    avoid automatic linefeed on Windows.
    """

    # process special case when total size is unknown and return immediately
    if not total or total < 0:
        msg = "%s / unknown" % current
        if len(msg) < width:  # leaves one character to avoid linefeed
            return msg
        if len("%s" % current) < width:
            return "%s" % current

    # --- adaptive layout algorithm ---
    #
    # [x] describe the format of the progress bar
    # [x] describe min width for each data field
    # [x] set priorities for each element
    # [x] select elements to be shown
    #   [x] choose top priority element min_width < avail_width
    #   [x] lessen avail_width by value if min_width
    #   [x] exclude element from priority list and repeat

    #  10% [.. ]  10/100
    # pppp bbbbb sssssss

    min_width = {
        "percent": 4,  # 100%
        "bar": 3,  # [.]
        "size": len("%s" % total) * 2 + 3,  # 'xxxx / yyyy'
    }
    priority = ["percent", "bar", "size"]

    # select elements to show
    selected = []
    avail = width
    for field in priority:
        if min_width[field] < avail:
            selected.append(field)
            avail -= (
                min_width[field] + 1
            )  # +1 is for separator or for reserved space at
            # the end of line to avoid linefeed on Windows
    # render
    output = ""
    for field in selected:

        if field == "percent":
            # fixed size width for percentage
            output += ("%s%%" % (100 * current // total)).rjust(min_width["percent"])
        elif field == "bar":  # [. ]
            # bar takes its min width + all available space
            output += bar_thermometer(current, total, min_width["bar"] + avail)
        elif field == "size":
            # size field has a constant width (min == max)
            output += ("%s / %s" % (current, total)).rjust(min_width["size"])

        selected = selected[1:]
        if selected:
            output += " "  # add field separator

    return output


# --/ console helpers


__current_size = 0  # global state variable, which exists solely as a


# workaround against Python 3.3.0 regression
# http://bugs.python.org/issue16409
# fixed in Python 3.3.1
def callback_progress(blocks, block_size, total_size, bar_function):
    """callback function for urlretrieve that is called when connection is
    created and when once for each block

    draws adaptive progress bar in terminal/console

    use sys.stdout.write() instead of "print,", because it allows one more
    symbol at the line end without linefeed on Windows

    :param blocks: number of blocks transferred so far
    :param block_size: in bytes
    :param total_size: in bytes, can be -1 if server doesn't return it
    :param bar_function: another callback function to visualize progress
    """
    global __current_size

    width = min(100, get_console_width())

    if sys.version_info[:3] == (3, 3, 0):  # regression workaround
        if blocks == 0:  # first call
            __current_size = 0
        else:
            __current_size += block_size
        current_size = __current_size
    else:
        current_size = min(blocks * block_size, total_size)
    progress = bar_function(current_size, total_size, width)
    if progress:
        sys.stdout.write("\r" + progress)


class ThrowOnErrorOpener(urllib.FancyURLopener):
    def http_error_default(self, url, fp, errcode, errmsg, headers):
        raise Exception("%s: %s" % (errcode, errmsg))


def download(url, out=None, bar=bar_adaptive):
    """High level function, which downloads URL into tmp file in current
    directory and then renames it to filename autodetected from either URL
    or HTTP headers.

    :param bar: function to track download progress (visualize etc.)
    :param out: output filename or directory
    :return:    filename where URL is downloaded to
    """
    names = dict()
    names["out"] = out or ""
    names["url"] = filename_from_url(url)
    # get filename for temp file in current directory
    prefix = (names["url"] or names["out"] or ".") + "."
    (fd, tmpfile) = tempfile.mkstemp(".tmp", prefix=prefix, dir="/tmp")
    os.close(fd)
    os.unlink(tmpfile)

    # set progress monitoring callback
    def callback_charged(blocks, block_size, total_size):
        # 'closure' to set bar drawing function in callback
        callback_progress(blocks, block_size, total_size, bar_function=bar)

    if bar:
        callback = callback_charged
    else:
        callback = None

    (tmpfile, headers) = ThrowOnErrorOpener().retrieve(url, tmpfile, callback)
    names["header"] = filename_from_headers(headers)
    if os.path.isdir(names["out"]):
        filename = names["header"] or names["url"]
        filename = names["out"] + "/" + filename
    else:
        filename = names["out"] or names["header"] or names["url"]
    # add numeric ' (x)' suffix if filename already exists
    if os.path.exists(filename):
        filename = filename_fix_existing(filename)
    shutil.move(tmpfile, filename)

    # print headers
    return filename


usage = """\
usage: wget.py [options] URL

options:
  -o --output FILE|DIR   output filename or directory
  -h --help
  --version
"""

if __name__ == "__main__":
    if len(sys.argv) < 2 or "-h" in sys.argv or "--help" in sys.argv:
        sys.exit(usage)
    if "--version" in sys.argv:
        sys.exit("wget.py " + __version__)

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-o", "--output", dest="output")
    (options, args) = parser.parse_args()

    url = sys.argv[1]
    filename = download(args[0], out=options.output)

    print("")
    print("Saved under %s" % filename)

r"""
features that require more tuits for urlretrieve API
http://www.python.org/doc/2.6/library/urllib.html#urllib.urlretrieve

[x] autodetect filename from URL
[x] autodetect filename from headers - Content-Disposition
    http://greenbytes.de/tech/tc2231/
[ ] make HEAD request to detect temp filename from Content-Disposition
[ ] process HTTP status codes (i.e. 404 error)
    http://ftp.de.debian.org/debian/pool/iso-codes_3.24.2.orig.tar.bz2
[ ] catch KeyboardInterrupt
[ ] optionally preserve incomplete file
[x] create temp file in current directory
[ ] resume download (broken connection)
[ ] resume download (incomplete file)
[x] show progress indicator
    http://mail.python.org/pipermail/tutor/2005-May/038797.html
[x] do not overwrite downloaded file
 [x] rename file automatically if exists
[x] optionally specify path for downloaded file

[ ] options plan
 [x] -h, --help, --version (CHAOS speccy)
[ ] clpbar progress bar style
_ 30.0Mb at  3.0 Mbps  eta:   0:00:20   30% [=====         ]
[ ] test "bar \r" print with \r at the end of line on Windows
[ ] process Python 2.x urllib.ContentTooShortError exception gracefully
    (ideally retry and continue download)

    (tmpfile, headers) = urllib.urlretrieve(url, tmpfile, callback_progress)
  File "C:\Python27\lib\urllib.py", line 93, in urlretrieve
    return _urlopener.retrieve(url, filename, reporthook, data)
  File "C:\Python27\lib\urllib.py", line 283, in retrieve
    "of %i bytes" % (read, size), result)
urllib.ContentTooShortError: retrieval incomplete: got only 15239952 out of 24807571 bytes

[ ] find out if urlretrieve may return unicode headers
[ ] test suite for unsafe filenames from url and from headers

[ ] security checks
  [ ] filename_from_url
  [ ] filename_from_headers
  [ ] MITM redirect from https URL
  [ ] https certificate check
  [ ] size+hash check helpers
    [ ] fail if size is known and mismatch
    [ ] fail if hash mismatch
"""
