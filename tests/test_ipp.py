"""Tests for IPP."""
import asyncio

from aiohttp import ClientSession
import pytest

from ipp import IPP, Printer
from ipp.const import DEFAULT_PRINTER_ATTRIBUTES
from ipp.enums import IppOperation
from ipp.exceptions import IPPConnectionError, IPPError

from . import DEFAULT_PRINTER_URI, load_fixture_binary


@pytest.mark.asyncio
async def test_ipp_request(aresponses):
    """Test IPP response is handled correctly."""
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
        response = await ipp.execute(
            IppOperation.GET_PRINTER_ATTRIBUTES,
            {
                "operation-attributes-tag": {
                    "requested-attributes": DEFAULT_PRINTER_ATTRIBUTES,
                },
            },
        )
        assert response["status-code"] == 0


@pytest.mark.asyncio
async def test_internal_session(aresponses):
    """Test IPP response is handled correctly."""
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

    async with IPP(DEFAULT_PRINTER_URI) as ipp:
        response = await ipp.execute(
            IppOperation.GET_PRINTER_ATTRIBUTES,
            {
                "operation-attributes-tag": {
                    "requested-attributes": DEFAULT_PRINTER_ATTRIBUTES,
                },
            },
        )
        assert response["status-code"] == 0


@pytest.mark.asyncio
async def test_request_port(aresponses):
    """Test the IPP server running on non-standard port."""
    aresponses.add(
        "printer.example.com:3333",
        "/ipp/print",
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/ipp"},
            body=load_fixture_binary("get-printer-attributes.bin"),
        ),
    )

    async with ClientSession() as session:
        ipp = IPP(
            host="printer.example.com",
            port=3333,
            base_path="/ipp/print",
            session=session,
        )
        response = await ipp.execute(
            IppOperation.GET_PRINTER_ATTRIBUTES,
            {
                "operation-attributes-tag": {
                    "requested-attributes": DEFAULT_PRINTER_ATTRIBUTES,
                },
            },
        )
        assert response["status-code"] == 0


@pytest.mark.asyncio
async def test_timeout(aresponses):
    """Test request timeout from the IPP server."""
    # Faking a timeout by sleeping
    async def response_handler(_):
        await asyncio.sleep(2)
        return aresponses.Response(body="Timeout!")

    aresponses.add("printer.example.com:631", "/ipp/print", "POST", response_handler)

    async with ClientSession() as session:
        ipp = IPP(DEFAULT_PRINTER_URI, session=session, request_timeout=1)
        with pytest.raises(IPPConnectionError):
            assert await ipp.execute(
                IppOperation.GET_PRINTER_ATTRIBUTES,
                {
                    "operation-attributes-tag": {
                        "requested-attributes": DEFAULT_PRINTER_ATTRIBUTES,
                    },
                },
            )


@pytest.mark.asyncio
async def test_http_error400(aresponses):
    """Test HTTP 404 response handling."""
    aresponses.add(
        "printer.example.com:631",
        "/ipp/print",
        "POST",
        aresponses.Response(text="Not Found!", status=404),
    )

    async with ClientSession() as session:
        ipp = IPP(DEFAULT_PRINTER_URI, session=session)
        with pytest.raises(IPPError):
            assert await ipp.execute(
                IppOperation.GET_PRINTER_ATTRIBUTES,
                {
                    "operation-attributes-tag": {
                        "requested-attributes": DEFAULT_PRINTER_ATTRIBUTES,
                    },
                },
            )


@pytest.mark.asyncio
async def test_unexpected_response(aresponses):
    """Test unexpected response handling."""
    aresponses.add(
        "printer.example.com:631",
        "/ipp/print",
        "POST",
        aresponses.Response(text="Surprise!", status=200),
    )

    async with ClientSession() as session:
        ipp = IPP(DEFAULT_PRINTER_URI, session=session)
        with pytest.raises(IPPError):
            assert await ipp.execute(
                IppOperation.GET_PRINTER_ATTRIBUTES,
                {
                    "operation-attributes-tag": {
                        "requested-attributes": DEFAULT_PRINTER_ATTRIBUTES,
                    },
                },
            )


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
        assert printer.info.uuid == "urn:uuid:cfe92100-67c4-11d4-a45f-f8d027761251"
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
