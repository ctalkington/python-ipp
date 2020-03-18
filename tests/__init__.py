"""Tests for IPP."""
import os

DEFAULT_PRINTER_HOST = "epson761251.local"
DEFAULT_PRINTER_PORT = 631
DEFAULT_PRINTER_PATH = "/ipp/print"
DEFAULT_PRINTER_URI = (
    f"ipp://{DEFAULT_PRINTER_HOST}:{DEFAULT_PRINTER_PORT}{DEFAULT_PRINTER_PATH}"
)


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path) as fptr:
        return fptr.read()


def load_fixture_binary(filename):
    """Load a binary fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, "rb") as fptr:
        return fptr.read()
