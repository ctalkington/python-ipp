"""Tests for Printer."""
import asyncio
from collections import namedtuple

import pytest
from aiohttp import ClientSession, TCPConnector
from ipp import Printer
from tests import (
    DEFAULT_PRINTER_URI,
    RESPONSE_GET_JOBS_FULL,
    RESPONSE_GET_PRINTER_ATTRIBUTES_FULL,
    CaseControlledTestServer,
    FakeResolver,
)

# pylint: disable=redefined-outer-name


_RedirectContext = namedtuple("RedirectContext", "add_server session")


@pytest.fixture
async def aiohttp_redirector():
    """Set up AIOHTTP Resolver with ClientSession."""
    resolver = FakeResolver()
    connector = TCPConnector(resolver=resolver, use_dns_cache=False)
    async with ClientSession(connector=connector) as session:
        yield _RedirectContext(add_server=resolver.add, session=session)


def test_init() -> None:
    """Test the initialization of Printer."""
    printer = Printer(DEFAULT_PRINTER_URI)
    assert isinstance(printer, Printer)


@pytest.mark.asyncio
async def test_get_attributes(aiohttp_redirector) -> None:
    """Test the get_attributes method."""
    async with CaseControlledTestServer() as server:
        aiohttp_redirector.add_server("printer.example.com", 631, server.port)
        printer = Printer(DEFAULT_PRINTER_URI, session=aiohttp_redirector.session)

        task = asyncio.create_task(printer.get_attributes())
        request = await server.receive_request()
        assert request.path_qs == "/ipp/print"
        server.send_response(
            request,
            text=RESPONSE_GET_PRINTER_ATTRIBUTES_FULL,
            headers={"Content-Type": "application/ipp"},
        )

        attributes = await task

    assert attributes == {}


@pytest.mark.asyncio
async def test_get_jobs(aiohttp_redirector) -> None:
    """Test the get_jobs method."""
    async with CaseControlledTestServer() as server:
        aiohttp_redirector.add_server("printer.example.com", 631, server.port)
        printer = Printer(DEFAULT_PRINTER_URI, session=aiohttp_redirector.session)

        task = asyncio.create_task(printer.get_jobs())
        request = await server.receive_request()
        assert request.path_qs == "/ipp/print"
        server.send_response(
            request,
            body=RESPONSE_GET_JOBS_FULL,
            headers={"Content-Type": "application/ipp"},
        )

        jobs = await task

    assert jobs == {}
