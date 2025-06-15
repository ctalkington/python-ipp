"""Data Serializer for IPP."""
from __future__ import annotations

import logging
import random
import struct
from typing import Any

from .const import DEFAULT_PROTO_VERSION
from .enums import IppTag
from .tags import ATTRIBUTE_TAG_MAP

_LOGGER = logging.getLogger(__name__)

class UnsupportedAttributeError(RuntimeError):
    """Some attribute name in a message is unsupported."""

    def __init__(self, name: str) -> None:
        """Initialize Exception with name of unsupported attribute."""
        super(Exception, self).__init__(name)

class DatatypeMismatchError(RuntimeError):
    """Some attribute value has an unexpected data type."""

    def __init__(self, msg: str) -> None:
        """Initialize Exception with message."""
        super(Exception, self).__init__(msg)

def construct_attribute_values(tag: IppTag, value: Any) -> bytes:
    """Serialize the attribute values into IPP format."""
    byte_str = b""

    if tag in (IppTag.INTEGER, IppTag.ENUM):
        byte_str += struct.pack(">h", 4)
        byte_str += struct.pack(">i", value)
    elif tag == IppTag.BOOLEAN:
        byte_str += struct.pack(">h", 1)
        byte_str += struct.pack(">?", value)
    else:
        encoded_value = value.encode("utf-8")
        byte_str += struct.pack(">h", len(encoded_value))
        byte_str += encoded_value

    return byte_str


def construct_attribute(name: str, value: Any, tag: IppTag | None = None) -> bytes:
    """Serialize the attribute into IPP format."""
    byte_str = b""

    if not tag and not (tag := ATTRIBUTE_TAG_MAP.get(name, None)):
        raise UnsupportedAttributeError(name)

    if isinstance(value, (list, tuple, set)):
        for index, list_value in enumerate(value):
            byte_str += struct.pack(">b", tag.value)

            if index == 0:
                byte_str += struct.pack(">h", len(name))
                byte_str += name.encode("utf-8")
            else:
                byte_str += struct.pack(">h", 0)

            byte_str += construct_attribute_values(tag, list_value)
    elif isinstance(value, dict):
        if tag != IppTag.BEGIN_COLLECTION:
            msg = (f"Attribute {name} has data of type dict, but "
                   f"its tag is not a collection but a {tag}")
            raise DatatypeMismatchError(msg)
        byte_str += struct.pack(">b", tag.value)  # value-tag
        byte_str += struct.pack(">h", len(name))  # name-length
        byte_str += name.encode("utf-8")          # name
        byte_str += struct.pack(">h", 0)          # value-length
        for k, v in value.items():
            byte_str += struct.pack(">b", IppTag.MEMBER_NAME.value)  # value-tag
            byte_str += struct.pack(">h", 0)       # name-length
            byte_str += struct.pack(">h", len(k))  # value-length
            byte_str += k.encode("utf-8")          # value (member-name)
            byte_str += construct_attribute(k, v)
        byte_str += struct.pack(">b", IppTag.END_COLLECTION.value)  # end-value-tag
        byte_str += struct.pack(">h", 0)          # end-name-length
        byte_str += struct.pack(">h", 0)          # end-value-length

    else:
        byte_str = struct.pack(">b", tag.value)

        byte_str += struct.pack(">h", len(name))
        byte_str += name.encode("utf-8")

        byte_str += construct_attribute_values(tag, value)

    return byte_str


def encode_dict(data: dict[str, Any]) -> bytes:
    """Serialize a dictionary of data into IPP format."""
    version = data["version"] or DEFAULT_PROTO_VERSION
    operation = data["operation"]

    if (request_id := data.get("request-id")) is None:
        request_id = random.choice(range(10000, 99999))  # nosec  # noqa: S311

    encoded = struct.pack(">bb", *version)
    encoded += struct.pack(">h", operation.value)
    encoded += struct.pack(">i", request_id)

    encoded += struct.pack(">b", IppTag.OPERATION.value)

    if isinstance(data.get("operation-attributes-tag"), dict):
        for attr, value in data["operation-attributes-tag"].items():
            encoded += construct_attribute(attr, value)

    if isinstance(data.get("job-attributes-tag"), dict):
        encoded += struct.pack(">b", IppTag.JOB.value)

        for attr, value in data["job-attributes-tag"].items():
            encoded += construct_attribute(attr, value)

    if isinstance(data.get("printer-attributes-tag"), dict):
        encoded += struct.pack(">b", IppTag.PRINTER.value)

        for attr, value in data["printer-attributes-tag"].items():
            encoded += construct_attribute(attr, value)

    encoded += struct.pack(">b", IppTag.END.value)

    if "data" in data:
        encoded += data["data"]

    return encoded
