"""Tests for Parser."""
from ipp import parser
from ipp.const import DEFAULT_CHARSET, DEFAULT_CHARSET_LANGUAGE, DEFAULT_PROTO_VERSION
from ipp.enums import IppOperation

RESPONSE_GET_PRINTER_ATTRIBUTES = b"\x02\x00\x00\x0b\x00\x00\x00\x01\x01G\x00\x12attributes-charset\x00\x05utf-8H\x00\x1battributes-natural-language\x00\x05en-USE\x00\x0bprinter-uri\x00'ipp://printer.example.com:361/ipp/printB\x00\x14requesting-user-name\x00\tPythonIPP\x03"


def test_parse() -> None:
    """Test the parse method."""
    result = parser.parse(RESPONSE_GET_PRINTER_ATTRIBUTES)
    assert result == {
        "data": b"",
        "jobs": [],
        "operation-attributes": {
            "attributes-charset": DEFAULT_CHARSET,
            "attributes-natural-language": DEFAULT_CHARSET_LANGUAGE,
            "printer-uri": "ipp://printer.example.com:361/ipp/print",
            "requesting-user-name": "PythonIPP",
        },
        "printers": [],
        "request-id": 1,
        "status-code": IppOperation.GET_PRINTER_ATTRIBUTES,
        "version": DEFAULT_PROTO_VERSION,
    }


def test_parse_attribute() -> None:
    """Test the parse_attribute method."""
    result = parser.parse_attribute(RESPONSE_GET_PRINTER_ATTRIBUTES, 9)
    assert result == (
        {
            "name": "attributes-charset",
            "name-length": 18,
            "tag": 71,
            "value": "utf-8",
            "value-length": 5,
        },
        37,
    )
