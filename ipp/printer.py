"""Printer Model for IPP."""
from yarl import URL

from .const import (
    DEFAULT_CHARSET,
    DEFAULT_CHARSET_LANGUAGE,
    DEFAULT_PRINTER_ATTRIBUTES,
    DEFAULT_JOB_ATTRIBUTES,
    DEFAULT_PROTO_VERSION,
)
from .ipp import IPP
from .enums import IppOperation


class Printer:
    """Abstraction for interaction with a printer using Internet Printing Protocol."""

    def __init__(self, uri: str):
        self.uri = uri
        self.charset = DEFAULT_CHARSET
        self.language = DEFAULT_CHARSET_LANGUAGE
        self.version = DEFAULT_PROTO_VERSION

        url = URL(uri)
        self.secure = url.scheme == "ipps"
        self.ipp = IPP(
            host=url.host, port=url.port, base_path=url.path, tls=self.secure
        )

    def _message(self, operation: str, msg: dict):
        base = {
            "version": self.version,
            "operation": operation,
            "id": None,  # will get added by encoder if one isn't given
            "operation-attributes-tag": {  # these are required to be in this order
                "attributes-charset": self.charset,
                "attributes-natural-language": self.language,
                "printer-uri": self.uri,
                "requesting-user-name": "PythonIPP",
            },
        }

        if msg is not dict:
            msg = {}

        return {**base, **msg}

    async def execute(self, operation: str, message: dict):
        message = self._message(operation, message)
        return await self.ipp._request(data=message)

    async def get_attributes(self, attributes=None):
        response_data = await self.execute(
            IppOperation.GET_PRINTER_ATTRIBUTES,
            {
                "requested-attributes": attributes
                if attributes
                else DEFAULT_PRINTER_ATTRIBUTES,
            },
        )

        return next(iter(response_data["printers"] or []), None)

    async def get_jobs(
        self, which_jobs: str = "not-completed", my_jobs: bool = False, attributes=None
    ):
        response_data = await self.execute(
            IppOperation.GET_JOBS,
            {
                "printer-uri": self.uri,
                "which-jobs": which_jobs,
                "my-jobs": my_jobs,
                "requested-attributes": attributes + ["job-id"]
                if attributes
                else DEFAULT_JOB_ATTRIBUTES,
            },
        )

        return {j["job-id"]: j for j in response_data["jobs"]}

