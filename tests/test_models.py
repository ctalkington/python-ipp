"""Tests for IPP Models."""
# pylint: disable=R0912,R0915
from __future__ import annotations

from typing import Any, List

import pytest

from pyipp import models, parser

from . import IPPE10_PRINTER_ATTRS, load_fixture_binary


@pytest.mark.asyncio
async def test_info() -> None:  # noqa: PLR0915
    """Test Info model."""
    parsed = parser.parse(load_fixture_binary("get-printer-attributes-epsonxp6000.bin"))
    data = parsed["printers"][0]
    info = models.Info.from_dict(data)

    assert info
    assert info.command_set == "ESCPL2,BDC,D4,D4PX,ESCPR7,END4,GENEP,URF"
    assert info.location == ""
    assert info.name == "EPSON XP-6000 Series"
    assert info.manufacturer == "EPSON"
    assert info.model == "XP-6000 Series"
    assert info.printer_name == "ipp/print"
    assert info.printer_info == "EPSON XP-6000 Series"
    assert info.printer_uri_supported == [
        "ipps://192.168.1.92:631/ipp/print",
        "ipp://192.168.1.92:631/ipp/print",
    ]
    assert info.more_info == "http://192.168.1.92:80/PRESENTATION/BONJOUR"
    assert info.serial == "583434593035343012"
    assert info.uuid == "cfe92100-67c4-11d4-a45f-f8d027761251"
    assert info.version == "20.44.NU25M7"
    assert info.uptime == 783801

    # no make/model, device id
    data["printer-make-and-model"] = ""
    info = models.Info.from_dict(data)

    assert info
    assert info.name == "EPSON XP-6000 Series"
    assert info.printer_name == "ipp/print"
    assert info.manufacturer == "EPSON"
    assert info.model == "XP-6000 Series"

    # no make/model, no device id, URI name
    data["printer-device-id"] = ""
    data["printer-make-and-model"] = ""
    data["printer-name"] = "ipp/print"
    info = models.Info.from_dict(data)

    assert info
    assert info.name == "IPP Printer"
    assert info.printer_name == "ipp/print"
    assert info.manufacturer == "Unknown"
    assert info.model == "Unknown"

    # no make/model, no device id, name
    data["printer-device-id"] = ""
    data["printer-make-and-model"] = ""
    data["printer-name"] = "Printy"
    info = models.Info.from_dict(data)

    assert info
    assert info.name == "Printy"
    assert info.printer_name == "Printy"
    assert info.manufacturer == "Unknown"
    assert info.model == "Unknown"

    # no make/model, no device id, no name
    data["printer-device-id"] = ""
    data["printer-make-and-model"] = ""
    data["printer-name"] = ""
    info = models.Info.from_dict(data)

    assert info
    assert info.name == "IPP Printer"
    assert info.printer_name == ""
    assert info.manufacturer == "Unknown"
    assert info.model == "Unknown"


@pytest.mark.asyncio
async def test_state() -> None:
    """Test State model."""
    data: dict[str, Any] = {
        "printer-state": 4,
        "printer-state-reasons": "none",
    }

    state = models.State.from_dict(data)

    assert state
    assert state.printer_state == "printing"
    assert state.reasons is None
    assert state.message is None


