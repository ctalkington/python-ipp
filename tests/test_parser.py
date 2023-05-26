"""Tests for Parser."""
from datetime import datetime, timezone

import pytest

from pyipp import IPPParseError, parser
from pyipp.const import DEFAULT_CHARSET, DEFAULT_CHARSET_LANGUAGE, DEFAULT_PROTO_VERSION
from pyipp.enums import (
    IppFinishing,
    IppJobState,
    IppOperation,
    IppOrientationRequested,
    IppPrinterState,
    IppPrintQuality,
    IppStatus,
)

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


def test_parse_brother_mfcj5320dw() -> None:
    """Test the parse method against response from Brother MFC-J5320DW."""
    response = load_fixture_binary("get-printer-attributes-brother-mfcj5320dw.bin")

    result = parser.parse(response)
    assert result
    assert result["version"] == (2, 0)
    assert result["status-code"] == IppStatus.OK

    assert result["printers"]
    assert result["printers"][0]

    printer = result["printers"][0]
    assert printer["printer-make-and-model"] == "Brother MFC-J5320DW"
    assert printer["printer-uuid"] == "urn:uuid:e3248000-80ce-11db-8000-30055ce13be2"


def test_parse_epson_xp6000() -> None:
    """Test the parse method against response from Epson XP-6000 Series."""
    response = load_fixture_binary("get-printer-attributes-epsonxp6000.bin")

    result = parser.parse(response)
    assert result
    assert result["version"] == (2, 0)
    assert result["status-code"] == IppStatus.OK
    assert result["request-id"] == 66306

    assert result["operation-attributes"] == {
        "attributes-charset": "utf-8",
        "attributes-natural-language": "en",
    }

    assert result["jobs"] == []

    assert result["printers"]
    assert result["printers"][0] == {
        "charset-configured": "utf-8",
        "charset-supported": "utf-8",
        "color-supported": True,
        "compression-supported": ["none", "gzip"],
        "copies-default": 1,
        "copies-supported": [1, 99],
        "document-format-default": "application/octet-stream",
        "document-format-preferred": "image/urf",
        "document-format-supported": [
            "application/octet-stream",
            "image/pwg-raster",
            "image/urf",
            "image/jpeg",
        ],
        "document-format-varying-attributes": ["copies", "sides"],
        "finishings-default": 3,
        "finishings-supported": 3,
        "generated-natural-language-supported": "en",
        "identify-actions-default": "flash",
        "identify-actions-supported": "flash",
        "ipp-features-supported": ["wfds-print-1.0", "airprint-1.7"],
        "ipp-versions-supported": ["1.0", "1.1", "2.0"],
        "job-creation-attributes-supported": [
            "copies",
            "finishings",
            "ipp-attribute-fidelity",
            "job-name",
            "media",
            "media-col",
            "orientation-requested",
            "output-bin",
            "print-quality",
            "printer-resolution",
            "sides",
            "print-color-mode",
            "print-content-optimize",
            "print-scaling",
            "job-mandatory-attributes",
        ],
        "jpeg-features-supported": "none",
        "jpeg-k-octets-supported": [0, 16384],
        "jpeg-x-dimension-supported": [0, 15000],
        "jpeg-y-dimension-supported": [1, 15000],
        "landscape-orientation-requested-preferred": 5,
        "marker-colors": [
            "#000000",
            "#00FFFF",
            "#FF00FF",
            "#FFFF00",
            "#000000",
        ],
        "marker-high-levels": [100, 100, 100, 100, 100],
        "marker-levels": [27, 99, 83, 6, 64],
        "marker-low-levels": [15, 15, 15, 15, 15],
        "marker-names": [
            "Photo Black ink",
            "Cyan ink",
            "Magenta ink",
            "Yellow ink",
            "Black ink",
        ],
        "marker-types": [
            "ink-cartridge",
            "ink-cartridge",
            "ink-cartridge",
            "ink-cartridge",
            "ink-cartridge",
        ],
        "media-bottom-margin-supported": [0, 300],
        "media-col-default": [
            "",
            "media-size",
            "",
            "x-dimension",
            21590,
            "y-dimension",
            27940,
            "",
            "media-top-margin",
            300,
            "media-left-margin",
            300,
            "media-right-margin",
            300,
            "media-bottom-margin",
            300,
            "media-type",
            "stationery",
            "media-source",
            "main",
            "",
        ],
        "media-col-ready": [
            "",
            "media-size",
            "",
            "x-dimension",
            21590,
            "y-dimension",
            27940,
            "",
            "media-top-margin",
            300,
            "media-left-margin",
            300,
            "media-right-margin",
            300,
            "media-bottom-margin",
            300,
            "media-type",
            "stationery",
            "media-source",
            "main",
            "",
            "",
            "media-size",
            "",
            "x-dimension",
            10160,
            "y-dimension",
            15240,
            "",
            "media-top-margin",
            300,
            "media-left-margin",
            300,
            "media-right-margin",
            300,
            "media-bottom-margin",
            300,
            "media-type",
            "photographic",
            "media-source",
            "photo",
            "",
            "",
            "media-size",
            "",
            "x-dimension",
            10160,
            "y-dimension",
            15240,
            "",
            "media-top-margin",
            0,
            "media-left-margin",
            0,
            "media-right-margin",
            0,
            "media-bottom-margin",
            0,
            "media-type",
            "photographic",
            "media-source",
            "photo",
            "",
            "",
            "media-size",
            "",
            "x-dimension",
            12000,
            "y-dimension",
            12000,
            "",
            "media-top-margin",
            0,
            "media-left-margin",
            0,
            "media-right-margin",
            0,
            "media-bottom-margin",
            0,
            "media-type",
            "disc",
            "media-source",
            "disc",
            "",
        ],
        "media-col-supported": [
            "media-size",
            "media-top-margin",
            "media-left-margin",
            "media-right-margin",
            "media-bottom-margin",
            "media-type",
            "media-source",
        ],
        "media-default": "na_letter_8.5x11in",
        "media-left-margin-supported": [0, 300],
        "media-ready": [
            "na_letter_8.5x11in",
            "na_index-4x6_4x6in",
            "disc_12cm_18x120mm",
        ],
        "media-right-margin-supported": [0, 300],
        "media-size-supported": [
            "",
            "x-dimension",
            21590,
            "y-dimension",
            27940,
            "",
            "",
            "x-dimension",
            10160,
            "y-dimension",
            15240,
            "",
            "",
            "x-dimension",
            12700,
            "y-dimension",
            17780,
            "",
            "",
            "x-dimension",
            20320,
            "y-dimension",
            25400,
            "",
            "",
            "x-dimension",
            10160,
            "y-dimension",
            18060,
            "",
            "",
            "x-dimension",
            21000,
            "y-dimension",
            29700,
            "",
            "",
            "x-dimension",
            10500,
            "y-dimension",
            14800,
            "",
            "",
            "x-dimension",
            21590,
            "y-dimension",
            35560,
            "",
            "",
            "x-dimension",
            8890,
            "y-dimension",
            12700,
            "",
            "",
            "x-dimension",
            13970,
            "y-dimension",
            21590,
            "",
            "",
            "x-dimension",
            10477,
            "y-dimension",
            24130,
            "",
            "",
            "x-dimension",
            21590,
            "y-dimension",
            33020,
            "",
            "",
            "x-dimension",
            12000,
            "y-dimension",
            12000,
            "",
            "",
            "x-dimension",
            [8900, 21590],
            "y-dimension",
            [12700, 111760],
            "",
        ],
        "media-source-supported": ["auto", "main", "photo", "disc"],
        "media-supported": [
            "na_letter_8.5x11in",
            "na_index-4x6_4x6in",
            "na_5x7_5x7in",
            "na_govt-letter_8x10in",
            "om_hivision_101.6x180.6mm",
            "iso_a4_210x297mm",
            "iso_a6_105x148mm",
            "na_legal_8.5x14in",
            "oe_photo-l_3.5x5in",
            "na_invoice_5.5x8.5in",
            "na_number-10_4.125x9.5in",
            "na_foolscap_8.5x13in",
            "disc_12cm_18x120mm",
            "custom_min_89x127mm",
            "custom_max_215.9x1117.6mm",
        ],
        "media-top-margin-supported": [0, 300],
        "media-type-supported": [
            "stationery",
            "photographic-high-gloss",
            "photographic",
            "photographic-semi-gloss",
            "photographic-glossy",
            "photographic-matte",
            "com.epson-luster",
            "envelope",
            "stationery-coated",
            "disc",
        ],
        "mopria-certified": "mopria-certified 1.3",
        "multiple-document-jobs-supported": False,
        "multiple-operation-time-out": 120,
        "multiple-operation-time-out-action": "abort-job",
        "natural-language-configured": "en",
        "operations-supported": [2, 4, 5, 6, 8, 9, 10, 11, 59, 60],
        "orientation-requested-default": 3,
        "orientation-requested-supported": 3,
        "output-bin-default": "face-up",
        "output-bin-supported": "face-up",
        "pages-per-minute": 9,
        "pages-per-minute-color": 9,
        "pdf-versions-supported": "none",
        "pdl-override-supported": "attempted",
        "print-color-mode-default": "auto",
        "print-color-mode-supported": [
            "color",
            "monochrome",
            "auto-monochrome",
            "process-monochrome",
            "auto",
        ],
        "print-content-optimize-default": "auto",
        "print-content-optimize-supported": "auto",
        "print-quality-default": 4,
        "print-quality-supported": [4, 5],
        "print-scaling-default": "auto",
        "print-scaling-supported": ["auto", "auto-fit", "fill", "fit", "none"],
        "printer-alert": "code=other",
        "printer-alert-description": "feed roller needed soon",
        "printer-config-change-date-time": "",
        "printer-config-change-time": 25,
        "printer-current-time": datetime(2022, 10, 4, 2, 21, 58, tzinfo=timezone.utc),
        "printer-device-id": "MFG:EPSON;CMD:ESCPL2,BDC,D4,D4PX,ESCPR7,END4,GENEP,URF;MDL:XP-6000 Series;CLS:PRINTER;DES:EPSON XP-6000 Series;CID:EpsonRGB;FID:FXN,DPA,WFA,ETN,AFN,DAN,WRA;RID:20;DDS:022500;ELG:1000;SN:583434593035343012;URF:CP1,PQ4-5,OB9,OFU0,RS360,SRGB24,W8,DM3,IS1-7-6,V1.4,MT1-3-7-8-10-11-12;",
        "printer-dns-sd-name": "EPSON XP-6000 Series",
        "printer-firmware-name": "Firmware",
        "printer-firmware-string-version": "20.44.NU25M7",
        "printer-firmware-version": "000020440000M7250000000000000000",
        "printer-geo-location": "",
        "printer-get-attributes-supported": "document-format",
        "printer-icons": [
            "https://192.168.1.92:443/PRESENTATION/AIRPRINT/PRINTER_128.PNG",
            "https://192.168.1.92:443/PRESENTATION/AIRPRINT/PRINTER_512.PNG",
        ],
        "printer-info": "EPSON XP-6000 Series",
        "printer-input-tray": [
            "type=other;dimunit=micrometers;mediafeed=279400;mediaxfeed=215900;maxcapacity=-2;level=-2;status=0;name=Sheet feeder bin 1;",
            "type=sheetFeedAutoNonRemovableTray;dimunit=micrometers;mediafeed=279400;mediaxfeed=215900;maxcapacity=-2;level=-2;status=0;name=Sheet feeder bin 1;",
            "type=sheetFeedAutoNonRemovableTray;dimunit=micrometers;mediafeed=152400;mediaxfeed=101600;maxcapacity=-2;level=-2;status=0;name=Sheet feeder bin 2;",
            "type=other;dimunit=micrometers;mediafeed=120000;mediaxfeed=120000;maxcapacity=-2;level=-2;status=5;name=Disc;",
        ],
        "printer-is-accepting-jobs": True,
        "printer-kind": ["document", "envelope", "photo", "disc"],
        "printer-location": "",
        "printer-make-and-model": "EPSON XP-6000 Series",
        "printer-more-info": "http://192.168.1.92:80/PRESENTATION/BONJOUR",
        "printer-name": "ipp/print",
        "printer-organization": "",
        "printer-organizational-unit": "",
        "printer-output-tray": "type=unRemovableBin;maxcapacity=50;remaining=-3;status=0;name=Face-up Tray;stackingorder=lastToFirst;pagedelivery=faceUp;",
        "printer-resolution-default": (360, 360, 3),
        "printer-resolution-supported": [
            (360, 360, 3),
            (720, 720, 3),
            (5760, 1440, 3),
        ],
        "printer-state": IppPrinterState.IDLE,
        "printer-state-change-date-time": datetime(
            2022,
            9,
            27,
            3,
            47,
            19,
            tzinfo=timezone.utc,
        ),
        "printer-state-change-time": 184119,
        "printer-state-reasons": "marker-supply-low-warning",
        "printer-strings-languages-supported": ["en", "es-mx", "pt", "fr"],
        "printer-strings-uri": "http://192.168.1.92:80/LANGUAGES/IPP?LANG=en",
        "printer-supply-info-uri": "http://192.168.1.92:80/PRESENTATION/HTML/TOP/PRTINFO.HTML",
        "printer-up-time": 783801,
        "printer-uri-supported": [
            "ipps://192.168.1.92:631/ipp/print",
            "ipp://192.168.1.92:631/ipp/print",
        ],
        "printer-uuid": "urn:uuid:cfe92100-67c4-11d4-a45f-f8d027761251",
        "pwg-raster-document-resolution-supported": (360, 360, 3),
        "pwg-raster-document-sheet-back": "rotated",
        "pwg-raster-document-type-supported": ["sgray_8", "srgb_8"],
        "queued-job-count": 0,
        "sides-default": "one-sided",
        "sides-supported": [
            "one-sided",
            "two-sided-short-edge",
            "two-sided-long-edge",
        ],
        "urf-supported": [
            "CP1",
            "PQ4-5",
            "OB9",
            "OFU0",
            "RS360",
            "SRGB24",
            "W8",
            "DM3",
            "IS1-7-6",
            "V1.4",
            "MT1-3-7-8-10-11-12",
        ],
        "uri-authentication-supported": ["none", "none"],
        "uri-security-supported": ["tls", "none"],
        "which-jobs-supported": ["completed", "not-completed"],
    }

    assert result["unsupported-attributes"] == []

    assert result["data"] == b""


