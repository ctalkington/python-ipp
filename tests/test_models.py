"""Tests for IPP Models."""
import pyipp.models as models
import pyipp.parser as parser
import pytest

from . import IPPE10_PRINTER_ATTRS, load_fixture_binary


@pytest.mark.asyncio
async def test_info():
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
        "ipps://epson761251.local.:631/ipp/print",
        "ipp://epson761251.local.:631/ipp/print",
    ]
    assert info.serial == "583434593035343012"
    assert info.uuid == "cfe92100-67c4-11d4-a45f-f8d027761251"
    assert info.version == "20.44.NU20K2"
    assert info.uptime == 4119

    # custom printer name
    data["printer-name"] = "Printy"
    info = models.Info.from_dict(data)

    assert info
    assert info.name == "Printy"
    assert info.printer_name == "Printy"

    # no custom name, no make/model
    data["printer-name"] = "ipp/print"
    data["printer-make-and-model"] = ""
    info = models.Info.from_dict(data)

    assert info
    assert info.name == "IPP Printer"
    assert info.printer_name == "ipp/print"
    assert info.manufacturer == "EPSON"
    assert info.model == "XP-6000 Series"

    # no custom name, no make/model, no device id
    data["printer-name"] = ""
    data["printer-make-and-model"] = ""
    data["printer-device-id"] = ""
    info = models.Info.from_dict(data)

    assert info
    assert info.name == "IPP Printer"
    assert info.printer_name == ""
    assert info.manufacturer == "Unknown"
    assert info.model == "Unknown"


@pytest.mark.asyncio
async def test_printer():
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
        "ipps://epson761251.local.:631/ipp/print",
        "ipp://epson761251.local.:631/ipp/print",
    ]
    assert printer.info.serial == "583434593035343012"
    assert printer.info.uuid == "cfe92100-67c4-11d4-a45f-f8d027761251"
    assert printer.info.version == "20.44.NU20K2"
    assert printer.info.uptime == 4119

    assert printer.state
    assert printer.state.printer_state == "idle"
    assert printer.state.reasons is None
    assert printer.state.message is None

    assert printer.markers
    assert printer.markers[0]
    assert printer.markers[0].marker_id == 4
    assert printer.markers[0].marker_type == "ink-cartridge"
    assert printer.markers[0].name == "Black ink"
    assert printer.markers[0].color == "#000000"
    assert printer.markers[0].level == 54
    assert printer.markers[0].low_level == 15
    assert printer.markers[0].high_level == 100

    assert printer.markers[1]
    assert printer.markers[1].marker_id == 1
    assert printer.markers[1].marker_type == "ink-cartridge"
    assert printer.markers[1].name == "Cyan ink"
    assert printer.markers[1].color == "#00FFFF"
    assert printer.markers[1].level == 88
    assert printer.markers[1].low_level == 15
    assert printer.markers[1].high_level == 100

    assert printer.markers[2]
    assert printer.markers[2].marker_id == 2
    assert printer.markers[2].marker_type == "ink-cartridge"
    assert printer.markers[2].name == "Magenta ink"
    assert printer.markers[2].color == "#FF00FF"
    assert printer.markers[2].level == 70
    assert printer.markers[2].low_level == 15
    assert printer.markers[2].high_level == 100

    assert printer.markers[3]
    assert printer.markers[3].marker_id == 0
    assert printer.markers[3].marker_type == "ink-cartridge"
    assert printer.markers[3].name == "Photo Black ink"
    assert printer.markers[3].color == "#000000"
    assert printer.markers[3].level == 96
    assert printer.markers[3].low_level == 15
    assert printer.markers[3].high_level == 100

    assert printer.markers[4]
    assert printer.markers[4].marker_id == 3
    assert printer.markers[4].marker_type == "ink-cartridge"
    assert printer.markers[4].name == "Yellow ink"
    assert printer.markers[4].color == "#FFFF00"
    assert printer.markers[4].level == 92
    assert printer.markers[4].low_level == 15
    assert printer.markers[4].high_level == 100


@pytest.mark.asyncio
async def test_printer_with_marker_data():
    """Test Printer model."""
    data = IPPE10_PRINTER_ATTRS.copy()
    data["marker-names"] = []
    data["marker-types"] = []
    data["marker-colors"] = []
    data["marker-levels"] = []
    data["marker-high-levels"] = []
    data["marker-low-levels"] = []

    # empty but valid types
    printer = models.Printer.from_dict(data)
    assert printer
    assert len(printer.markers) == 0

    # no names
    data["marker-names"] = -1

    printer = models.Printer.from_dict(data)
    assert printer
    assert len(printer.markers) == 0

    # partial valid data
    data["marker-names"] = ["Black"]
    data["marker-colors"] = -2

    printer = models.Printer.from_dict(data)
    assert printer
    assert len(printer.markers) == 1
    assert printer.markers[0]
    assert printer.markers[0].name == "Black"
    assert printer.markers[0].color == ""
    assert printer.markers[0].level == -2
    assert printer.markers[0].high_level == 100
    assert printer.markers[0].low_level == 0
    assert printer.markers[0].marker_type == "unknown"

    # partial valid data, extra data
    data["marker-names"] = ["Black"]
    data["marker-colors"] = -2
    data["marker-levels"] = [99, 98]

    printer = models.Printer.from_dict(data)
    assert printer
    assert len(printer.markers) == 1
    assert printer.markers[0]
    assert printer.markers[0].name == "Black"
    assert printer.markers[0].color == ""
    assert printer.markers[0].level == 99
    assert printer.markers[0].high_level == 100
    assert printer.markers[0].low_level == 0
    assert printer.markers[0].marker_type == "unknown"

    # full valid
    data["marker-names"] = ["Black"]
    data["marker-types"] = ["ink-cartridge"]
    data["marker-colors"] = ["#FF0000"]
    data["marker-levels"] = [77]
    data["marker-high-levels"] = [100]
    data["marker-low-levels"] = [0]

    printer = models.Printer.from_dict(data)
    assert printer
    assert printer.markers[0]
    assert printer.markers[0].name == "Black"
    assert printer.markers[0].color == "#FF0000"
    assert printer.markers[0].level == 77
    assert printer.markers[0].high_level == 100
    assert printer.markers[0].low_level == 0
    assert printer.markers[0].marker_type == "ink-cartridge"
