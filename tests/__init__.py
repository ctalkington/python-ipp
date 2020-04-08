"""Tests for IPP."""
import os

DEFAULT_PRINTER_HOST = "epson761251.local"
DEFAULT_PRINTER_PORT = 631
DEFAULT_PRINTER_PATH = "/ipp/print"
DEFAULT_PRINTER_URI = (
    f"ipp://{DEFAULT_PRINTER_HOST}:{DEFAULT_PRINTER_PORT}{DEFAULT_PRINTER_PATH}"
)

IPP11_PRINTER_ATTRIBUTES = {
    "attributes-charset": "",
    "attributes-natural-language": "",
    "charset-configured": "",
    "charset-supported": "",
    "compression-supported": "",
    "document-format-default": "",
    "document-format-supported": "",
    "generated-natural-language-supported": "",
    "ipp-versions-supported": "",
    "operations-supported": "",
    "pdl-override-supported": "",
    "printer-is-accepting-jobs": "",
    "printer-name": "",
    "printer-state": "",
    "printer-state-reasons": "",
    "printer-up-time": "",
    "printer-uri": "",
    "printer-uri-supported": "",
    "queued-job-count": "",
    "request-id": "",
    "requested-attributes": "",
    "requesting-user-name": "",
    "status-code": "",
    "uri-authentication-supported": "",
    "uri-security-supported": "",
    "version-number": "",
}

IPP20_PRINTER_ATTRIBUTES = IPP11_PRINTER_ATTRIBUTES + {
    "color-supported": "",
    "copies-default": "",
    "copies-supported": "",
    "finishings-default": "",
    "finishings-supported": "",
    "job-creation-attributes-supported": "",
    "media-default": "",
    "media-ready": "",
    "media-supported": "",
    "orientation-requested-default": "",
    "orientation-requested-supported": "",
    "output-bin-default": "",
    "output-bin-supported": "",
    "pages-per-minute": "",
    "pages-per-minute-color": "",
    "print-quality-default": "",
    "print-quality-supported": "",
    "printer-alert": "",
    "printer-alert-description": "",
    "printer-device-id": "",
    "printer-info": "",
    "printer-location": "",
    "printer-make-and-model": "",
    "printer-more-info": "",
    "printer-resolution-default": "",
    "sides-default": "",
    "sides-supported": "",
    "status-message": "",
}


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
