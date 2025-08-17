"""Tests for Serializer."""

from pyipp import serializer
from pyipp.const import DEFAULT_CHARSET, DEFAULT_CHARSET_LANGUAGE, DEFAULT_PROTO_VERSION
from pyipp.enums import IppOperation, IppTag

from . import load_fixture_binary


def test_construct_attribute_values() -> None:
    """Test the construct_attribute_values method."""
    result = serializer.construct_attribute_values(
        IppTag.INTEGER,
        IppOperation.GET_PRINTER_ATTRIBUTES,
    )
    assert result == b"\x00\x04\x00\x00\x00\x0b"

    result = serializer.construct_attribute_values(
        IppTag.ENUM,
        IppOperation.GET_PRINTER_ATTRIBUTES,
    )
    assert result == b"\x00\x04\x00\x00\x00\x0b"

    result = serializer.construct_attribute_values(
        IppTag.BOOLEAN,
        "0",
    )
    assert result == b"\x00\x01\x01"

    result = serializer.construct_attribute_values(
        IppTag.URI,
        "ipps://localhost:631",
    )
    assert result == b"\x00\x14ipps://localhost:631"


def test_construct_attribute() -> None:
    """Test the construct_attribute method."""
    result = serializer.construct_attribute("attributes-charset", DEFAULT_CHARSET)
    assert result == b"G\x00\x12attributes-charset\x00\x05utf-8"

    result = serializer.construct_attribute(
        "operations-supported",
        [IppOperation.GET_PRINTER_ATTRIBUTES],
    )
    assert result == b"#\x00\x14operations-supported\x00\x04\x00\x00\x00\x0b"


def test_construct_attribute_no_tag_unmapped() -> None:
    """Test the construct_attribute method with no tag and unmapped attribute name."""
    result = serializer.construct_attribute(
        "no-tag-unmapped",
        None,
    )

    assert result == b""


def test_encode_dict() -> None:
    """Test the encode_dict method."""
    result = serializer.encode_dict(
        {
            "version": DEFAULT_PROTO_VERSION,
            "operation": IppOperation.GET_PRINTER_ATTRIBUTES,
            "request-id": 1,
            "operation-attributes-tag": {
                "attributes-charset": DEFAULT_CHARSET,
                "attributes-natural-language": DEFAULT_CHARSET_LANGUAGE,
                "printer-uri": "ipp://printer.example.com:361/ipp/print",
                "requesting-user-name": "PythonIPP",
            },
        },
    )

    assert result == load_fixture_binary(
        "serializer/get-printer-attributes-request-000.bin",
    )
