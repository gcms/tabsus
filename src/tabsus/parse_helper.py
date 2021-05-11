import re

COMMENT_PATTERN = re.compile(r';.*$')


def strip_comments(line):
    return COMMENT_PATTERN.sub('', line)
