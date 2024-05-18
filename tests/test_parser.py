"""Tests for Parser."""
import pytest
from syrupy.assertion import SnapshotAssertion

from pyipp import IPPParseError, parser
from pyipp.const import DEFAULT_CHARSET, DEFAULT_CHARSET_LANGUAGE, DEFAULT_PROTO_VERSION
from pyipp.enums import IppOperation

from . import load_fixture_binary

RESPONSE_GET_PRINTER_ATTRIBUTES = load_fixture_binary(
    "get-printer-attributes-response-000.bin",
)

MOCK_IEEE1284_DEVICE_ID = "MFG:EPSON;CMD:ESCPL2,BDC,D4,D4PX,ESCPR7,END4,GENEP,URF;MDL:XP-6000 Series;CLS:PRINTER;DES:EPSON XP-6000 Series;CID:EpsonRGB;FID:FXN,DPA,WFA,ETN,AFN,DAN,WRA;RID:20;DDS:022500;ELG:1000;SN:583434593035343012;URF:CP1,PQ4-5,OB9,OFU0,RS360,SRGB24,W8,DM3,IS1-7-6,V1.4,MT1-3-7-8-10-11-12;"


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
        "unsupported-attributes": [],
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


def test_parse_attribute_reserved_string() -> None:
    """Test the parse_attribute method when provided a reserved string."""
    result = parser.parse_attribute(b"C\x00\x0freserved-string\x00\x04yoda", 0)
    assert result == (
        {
            "name": "reserved-string",
            "name-length": 15,
            "tag": 67,
            "value": "yoda",
            "value-length": 4,
        },
        24,
    )

    result = parser.parse_attribute(b"C\x00\x0freserved-string\x00\x00", 0)
    assert result == (
        {
            "name": "reserved-string",
            "name-length": 15,
            "tag": 67,
            "value": None,
            "value-length": 0,
        },
        20,
    )


def test_parse_attribute_invalid_date() -> None:
    """Test the parse_attribute method when provided an invalid date."""
    invalid = b"1\x00\x14printer-current-time\x00\x0299"

    with pytest.raises(IPPParseError):
        parser.parse_attribute(invalid, 0)


def test_parse_ieee1284_device_id() -> None:
    """Test the parse_ieee1284_device_id method."""
    result = parser.parse_ieee1284_device_id(MOCK_IEEE1284_DEVICE_ID)

    assert result
    assert result["MFG"] == "EPSON"
    assert result["MDL"] == "XP-6000 Series"
    assert result["SN"] == "583434593035343012"
    assert result["CMD"] == "ESCPL2,BDC,D4,D4PX,ESCPR7,END4,GENEP,URF"

    assert result["MANUFACTURER"] == result["MFG"]
    assert result["MODEL"] == result["MDL"]
    assert result["COMMAND SET"] == result["CMD"]


def test_parse_ieee1284_device_id_manufacturer_only() -> None:
    """Test the parse_ieee1284_device_id method with only a manufacturer."""
    result = parser.parse_ieee1284_device_id("MANUFACTURER:EPSON")

    assert result == {
        "MANUFACTURER": "EPSON",
    }


def test_parse_ieee1284_device_id_empty() -> None:
    """Test the parse_ieee1284_device_id method with empty string."""
    result = parser.parse_ieee1284_device_id("")

    assert isinstance(result, dict)


def test_parse_make_and_model() -> None:
    """Test the parse_make_and_model method."""
    result = parser.parse_make_and_model("")
    assert result == ("Unknown", "Unknown")

    # generic fallback for unknown brands
    result = parser.parse_make_and_model("IPP")
    assert result == ("IPP", "Unknown")

    result = parser.parse_make_and_model("IPP Printer")
    assert result == ("IPP", "Printer")

    # known brands
    result = parser.parse_make_and_model("EPSON XP-6000 Series")
    assert result == ("EPSON", "XP-6000 Series")

    result = parser.parse_make_and_model("HP Officejet Pro 6830")
    assert result == ("HP", "Officejet Pro 6830")

    result = parser.parse_make_and_model("HP Photosmart D110 Series")
    assert result == ("HP", "Photosmart D110 Series")


def test_parse_brother_mfcj5320dw(snapshot: SnapshotAssertion) -> None:
    """Test the parse method against response from Brother MFC-J5320DW."""
    response = load_fixture_binary("get-printer-attributes-brother-mfcj5320dw.bin")

    result = parser.parse(response)
    assert result == snapshot


def test_parse_epson_xp6000(snapshot: SnapshotAssertion) -> None:
    """Test the parse method against response from Epson XP-6000 Series."""
    response = load_fixture_binary("get-printer-attributes-epsonxp6000.bin")

    result = parser.parse(response)
    assert result == snapshot


def test_parse_kyocera_ecosys_m2540dn(snapshot: SnapshotAssertion) -> None:
    """Test the parse method against response from Kyocera Ecosys M2540DN."""
    response = load_fixture_binary(
        "get-printer-attributes-kyocera-ecosys-m2540dn-001.bin",
    )

    result = parser.parse(response)
    assert result == snapshot
