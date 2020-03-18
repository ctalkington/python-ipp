"""Tests for IPP."""
import asyncio

import pytest
from aiohttp import ClientSession
from pyipp import IPP
from pyipp.const import DEFAULT_PRINTER_ATTRIBUTES
from pyipp.enums import IppOperation
from pyipp.exceptions import IPPConnectionError, IPPConnectionUpgradeRequired, IPPError

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
async def test_http_error404(aresponses):
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
async def test_http_error426(aresponses):
    """Test HTTP 426 response handling."""
    aresponses.add(
        "printer.example.com:631",
        "/ipp/print",
        "POST",
        aresponses.Response(
            text="Upgrade Required", headers={"Upgrade": "TLS/1.2"}, status=426,
        ),
    )

    async with ClientSession() as session:
        ipp = IPP(DEFAULT_PRINTER_URI, session=session)
        with pytest.raises(IPPConnectionUpgradeRequired):
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
