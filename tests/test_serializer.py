"""Tests for Serializer."""
from ipp import serializer
from ipp.const import DEFAULT_CHARSET, DEFAULT_CHARSET_LANGUAGE, DEFAULT_PROTO_VERSION
from ipp.enums import IppOperation, IppTag

REQUEST_GET_PRINTER_ATTRIBUTES = b"\x02\x00\x00\x0b\x00\x00\x00\x01\x01G\x00\x12attributes-charset\x00\x05utf-8H\x00\x1battributes-natural-language\x00\x05en-USE\x00\x0bprinter-uri\x00'ipp://printer.example.com:361/ipp/printB\x00\x14requesting-user-name\x00\tPythonIPP\x03"


def test_construct_attibute_values() -> None:
    """Test the __construct_attibute_values method."""
    result = serializer.__construct_attibute_values(
        IppTag.INTEGER, IppOperation.GET_PRINTER_ATTRIBUTES
    )
    assert result == b"\x00\x04\x00\x00\x00\x0b"

    result = serializer.__construct_attibute_values(
        IppTag.ENUM, IppOperation.GET_PRINTER_ATTRIBUTES
    )
    assert result == b"\x00\x04\x00\x00\x00\x0b"


def test_construct_attribute() -> None:
    """Test the construct_attribute method."""
    result = serializer.construct_attribute("attributes-charset", DEFAULT_CHARSET)
    assert result == b"G\x00\x12attributes-charset\x00\x05utf-8"

    result = serializer.construct_attribute(
        "operations-supported", [IppOperation.GET_PRINTER_ATTRIBUTES],
    )
    assert result == b"#\x00\x14operations-supported\x00\x04\x00\x00\x00\x0b"


def test_encode_dict() -> None:
    """Test the encode_dict method."""
    result = serializer.encode_dict(
        {
            "version": DEFAULT_PROTO_VERSION,
            "operation": IppOperation.GET_PRINTER_ATTRIBUTES,
            "id": 1,
            "operation-attributes-tag": {
                "attributes-charset": DEFAULT_CHARSET,
                "attributes-natural-language": DEFAULT_CHARSET_LANGUAGE,
                "printer-uri": "ipp://printer.example.com:361/ipp/print",
                "requesting-user-name": "PythonIPP",
            },
        }
    )

    assert result == REQUEST_GET_PRINTER_ATTRIBUTES
