"""Tests for Parser."""
from pyipp import parser
from pyipp.const import DEFAULT_CHARSET, DEFAULT_CHARSET_LANGUAGE, DEFAULT_PROTO_VERSION
from pyipp.enums import IppOperation, IppPrinterState
import datetime

from . import load_fixture_binary

RESPONSE_GET_PRINTER_ATTRIBUTES = load_fixture_binary(
    "get-printer-attributes-response-000.bin"
)

MOCK_IEEE1284_DEVICE_ID = "MFG:EPSON;CMD:ESCPL2,BDC,D4,D4PX,ESCPR7,END4,GENEP,URF;MDL:XP-6000 Series;CLS:PRINTER;DES:EPSON XP-6000 Series;CID:EpsonRGB;FID:FXN,DPA,WFA,ETN,AFN,DAN,WRA;RID:20;DDS:022500;ELG:1000;SN:583434593035343012;URF:CP1,PQ4-5,OB9,OFU0,RS360,SRGB24,W8,DM3,IS1-7-6,V1.4,MT1-3-7-8-10-11-12;"  # noqa


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
        "unsupported-attributes": [],
        "printers": [],
        "request-id": 1,
        "status-code": IppOperation.GET_PRINTER_ATTRIBUTES.value,
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


def test_parse_attribute_date() -> None:
    """Test DATE attribute parser"""
    blob = load_fixture_binary('get-jobs-kyocera-ecosys-m2540dn-000.bin')
    date = parser.parse_attribute(blob, 1022)
    assert date == (
        {
            'tag': 49,
            'name-length': 21,
            'name': 'date-time-at-creation',
            'value-length': 11,
            'value': datetime.datetime(2021, 9, 28, 9, 37, 15,
                                       tzinfo=datetime.timezone.utc)},
        1059,
    )


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


def test_parse_brother_mfcj5320dw() -> None:
    """Test the parse method against response from Brother MFC-J5320DW."""
    response = load_fixture_binary("get-printer-attributes-brother-mfcj5320dw.bin")

    result = parser.parse(response)
    assert result

    assert result["version"] == DEFAULT_PROTO_VERSION
    assert result["printers"]

    assert result["printers"][0]

    printer = result["printers"][0]
    assert printer["printer-make-and-model"] == "Brother MFC-J5320DW"
    assert printer["printer-uuid"] == "urn:uuid:e3248000-80ce-11db-8000-30055ce13be2"


def test_parse_kyocera_ecosys_m2540() -> None:
    """Test the parse method against response from KYOCERA ECOSYS M2540dn.
       Responce with some incomplete/substituted/unsupported attributes
    """
    response = load_fixture_binary("get-printer-attributes-kyocera-ecosys-m2540dn-001.bin")

    result = parser.parse(response)
    assert result

    assert result == {
        "version": (2, 0),
        "status-code": 1,
        "request-id": 47131,
        "operation-attributes": {
            "attributes-charset": "utf-8",
            "attributes-natural-language": "en-us"},
        "jobs": [],
        "printers": [
            {
                "printer-name": "mfu00-0365",
                "printer-location": "8409",
                "printer-info": "mfu00-0365",
                "printer-make-and-model": "ECOSYS M2540dn",
                "printer-state": IppPrinterState.IDLE,
                "printer-state-message": "Sleeping...  ",
                "printer-uri-supported": [
                    "ipps://10.104.12.95:443/ipp/print",
                    "ipp://10.104.12.95:631/ipp/print"]}],
        "unsupported-attributes": [
            {
                "requested-attributes": [
                    "printer-type",
                    "printer-state-reason",
                    "device-uri",
                    "printer-is-shared"]}],
        "data": b""}
    