@pytest.mark.asyncio
async def test_printer() -> None:  # noqa: PLR0915
    """Test Printer model."""
    parsed = parser.parse(load_fixture_binary("get-printer-attributes-epsonxp6000.bin"))
    printer = models.Printer.from_dict(parsed["printers"][0])

    assert printer

    assert printer.info
    assert printer.info.command_set == "ESCPL2,BDC,D4,D4PX,ESCPR7,END4,GENEP,URF"
    assert printer.info.location == ""
    assert printer.info.name == "EPSON XP-6000 Series"
    assert printer.info.manufacturer == "EPSON"
    assert printer.info.model == "XP-6000 Series"
    assert printer.info.printer_name == "ipp/print"
    assert printer.info.printer_info == "EPSON XP-6000 Series"
    assert printer.info.printer_uri_supported == [
        "ipps://192.168.1.92:631/ipp/print",
        "ipp://192.168.1.92:631/ipp/print",
    ]
    assert printer.info.more_info == "http://192.168.1.92:80/PRESENTATION/BONJOUR"
    assert printer.info.serial == "583434593035343012"
    assert printer.info.uuid == "cfe92100-67c4-11d4-a45f-f8d027761251"
    assert printer.info.version == "20.44.NU25M7"
    assert printer.info.uptime == 783801

    assert printer.state
    assert printer.state.printer_state == "idle"
    assert printer.state.reasons == "marker-supply-low-warning"
    assert printer.state.message is None

    assert printer.markers
    assert isinstance(printer.markers, list)
    assert len(printer.markers) == 5

    assert printer.markers[0]
    assert printer.markers[0].marker_id == 4
    assert printer.markers[0].marker_type == "ink-cartridge"
    assert printer.markers[0].name == "Black ink"
    assert printer.markers[0].color == "#000000"
    assert printer.markers[0].level == 64
    assert printer.markers[0].low_level == 15
    assert printer.markers[0].high_level == 100

    assert printer.markers[1]
    assert printer.markers[1].marker_id == 1
    assert printer.markers[1].marker_type == "ink-cartridge"
    assert printer.markers[1].name == "Cyan ink"
    assert printer.markers[1].color == "#00FFFF"
    assert printer.markers[1].level == 99
    assert printer.markers[1].low_level == 15
    assert printer.markers[1].high_level == 100

    assert printer.markers[2]
    assert printer.markers[2].marker_id == 2
    assert printer.markers[2].marker_type == "ink-cartridge"
    assert printer.markers[2].name == "Magenta ink"
    assert printer.markers[2].color == "#FF00FF"
    assert printer.markers[2].level == 83
    assert printer.markers[2].low_level == 15
    assert printer.markers[2].high_level == 100

    assert printer.markers[3]
    assert printer.markers[3].marker_id == 0
    assert printer.markers[3].marker_type == "ink-cartridge"
    assert printer.markers[3].name == "Photo Black ink"
    assert printer.markers[3].color == "#000000"
    assert printer.markers[3].level == 27
    assert printer.markers[3].low_level == 15
    assert printer.markers[3].high_level == 100

    assert printer.markers[4]
    assert printer.markers[4].marker_id == 3
    assert printer.markers[4].marker_type == "ink-cartridge"
    assert printer.markers[4].name == "Yellow ink"
    assert printer.markers[4].color == "#FFFF00"
    assert printer.markers[4].level == 6
    assert printer.markers[4].low_level == 15
    assert printer.markers[4].high_level == 100

    assert printer.uris
    assert isinstance(printer.uris, list)
    assert len(printer.uris) == 2

    assert printer.uris[0]
    assert printer.uris[0].uri == "ipps://192.168.1.92:631/ipp/print"
    assert printer.uris[0].authentication is None
    assert printer.uris[0].security == "tls"

    assert printer.uris[1]
    assert printer.uris[1].uri == "ipp://192.168.1.92:631/ipp/print"
    assert printer.uris[1].authentication is None
    assert printer.uris[1].security is None

def test_printer_as_dict() -> None:
    """Test the dictionary version of Printer."""
    parsed = parser.parse(load_fixture_binary("get-printer-attributes-epsonxp6000.bin"))
    printer = models.Printer.from_dict(parsed["printers"][0])

    assert printer

    printer_dict = printer.as_dict()
    assert printer_dict
    assert isinstance(printer_dict, dict)
    assert isinstance(printer_dict["info"], dict)
    assert isinstance(printer_dict["state"], dict)
    assert isinstance(printer_dict["markers"], List)
    assert len(printer_dict["markers"]) == 5
    assert isinstance(printer_dict["uris"], List)
    assert len(printer_dict["uris"]) == 2

@pytest.mark.asyncio
async def test_printer_with_single_marker() -> None:
    """Test Printer model with single marker."""
    data = IPPE10_PRINTER_ATTRS.copy()
    data["marker-names"] = "Black"
    data["marker-types"] = "ink-cartridge"
    data["marker-colors"] = "#FF0000"
    data["marker-levels"] = 77
    data["marker-high-levels"] = 100
    data["marker-low-levels"] = 0

    printer = models.Printer.from_dict(data)
    assert printer
    assert printer.markers[0]
    assert printer.markers[0].name == "Black"
    assert printer.markers[0].color == "#FF0000"
    assert printer.markers[0].level == 77
    assert printer.markers[0].high_level == 100
    assert printer.markers[0].low_level == 0
    assert printer.markers[0].marker_type == "ink-cartridge"


