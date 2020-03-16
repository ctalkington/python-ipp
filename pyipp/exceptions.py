"""Exceptions for IPP."""


class IPPError(Exception):
    """Generic IPP exception."""

    pass


class IPPConnectionError(IPPError):
    """IPP connection exception."""

    pass
