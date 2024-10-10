"""Tests for IPP public interface."""
import pytest
from aiohttp import ClientSession
from aresponses import ResponsesMockServer

from pyipp import IPP, Printer
from pyipp.const import DEFAULT_PRINTER_ATTRIBUTES
from pyipp.enums import IppOperation

from . import (
    DEFAULT_PRINTER_HOST,
    DEFAULT_PRINTER_PATH,
    DEFAULT_PRINTER_PORT,
    DEFAULT_PRINTER_URI,
    load_fixture_binary,
)

MATCH_DEFAULT_HOST = f"{DEFAULT_PRINTER_HOST}:{DEFAULT_PRINTER_PORT}"


@pytest.mark.asyncio
async def test_printer(aresponses: ResponsesMockServer) -> None:
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
        printer = await ipp.printer()

        assert printer
        assert isinstance(printer, Printer)


@pytest.mark.asyncio
async def test_printer_update_logic(aresponses: ResponsesMockServer) -> None:
    """Test getting updated IPP printer information."""
    aresponses.add(
        MATCH_DEFAULT_HOST,
        DEFAULT_PRINTER_PATH,
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/ipp"},
            body=load_fixture_binary("get-printer-attributes-epsonxp6000.bin"),
        ),
        repeat=2,
    )

    async with ClientSession() as session:
        ipp = IPP(DEFAULT_PRINTER_URI, session=session)
        printer = await ipp.printer()

        assert printer
        assert isinstance(printer, Printer)

        printer = await ipp.printer()
        assert printer
        assert isinstance(printer, Printer)


@pytest.mark.asyncio
async def test_raw(aresponses: ResponsesMockServer) -> None:
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

        assert response
        assert isinstance(response, bytes)
