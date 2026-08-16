import re

PHONE_REGEX = re.compile(r"^09\d{9}$")


def normalize_phone_number(value: str) -> str:
    value = value.strip().replace(" ", "").replace("-", "")

    if value.startswith("+98"):
        value = "0" + value[3:]
    elif value.startswith("0098"):
        value = "0" + value[4:]
    elif value.startswith("98") and len(value) == 12:
        value = "0" + value[2:]

    if not PHONE_REGEX.fullmatch(value):
        raise ValueError("شماره موبایل باید با 09 اغاز شود")

    return value