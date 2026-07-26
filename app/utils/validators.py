import re

PHONE_RE = re.compile(r'^\+?[0-9]{7,15}$')


def is_valid_phone(value):
    return bool(PHONE_RE.match(str(value)))
