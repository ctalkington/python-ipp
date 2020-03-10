"""Data Serializer for IPP."""
import random
import struct
from typing import Any

from .const import DEFAULT_PROTO_VERSION
from .enums import IppTag
from .tags import ATTRIBUTE_TAG_MAP


def update_attribute_tag_map(attribute: str, tag: IppTag):
    """Update the attribute tag mapping."""
    ATTRIBUTE_TAG_MAP[attribute] = tag


def __construct_attibute_values(tag: IppTag, value):
    """Serialize the attribute values into IPP format."""
    bs = b""

    if tag in (IppTag.INTEGER, IppTag.ENUM):
        bs += struct.pack(">h", 4)
        bs += struct.pack(">i", value)
    elif tag == IppTag.BOOLEAN:
        bs += struct.pack(">h", 1)
        bs += struct.pack(">?", value)
    else:
        bs += struct.pack(">h", len(value))
        bs += value.encode("utf-8")

    return bs


def construct_attribute(name: str, value, tag=None):
    """Serialize the attribute into IPP format."""
    bs = b""

    if not tag:
        tag = ATTRIBUTE_TAG_MAP.get(name, None)

    if not tag:
        return bs

    if isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set):
        for index, v in enumerate(value):
            bs += struct.pack(">b", tag.value)

            if index == 0:
                bs += struct.pack(">h", len(name))
                bs += name.encode("utf-8")
            else:
                bs += struct.pack(">h", 0)

            bs += __construct_attibute_values(tag, v)
    else:
        bs = struct.pack(">b", tag.value)

        bs += struct.pack(">h", len(name))
        bs += name.encode("utf-8")

        bs += __construct_attibute_values(tag, value)

    return bs


def encode_dict(data: dict) -> Any:
    version = data["version"] or DEFAULT_PROTO_VERSION
    operation = data["operation"]
    request_id = data["id"] or "".join(random.sample("0123456789", 5))

    encoded = struct.pack(">bb", *version)
    encoded += struct.pack(">h", operation.value)
    encoded += struct.pack(">i", request_id)

    encoded += struct.pack(">b", IppTag.OPERATION.value)

    if isinstance(data["operation-attributes-tag"], dict):
        for attr, value in data["operation-attributes-tag"].items():
            data += construct_attribute(attr, value)

    if isinstance(data["job-attributes-tag"], dict):
        data += struct.pack(">b", IppTag.JOB.value)

        for attr, value in data["job-attributes-tag"].items():
            data += construct_attribute(attr, value)

    if isinstance(data["printer-attributes-tag"], dict):
        data += struct.pack(">b", IppTag.PRINTER.value)

        for attr, value in data["printer-attributes-tag"].items():
            data += construct_attribute(attr, value)

    data += struct.pack(">b", IppTag.END.value)

    return encoded
