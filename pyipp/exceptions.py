"""Exceptions for IPP."""


class IPPError(Exception):
    """Generic IPP exception."""

    pass


class IPPConnectionError(IPPError):
    """IPP connection exception."""

    pass


class IPPConnectionUpgradeRequired(IPPError):
    """IPP connection upgrade requested."""

    pass


class IPPParseError(IPPError):
    """IPP parse exception."""

    pass


class IPPResponseError(IPPError):
    """IPP response exception."""

    pass
