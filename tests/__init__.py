"""Tests for IPP."""
import os

DEFAULT_PRINTER_HOST = "epson761251.local"
DEFAULT_PRINTER_PORT = 631
DEFAULT_PRINTER_PATH = "/ipp/print"
DEFAULT_PRINTER_URI = (
    f"ipp://{DEFAULT_PRINTER_HOST}:{DEFAULT_PRINTER_PORT}{DEFAULT_PRINTER_PATH}"
)

# RFC 2911 - IPP 1.1
RFC2911_PRINTER_ATTRS = {
    "attributes-charset": "",
    "attributes-natural-language": "",
    "charset-configured": "",
    "charset-supported": "",
    "color-supported": "",
    "compression-supported": "",
    "copies-default": "",
    "copies-supported": "",
    "document-format-default": "",
    "document-format-supported": "",
    "finishings-default": "",
    "finishings-supported": "",
    "generated-natural-language-supported": "",
    "ipp-versions-supported": "",
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
    "printer-is-accepting-jobs": "",
    "printer-location": "",
    "printer-make-and-model": "",  # optional
    "printer-more-info": "",
    "printer-name": "",
    "printer-resolution-default": "",
    "printer-state": "",
    "printer-state-reasons": "",
    "printer-up-time": "",
    "printer-uri": "",
    "printer-uri-supported": "",
    "operations-supported": "",
    "pdl-override-supported": "",
    "queued-job-count": "",
    "request-id": "",
    "requested-attributes": "",
    "requesting-user-name": "",
    "sides-default": "",
    "sides-supported": "",
    "status-code": "",
    "status-message": "",
    "uri-authentication-supported": "",
    "uri-security-supported": "",
    "version-number": "",
}

# RFC 3995
RFC3995_PRINTER_ATTRS = {
    "printer-state-change-date-time": "",
    "printer-state-change-time": "",
}

# PWG 5100.2
PWG51002_PRINTER_ATTRS = {
    "output-bin-default": "",
    "output-bin-supported": "",
}

# PWG 5100.3
PWG51003_PRINTER_ATTRS = {
    "job-account-id-default": "",
    "job-account-id-supported": "",
    "job-accounting-user-id-default": "",
    "job-accounting-user-id-supported": "",
    "media-col-default": "",
    "media-col-ready": "",
    "media-col-supported": "",
    "media-type-supported": "",
}

# PWG 5100.4
PWG51004_PRINTER_ATTRS = {
    "pwg-raster-document-resolution-supported": "",
    "pwg-raster-document-sheet-back": "",
    "pwg-raster-document-type-supported": "",
}

# PWG 5100.6
PWG51006_PRINTER_ATTRS = {
    "overrides-supported": "",
}

# PWG 5100.7
PWG51007_PRINTER_ATTRS = {
    "print-content-optimize-default": "",
    "print-content-optimize-supported": "",
}

# PWG 5100.9
PWG51009_PRINTER_ATTRS = {
    "printer-alert": "",
    "printer-alert-description": "",
}

# PWG 5100.11
PWG510011_PRINTER_ATTRS = {
    "feed-orientation-default": "",
    "feed-orientation-supported": "",
    "job-creation-attributes-supported": "",
    "job-ids-supported": "",
    "job-password-supported": "",
    "job-password-encryption-supported": "",
    "media-col-database": "",
    "which-jobs-supported": "",
}

# PWG 5100.13
PWG510013_PRINTER_ATTRS = {
    "document-password-supported": "",
    "identify-actions-default": "",
    "identify-actions-supported": "",
    "ipp-features-supported": "",
    "job-constraints-supported": "",
    "job-preferred-attributes-supported": "",
    "job-resolvers-supported": "",
    "media-bottom-margin-supported": "",
    "media-col-database.media-source-properties": "",
    "media-col-ready.media-source-properties": "",
    "media-left-margin-supported": "",
    "media-right-margin-supported": "",
    "media-source-supported": "",
    "media-top-margin-supported": "",
    "multiple-operation-timeout-action": "",
    "print-color-mode-default": "",
    "print-color-mode-supported": "",
    "print-rendering-intent-default": "",
    "print-rendering-intent-supported": "",
    "printer-charge-info": "",
    "printer-charge-info-url": "",
    "printer-config-change-date-time": "",
    "printer-config-change-time": "",
    "printer-geo-location": "",
    "printer-get-attributes-supported": "",
    "printer-icc-profiles": "",
    "printer-icons": "",
    "printer-mandatory-job-attributes": "",
    "printer-organization": "",
    "printer-organizational-unit": "",
    "printer-supply": "",
    "printer-supply-description": "",
    "printer-supply-info-uri": "",
    "printer-uuid": "",
    "which-jobs-supported": "",
}

# PWG 5100.13
IPP20_PRINTER_ATTRIBUTES = {
    **RFC2911_PRINTER_ATTRS,
    **RFC3995_PRINTER_ATTRS,
    **PWG51002_PRINTER_ATTRS,
    **PWG51003_PRINTER_ATTRS,
    **PWG51004_PRINTER_ATTRS,
    **PWG51006_PRINTER_ATTRS,
    **PWG51007_PRINTER_ATTRS,
    **PWG51009_PRINTER_ATTRS,
    **PWG510011_PRINTER_ATTRS,
    **PWG510013_PRINTER_ATTRS,
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
