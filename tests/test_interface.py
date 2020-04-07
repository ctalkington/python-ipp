"""Tests for IPP Printer model."""
import pytest
from aiohttp import ClientSession
from pyipp import IPP, Printer

from . import (
    DEFAULT_PRINTER_HOST,
    DEFAULT_PRINTER_PATH,
    DEFAULT_PRINTER_PORT,
    DEFAULT_PRINTER_URI,
    load_fixture_binary,
)

MATCH_DEFAULT_HOST = f"{DEFAULT_PRINTER_HOST}:{DEFAULT_PRINTER_PORT}"


@pytest.mark.asyncio
async def test_printer(aresponses):
    """Test getting IPP printer information."""
    aresponses.add(
        MATCH_DEFAULT_HOST,
        DEFAULT_PRINTER_PATH,
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/ipp"},
            body=load_fixture_binary("get-printer-attributes-epsonxp6000.bin"),
        ),
    )

    async with ClientSession() as session:
        ipp = IPP(DEFAULT_PRINTER_URI, session=session)
        printer: Printer = await ipp.printer()

        assert printer

        assert printer.info
        assert printer.info.command_set == "ESCPL2,BDC,D4,D4PX,ESCPR7,END4,GENEP,URF"
        assert printer.info.location == ""
        assert printer.info.name == "EPSON XP-6000 Series"
        assert printer.info.manufacturer == "EPSON"
        assert printer.info.model == "XP-6000 Series"
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
async def test_raw(aresponses):
    """Test raw method is handled correctly."""
    aresponses.add(
        MATCH_DEFAULT_HOST,
        DEFAULT_PRINTER_PATH,
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/ipp"},
            body=load_fixture_binary("get-printer-attributes-epsonxp6000.bin"),
        ),
    )

    async with ClientSession() as session:
        ipp = IPP(DEFAULT_PRINTER_URI, session=session)
        response = await ipp.raw(
            IppOperation.GET_PRINTER_ATTRIBUTES,
            {
                "operation-attributes-tag": {
                    "requested-attributes": DEFAULT_PRINTER_ATTRIBUTES,
                },
            },
        )

        assert isinstance(response, bytes)
