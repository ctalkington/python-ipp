"""Data Serializer for IPP."""

from __future__ import annotations

import logging
import random
import struct
from typing import Any, Iterable

from .const import DEFAULT_PROTO_VERSION
from .enums import IppTag
from .tags import ATTRIBUTE_TAG_MAP

_LOGGER = logging.getLogger(__name__)


class IppAttribute(object):
    """
    Wrapper for job, printer and operation attributes.

    If an attribute you're attempting to send with your operation is not in the
    `ATTRIBUTE_TAG_MAP`, this module will ignore serializing it, unless you
    wrap the value of the attribute in an IppAttribute (with the correct
    `IppTag` supplied on the constructor).  This will allow the serialization
    machinery to know how to serialize your desired attribute.

    To serialize collections, just use a plain `dict()`.

    Example code using `IppAttribute`s:

        async with pyipp.IPP(
            host="localhost",
            port=631,
            base_path="/printers/Cups-PDF",
            tls=False,
            verify_ssl=True,
        ) as ipp:
            opattrs: dict[str, Any] = {"document-format": "text/plain"}
            jobattrs: dict[str, Any] = {}
            jobattrs["media-col"] = {
                "media-size": {
                    "x-dimension": IppAttribute(IppTag.INTEGER, 21590),  # ; US Letter Width
                    "y-dimension": IppAttribute(IppTag.INTEGER, 27940),  # ; US Letter Length
                },
            }
            jobattrs["print-scaling"] = IppAttribute(IppTag.KEYWORD, "none")

            pp = {
                "operation-attributes-tag": opattrs,
                "job-attributes-tag": jobattrs,
                "data": "hello world!".encode(
                    "utf-8"
                ),
            }
            await ipp.execute(
                pyipp.enums.IppOperation.PRINT_JOB,
                pp,
            )
        )
    """

    def __init__(self, tag: IppTag, value: Any):
        self.tag = tag
        self.value = value


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

    if not isinstance(value, IppAttribute) and not isinstance(value, dict):
        if not tag and not (tag := ATTRIBUTE_TAG_MAP.get(name, None)):
            _LOGGER.warning("Unknown IppTag for %s", name)
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
    elif isinstance(value, IppAttribute):
        byte_str = struct.pack(">b", value.tag.value)

        byte_str += struct.pack(">h", len(name))
        byte_str += name.encode("utf-8")

        byte_str += construct_attribute_values(value.tag.value, value.value)
    elif isinstance(value, dict):
        if value:
            byte_str = struct.pack(">b", IppTag.BEGIN_COLLECTION)
            encoded_name = name.encode("utf-8")
            byte_str += struct.pack(">h", len(encoded_name))
            byte_str += encoded_name
            byte_str += struct.pack(">h", 0)  # no value
            for k, v in value.items():
                byte_str += struct.pack(">b", IppTag.MEMBER_NAME)
                byte_str += struct.pack(">h", 0)
                encoded_k = k.encode("utf-8")
                byte_str += struct.pack(">h", len(encoded_k))
                byte_str += encoded_k
                if isinstance(v, dict):
                    # K must be empty string now, since we have already
                    # serialized K here, so the first two items after
                    # begCollection must be zero-length markers.
                    k = ""
                    byte_str += construct_attribute(k, v)
                else:
                    # Same here.
                    k = ""
                    byte_str += construct_attribute(k, v)
            byte_str += struct.pack(">b", IppTag.END_COLLECTION)
            byte_str += struct.pack(">h", 0)
            byte_str += struct.pack(">h", 0)
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
