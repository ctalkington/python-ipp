"""Tests for Serializer."""
from pyipp import serializer
from pyipp.const import DEFAULT_CHARSET, DEFAULT_CHARSET_LANGUAGE, DEFAULT_PROTO_VERSION
from pyipp.enums import IppJobState, IppOperation, IppTag

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


def test_encode_dict_job_attributes_tag() -> None:
    """Test the encode_dict method for job-attributes-tag."""
    result = serializer.encode_dict(
        {
            "version": DEFAULT_PROTO_VERSION,
            "operation": IppOperation.CREATE_JOB,
            "request-id": 1,
            "job-attributes-tag": {
                "printer-uri": "ipp://localhost:631/printers/hp",
                "job-originating-user-name": "PythonIPP",
                "job-name": "test",
                "copies": 1,
                "finishings": [],
                "job-cancel-after": 10800,
                "job-hold-until": "no-hold",
                "job-priority": 50,
                "job-sheets": [],
                "number-up": 1,
                "job-uuid": "urn:uuid:68307de6-fbea-11ed-be56-0242ac120002",
                "job-originating-host-name": "localhost",
                "time-at-creation": 0,
                "time-at-processing": 0,
                "time-at-completed": 0,
                "job-id": 99,
                "job-state": IppJobState.PROCESSING,
                "job-state-reasons": "processing-to-stop-point",
                "job-media-sheets-completed": 0,
                "job-printer-uri": "ipp://localhost:631/printers/hp",
                "job-k-octets": 1,
                "document-format": "text/plain",
                "job-printer-state-message": "Printing page 1, 10% complete.",
                "job-printer-state-reasons": "none",
            },
        },
    )

    assert result == load_fixture_binary(
        "serializer/create-job-attributes-request-000.bin",
    )


def test_encode_dict_printer_attributes_tag() -> None:
    """Test the encode_dict method for printer-attributes-tag."""
    result = serializer.encode_dict(
        {
            "version": DEFAULT_PROTO_VERSION,
            "operation": IppOperation.SET_PRINTER_ATTRIBUTES,
            "request-id": 1,
            "printer-attributes-tag": {
                "printer-geo-location": "geo:38.622780,-90.193329",
                "printer-info": "extended info",
                "printer-location": "Office",
                "printer-organization": "PythonIPP",
                "printer-organizational-unit": "IT",
            },
        },
    )

    assert result == load_fixture_binary(
        "serializer/set-printer-attributes-request-000.bin",
    )