def test_parse_kyocera_ecosys_m2540dn() -> None:
    """Test the parse method against response from Kyocera Ecosys M2540DN."""
    response = load_fixture_binary(
        "get-printer-attributes-kyocera-ecosys-m2540dn-001.bin",
    )

    result = parser.parse(response)
    assert result

    assert result["version"] == (2, 0)
    assert result["status-code"] == IppStatus.OK_IGNORED_OR_SUBSTITUTED
    assert result["request-id"] == 47131

    assert result["operation-attributes"] == {
        "attributes-charset": "utf-8",
        "attributes-natural-language": "en-us",
    }

    assert result["jobs"] == []

    assert result["printers"]
    assert result["printers"][0] == {
        "printer-name": "mfu00-0365",
        "printer-location": "8409",
        "printer-info": "mfu00-0365",
        "printer-make-and-model": "ECOSYS M2540dn",
        "printer-state": IppPrinterState.IDLE,
        "printer-state-message": "Sleeping...  ",
        "printer-uri-supported": [
            "ipps://10.104.12.95:443/ipp/print",
            "ipp://10.104.12.95:631/ipp/print",
        ],
    }

    assert result["unsupported-attributes"] == [
        {
            "requested-attributes": [
                "printer-type",
                "printer-state-reason",
                "device-uri",
                "printer-is-shared",
            ],
        },
    ]

    assert result["data"] == b""


