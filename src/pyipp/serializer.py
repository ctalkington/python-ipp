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
        _LOGGER.debug("Unknown IppTag for %s", name)
        return byte_str

    if isinstance(value, (list, tuple, set)):
        for index, list_value in enumerate(value):
            byte_str += struct.pack(">b", tag.value)

            if index == 0:
                byte_str += struct.pack(">h", len(name))
                byte_str += name.encode("utf-8")
            else:
                byte_str += struct.pack(">h", 0)

            byte_str += construct_attribute_values(tag, list_value)
    else:
        byte_str = struct.pack(">b", tag.value)

        byte_str += struct.pack(">h", len(name))
        byte_str += name.encode("utf-8")

        byte_str += construct_attribute_values(tag, value)

    return byte_str


def encode_collection(name: str, collection: dict[str, Any]) -> bytes:
    """Encode a dict representing an IPP collection as a byte string.

    Args:
    ----
        name (str): The name of the collection
        collection (dict[str, Any]): The collection contents

    Returns:
    -------
        bytes: A binary string representing the collection
    """
    byte_str = b""

    byte_str += struct.pack(">b", IppTag.BEGIN_COLLECTION.value)
    byte_str += struct.pack(">h", len(name))
    byte_str += name.encode("utf-8")
    byte_str += struct.pack(">h", 0)

    for member_name, value in collection.items():
        if isinstance(value, dict):
            byte_str += encode_collection(name=member_name, collection=value)
        else:
            byte_str += struct.pack(">b", IppTag.MEMBER_NAME.value)
            byte_str += struct.pack(">h", 0)
            byte_str += struct.pack(">h", len(member_name))
            byte_str += member_name.encode("utf-8")
            if isinstance(value, int):
                byte_str += struct.pack(">b", IppTag.INTEGER.value)
                byte_str += struct.pack(">h", 0)
                byte_str += struct.pack(">h", 4)
                byte_str += struct.pack(">h", value)
            else:
                byte_str += struct.pack(">b", IppTag.KEYWORD.value)
                byte_str += struct.pack(">h", 0)
                byte_str += struct.pack(">h", len(value))
                byte_str += value.encode("utf-8")

    byte_str += struct.pack(">b", IppTag.END_COLLECTION.value)
    byte_str += struct.pack(">h", 0)
    byte_str += struct.pack(">h", 0)

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
            encoded += (
                encode_collection(attr, value)
                if isinstance(value, dict)
                else construct_attribute(attr, value)
            )

    if isinstance(data.get("printer-attributes-tag"), dict):
        encoded += struct.pack(">b", IppTag.PRINTER.value)

        for attr, value in data["printer-attributes-tag"].items():
            encoded += construct_attribute(attr, value)

    encoded += struct.pack(">b", IppTag.END.value)

    if "data" in data:
        encoded += data["data"]

    return encoded
