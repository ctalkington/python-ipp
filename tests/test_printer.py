"""Tests for IPP Printer model."""
from aiohttp import ClientSession
import pytest

from ipp import IPP, Printer

from . import DEFAULT_PRINTER_URI, load_fixture_binary


@pytest.mark.asyncio
async def test_printer(aresponses):
    """Test getting IPP printer information."""
    aresponses.add(
        "printer.example.com:631",
        "/ipp/print",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/ipp"},
            body=load_fixture_binary("get-printer-attributes.bin"),
        ),
    )

    async with ClientSession() as session:
        ipp = IPP(DEFAULT_PRINTER_URI, session=session)
        printer: Printer = await ipp.printer()
        
        assert printer

        assert printer.info
        assert printer.info.name == "EPSON XP-6000 Series"
        assert printer.info.uuid == "cfe92100-67c4-11d4-a45f-f8d027761251"
        assert printer.info.version == "20.44.NU11JA"
        assert printer.info.uptime == 1359212

        assert printer.markers
        assert printer.markers[0]
        assert printer.markers[0].marker_id == 4
        assert printer.markers[0].marker_type == "ink-cartridge"
        assert printer.markers[0].name == "Black ink"
        assert printer.markers[0].color == "#000000"
        assert printer.markers[0].level == 58
        assert printer.markers[0].low_level == 15
        assert printer.markers[0].high_level == 100

        assert printer.markers[1]
        assert printer.markers[1].marker_id == 1
        assert printer.markers[1].marker_type == "ink-cartridge"
        assert printer.markers[1].name == "Cyan ink"
        assert printer.markers[1].color == "#00FFFF"
        assert printer.markers[1].level == 91
        assert printer.markers[1].low_level == 15
        assert printer.markers[1].high_level == 100

        assert printer.markers[2]
        assert printer.markers[2].marker_id == 2
        assert printer.markers[2].marker_type == "ink-cartridge"
        assert printer.markers[2].name == "Magenta ink"
        assert printer.markers[2].color == "#FF00FF"
        assert printer.markers[2].level == 73
        assert printer.markers[2].low_level == 15
        assert printer.markers[2].high_level == 100

        assert printer.markers[3]
        assert printer.markers[3].marker_id == 0
        assert printer.markers[3].marker_type == "ink-cartridge"
        assert printer.markers[3].name == "Photo Black ink"
        assert printer.markers[3].color == "#000000"
        assert printer.markers[3].level == 98
        assert printer.markers[3].low_level == 15
        assert printer.markers[3].high_level == 100

        assert printer.markers[4]
        assert printer.markers[4].marker_id == 3
        assert printer.markers[4].marker_type == "ink-cartridge"
        assert printer.markers[4].name == "Yellow ink"
        assert printer.markers[4].color == "#FFFF00"
        assert printer.markers[4].level == 95
        assert printer.markers[4].low_level == 15
        assert printer.markers[4].high_level == 100
