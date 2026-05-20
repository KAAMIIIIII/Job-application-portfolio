import re


def to_camel(s: str) -> str:
    return re.sub(r'_([a-z])', lambda m: m.group(1).upper(), s)


def camelize(val):
    if isinstance(val, list):
        return [camelize(item) for item in val]
    if isinstance(val, dict):
        return {to_camel(k): camelize(v) for k, v in val.items()}
    return val