@pytest.mark.asyncio
async def test_printer_with_single_marker_empty_strings() -> None:
    """Test Printer model with single marker with empty string values."""
    data = IPPE10_PRINTER_ATTRS.copy()
    data["marker-names"] = ""
    data["marker-types"] = ""
    data["marker-colors"] = ""
    data["marker-levels"] = ""
    data["marker-low-levels"] = ""
    data["marker-high-levels"] = ""

    printer = models.Printer.from_dict(data)
    assert printer
    assert len(printer.markers) == 0


@pytest.mark.asyncio
async def test_printer_with_single_marker_invalid() -> None:
    """Test Printer model with single invalid marker name."""
    data = IPPE10_PRINTER_ATTRS.copy()
    data["marker-names"] = -1

    printer = models.Printer.from_dict(data)
    assert printer
    assert len(printer.markers) == 0


@pytest.mark.asyncio
async def test_printer_with_extra_marker_data() -> None:
    """Test Printer model with extra marker data."""
    data = IPPE10_PRINTER_ATTRS.copy()
    data["marker-names"] = ["Black"]
    data["marker-types"] = ["ink-cartridge", "ink"]
    data["marker-colors"] = ["#FF0000", "#FF1111"]
    data["marker-levels"] = [99, 33]
    data["marker-low-levels"] = [0, 10]
    data["marker-high-levels"] = [99, 100]

    printer = models.Printer.from_dict(data)
    assert printer
    assert len(printer.markers) == 1
    assert printer.markers[0]
    assert printer.markers[0].name == "Black"
    assert printer.markers[0].color == "#FF0000"
    assert printer.markers[0].level == 99
    assert printer.markers[0].high_level == 99
    assert printer.markers[0].low_level == 0
    assert printer.markers[0].marker_type == "ink-cartridge"


@pytest.mark.asyncio
async def test_printer_with_single_supported_uri() -> None:
    """Test Printer model with single supported uri."""
    data = IPPE10_PRINTER_ATTRS.copy()
    data["printer-uri-supported"] = "ipp://10.104.12.95:631/ipp/print"
    data["uri-authentication-supported"] = "none"
    data["uri-security-supported"] = "none"

    printer = models.Printer.from_dict(data)
    assert printer
    assert printer.uris[0]
    assert printer.uris[0].uri == "ipp://10.104.12.95:631/ipp/print"
    assert printer.uris[0].authentication is None
    assert printer.uris[0].security is None


@pytest.mark.asyncio
async def test_printer_with_single_supported_uri_extra_data() -> None:
    """Test Printer model with single supported uri with extra data."""
    data = IPPE10_PRINTER_ATTRS.copy()
    data["printer-uri-supported"] = "ipp://10.104.12.95:631/ipp/print"
    data["uri-authentication-supported"] = ["none", "basic"]
    data["uri-security-supported"] = ["none", "tls"]

    printer = models.Printer.from_dict(data)
    assert printer
    assert printer.uris[0]
    assert printer.uris[0].uri == "ipp://10.104.12.95:631/ipp/print"
    assert printer.uris[0].authentication is None
    assert printer.uris[0].security is None


@pytest.mark.asyncio
async def test_printer_with_single_supported_uri_invalid_uri() -> None:
    """Test Printer model with single invalid supported uri."""
    data = IPPE10_PRINTER_ATTRS.copy()
    data["printer-uri-supported"] = -1
    data["uri-authentication-supported"] = "none"
    data["uri-security-supported"] = "none"

    printer = models.Printer.from_dict(data)
    assert printer
    assert len(printer.uris) == 0


@pytest.mark.asyncio
async def test_printer_with_single_supported_uri_with_security() -> None:
    """Test Printer model with multiple markers."""
    data = IPPE10_PRINTER_ATTRS.copy()
    data["printer-uri-supported"] = "ipps://10.104.12.95:631/ipp/print"
    data["uri-authentication-supported"] = "basic"
    data["uri-security-supported"] = "tls"

    printer = models.Printer.from_dict(data)
    assert printer
    assert printer.uris[0]
    assert printer.uris[0].uri == "ipps://10.104.12.95:631/ipp/print"
    assert printer.uris[0].authentication == "basic"
    assert printer.uris[0].security == "tls"
