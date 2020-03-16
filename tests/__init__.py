"""Tests for IPP."""
import os

DEFAULT_PRINTER_URI = "ipp://printer.example.com:631/ipp/print"


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