def test_parse_kyocera_ecosys_m2540dn_get_jobs() -> None:
    """Test the parse method against get-jobs response from Kyocera Ecosys M2540DN."""
    response = load_fixture_binary("get-jobs-kyocera-ecosys-m2540dn-000.bin")
    result = parser.parse(response)

    assert result
    assert result["version"] == (2, 0)
    assert result["status-code"] == IppStatus.OK
    assert result["request-id"] == 92255

    assert result["operation-attributes"] == {
        "attributes-charset": "utf-8",
        "attributes-natural-language": "en-us",
    }

    assert result["jobs"]
    assert result["jobs"][0] == {
        "compression-supplied": "none",
        "copies": 1,
        "date-time-at-completed": datetime(2021, 9, 28, 9, 37, 35, tzinfo=timezone.utc),
        "date-time-at-creation": datetime(2021, 9, 28, 9, 37, 15, tzinfo=timezone.utc),
        "date-time-at-processing": datetime(
            2021,
            9,
            28,
            9,
            37,
            16,
            tzinfo=timezone.utc,
        ),
        "document-format-supplied": "image/urf",
        "document-format-version-supplied": "1.4",
        "document-name-supplied": "doc",
        "feed-orientation": "short-edge-first",
        "finishings": IppFinishing.NONE,
        "job-id": 1000,
        "job-impressions": "",
        "job-impressions-completed": 3,
        "job-name": "Microsoft Word - ТСД",  # noqa: RUF001
        "job-originating-user-name": "CORP\\OFFICE20708$",
        "job-printer-up-time": 179727,
        "job-printer-uri": "ipps://10.104.12.95:443/ipp/print",
        "job-priority": 50,
        "job-state": IppJobState.COMPLETED,
        "job-state-message": "completed : job-completed-successfully",
        "job-state-reasons": "job-completed-successfully",
        "job-uri": "ipps://mfu00-0365:443/jobs/1000",
        "job-uuid": "urn:uuid:4509a320-00a2-0079-00c9-00557cc48011",
        "multiple-document-handling": "separate-documents-collated-copies",
        "orientation-requested": IppOrientationRequested.PORTRAIT,
        "output-bin": "top",
        "print-color-mode": "monochrome",
        "print-content-optimize": "auto",
        "print-quality": IppPrintQuality.NORMAL,
        "print-scaling": "auto",
        "printer-resolution": (600, 600, 3),
        "sides": "one-sided",
        "time-at-completed": 1632821855,
        "time-at-creation": 1632821835,
        "time-at-processing": 1632821836,
    }

    assert result["unsupported-attributes"] == []

    assert result["data"] == b""
