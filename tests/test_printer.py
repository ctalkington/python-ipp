"""Tests for Printer."""
import pytest

from ipp import IPP, Printer
from tests import DEFAULT_PRINTER_URI


def test_init() -> None:
    instance = Printer(DEFAULT_PRINTER_URI)
    assert isinstance(instance, Printer)
    assert isinstance(instance.ipp, IPP)


@pytest.mark.asyncio
async def test_get_attributes() -> None:
    instance = Printer(DEFAULT_PRINTER_URI)
    attributes = await instance.get_attributes()

    assert attributes == {}


@pytest.mark.asyncio
async def test_get_jobs() -> None:
    instance = Printer(DEFAULT_PRINTER_URI)
    jobs = await instance.get_jobs()

    assert jobs == {}
