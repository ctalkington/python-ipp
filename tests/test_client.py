"""Tests for IPP Client."""
import asyncio

import pytest
from aiohttp import ClientResponse, ClientSession
from aresponses import Response, ResponsesMockServer

from pyipp import IPP
from pyipp.const import DEFAULT_PRINTER_ATTRIBUTES
from pyipp.enums import IppOperation
from pyipp.exceptions import (
    IPPConnectionError,
    IPPConnectionUpgradeRequired,
    IPPError,
    IPPParseError,
    IPPVersionNotSupportedError,
)

from . import (
    DEFAULT_PRINTER_HOST,
    DEFAULT_PRINTER_PATH,
    DEFAULT_PRINTER_PORT,
    DEFAULT_PRINTER_URI,
    load_fixture_binary,
)

MATCH_DEFAULT_HOST = f"{DEFAULT_PRINTER_HOST}:{DEFAULT_PRINTER_PORT}"
NON_STANDARD_PORT = 3333


@pytest.mark.asyncio
async def test_ipp_request(aresponses: ResponsesMockServer) -> None:
    """Test IPP response is handled correctly."""
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
async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test IPP response is handled correctly."""
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
async def test_request_port(aresponses: ResponsesMockServer) -> None:
    """Test the IPP server running on non-standard port."""
    aresponses.add(
        f"{DEFAULT_PRINTER_HOST}:{NON_STANDARD_PORT}",
        DEFAULT_PRINTER_PATH,
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/ipp"},
            body=load_fixture_binary("get-printer-attributes-epsonxp6000.bin"),
        ),
    )

    async with ClientSession() as session:
        ipp = IPP(
            host=DEFAULT_PRINTER_HOST,
            port=NON_STANDARD_PORT,
            base_path=DEFAULT_PRINTER_PATH,
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
async def test_request_tls(aresponses: ResponsesMockServer) -> None:
    """Test the IPP server over TLS."""
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
        ipp = IPP(
            host=DEFAULT_PRINTER_HOST,
            port=DEFAULT_PRINTER_PORT,
            tls=True,
            base_path=DEFAULT_PRINTER_PATH,
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
async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout from the IPP server."""

    # Faking a timeout by sleeping
    async def response_handler(_: ClientResponse) -> Response:
        await asyncio.sleep(2)
        return Response(body="Timeout!")

    aresponses.add(
        MATCH_DEFAULT_HOST,
        DEFAULT_PRINTER_PATH,
        "POST",
        response_handler,
    )

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
async def test_http_error404(aresponses: ResponsesMockServer) -> None:
    """Test HTTP 404 response handling."""
    aresponses.add(
        MATCH_DEFAULT_HOST,
        DEFAULT_PRINTER_PATH,
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
async def test_http_error426(aresponses: ResponsesMockServer) -> None:
    """Test HTTP 426 response handling."""
    aresponses.add(
        MATCH_DEFAULT_HOST,
        DEFAULT_PRINTER_PATH,
        "POST",
        aresponses.Response(
            text="Upgrade Required",
            headers={"Upgrade": "TLS/1.0, HTTP/1.1"},
            status=426,
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
async def test_unexpected_response(aresponses: ResponsesMockServer) -> None:
    """Test unexpected response handling."""
    aresponses.add(
        MATCH_DEFAULT_HOST,
        DEFAULT_PRINTER_PATH,
        "POST",
        aresponses.Response(text="Surprise!", status=200),
    )

    async with ClientSession() as session:
        ipp = IPP(DEFAULT_PRINTER_URI, session=session)
        with pytest.raises(IPPParseError):
            assert await ipp.execute(
                IppOperation.GET_PRINTER_ATTRIBUTES,
                {
                    "operation-attributes-tag": {
                        "requested-attributes": DEFAULT_PRINTER_ATTRIBUTES,
                    },
                },
            )


@pytest.mark.asyncio
async def test_ipp_error_0x0503(aresponses: ResponsesMockServer) -> None:
    """Test IPP Error 0x0503 response handling."""
    aresponses.add(
        MATCH_DEFAULT_HOST,
        DEFAULT_PRINTER_PATH,
        "POST",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/ipp"},
            body=load_fixture_binary("get-printer-attributes-error-0x0503.bin"),
        ),
    )

    async with ClientSession() as session:
        ipp = IPP(DEFAULT_PRINTER_URI, session=session)
        with pytest.raises(IPPVersionNotSupportedError):
            assert await ipp.execute(
                IppOperation.GET_PRINTER_ATTRIBUTES,
                {
                    "operation-attributes-tag": {
                        "requested-attributes": DEFAULT_PRINTER_ATTRIBUTES,
                    },
                },
            )
