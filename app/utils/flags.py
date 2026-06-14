from __future__ import annotations


def country_flag(country_code: str) -> str:
    code = (country_code or "").upper()
    if len(code) != 2:
        return ""
    return "".join(chr(127397 + ord(char)) for char in code)
