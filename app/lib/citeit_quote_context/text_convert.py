# Copyright (C) 2015-2020 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
_copyright__ = "Copyright (C) 2015-2020 Tim Langeman"
__license__ = "MIT"
__version__ = "0.4"


from bs4 import BeautifulSoup
import difflib
import settings
import re

class TextConvert:
    """ Remove the following characters from a string.
        This is often used the normalize the Quote Hash:
            escape(quote)|escape_url(citing)escape_url(cited)
    """
    def __init__(self, str, url=None):
        self.str = str  # page's html, containing potential link, meta tags

    def escape(self):
        return escape_text(self.str)

    def escape_url(self):
        return escape_url(self.str)


def html_to_text(html_str):
    soup = BeautifulSoup(html_str, 'html.parser')
    return soup.get_text()


def escape_text(str, escape_hex=True):
    """Remove characters from the string"""
    str_return = ''

    # Filter out str characters with Unicode code points
    if settings.TEXT_ESCAPE_CODE_POINTS:
        for char in str:
            if (ord(char) not in settings.TEXT_ESCAPE_CODE_POINTS):
                str_return = str_return + char

    # Filter out specific characters
    if settings.ESCAPE_SPECIAL_CHARS:
        for special_char in settings.ESCAPE_SPECIAL_CHARS:
            str_return = str_return.replace(special_char, '')

    # Filter out characters matching a specific pattern
    if escape_hex:

        # Consider \u00e2\u0080\u0099 as a single character instead of 3 seperate
        # https://patrickwu.space/2017/11/09/python-encoding-issue/
        #str_return = re.sub(r'[\xc2-\xf4][\x80-\xbf]+',
        #                       lambda m: m.group(0).encode('latin1').decode(
        #                           'utf8'), str_return)

        pass

        # Examples of Characters to match and remove:
        # '\u00e2\u0080\u009d',   # "â"
        # '\u00e2\u0080\u009c',   # LEFT DOUBLE QUOTATION MARK
        # '\u00e2\u0080\u0093',   # DASH
        # '\u00e2\u0080\u00a6',   # BROKEN BAR
        # '\u00e2\u0080\u0098',   # LEFT SINGLE QUOTATION
        # '\u00e2\u0080\u0099',   # RIGHT SINGLE QUOTATION

        # Create Regex pattern to match unicode escape stored in 3-bytes
        # hexaPattern = re.compile(r'[\xc2-\xf4][\x80-\xbf]+')
        # str_return = re.sub(hexaPattern, '', str_return)  # remove unicode hex characters

    return str_return


def escape_url(str):
    """Remove characters from the string"""
    str_return = ''
    for char in str:
        if (ord(char) not in settings.URL_ESCAPE_CODE_POINTS):
            str_return = str_return + char
    return str_return


def levenshtein_distance(word1, word2):
    """
    Credit: https://en.wikipedia.org/wiki/Levenshtein_distance
        :param word1:
        :param word2:
        :return:
    """
    word2 = word2.lower()
    word1 = word1.lower()
    matrix = [[0 for x in range(len(word2) + 1)] for x in range(len(word1) + 1)]

    for x in range(len(word1) + 1):
        matrix[x][0] = x
    for y in range(len(word2) + 1):
        matrix[0][y] = y

    for x in range(1, len(word1) + 1):
        for y in range(1, len(word2) + 1):
            if word1[x - 1] == word2[y - 1]:
                matrix[x][y] = min(
                    matrix[x - 1][y] + 1,
                    matrix[x - 1][y - 1],
                    matrix[x][y - 1] + 1
                )
            else:
                matrix[x][y] = min(
                    matrix[x - 1][y] + 1,
                    matrix[x - 1][y - 1] + 1,
                    matrix[x][y - 1] + 1
                )

    return matrix[len(word1)][len(word2)]


def show_diff(text, n_text):
    """
    Credit: http://stackoverflow.com/a/788780
        Unify operations between two compared strings seqm is a difflib.
        SequenceMatcher instance whose a & b are strings
    """
    seqm = difflib.SequenceMatcher(None, text, n_text)
    output = []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():

        if opcode == 'equal':
            # output.append(seqm.a[a0:a1])
            pass
        elif opcode == 'insert':
            output.append(seqm.b[b0:b1])
        elif opcode == 'delete':
            output.append(seqm.a[a0:a1])
        elif opcode == 'replace':
            output.append(seqm.b[b0:b1])

    return ''.join(output)