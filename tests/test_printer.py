"""Tests for Printer."""
import asyncio

from ipp.printer import Printer
from tests import DEFAULT_PRINTER_URI


def test_init() -> None:
    instance = Printer(DEFAULT_PRINTER_URI)
    assert instance == None


def test_get_attributes() -> None:
    instance = Printer(DEFAULT_PRINTER_URI)
    attributes = Printer.get_attributes()

    assert attributes == {}


def test_get_jobs() -> None:
    instance = Printer(DEFAULT_PRINTER_URI)
    jobs = Printer.get_jobs()

    assert jobs == {}