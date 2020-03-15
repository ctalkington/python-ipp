"""Tests for Parser."""
from ipp import parser
from ipp.const import DEFAULT_CHARSET, DEFAULT_CHARSET_LANGUAGE, DEFAULT_PROTO_VERSION
from ipp.enums import IppOperation

from . import load_fixture_binary

RESPONSE_GET_PRINTER_ATTRIBUTES = load_fixture_binary(
    "get-printer-attributes-response-000.bin"
)


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
