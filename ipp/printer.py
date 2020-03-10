"""Printer Model for IPP."""
from aiohttp.client import ClientSession
from deepmerge import always_merger
from yarl import URL

from .const import (
    DEFAULT_CHARSET,
    DEFAULT_CHARSET_LANGUAGE,
    DEFAULT_JOB_ATTRIBUTES,
    DEFAULT_PRINTER_ATTRIBUTES,
    DEFAULT_PROTO_VERSION,
)
from .enums import IppOperation
from .ipp import IPP


class Printer(IPP):
    """Abstraction for interaction with a printer using Internet Printing Protocol."""

    def __init__(self, uri: str, session: ClientSession = None):
        """Initialize the Printer."""
        self.uri = uri
        self.charset = DEFAULT_CHARSET
        self.language = DEFAULT_CHARSET_LANGUAGE
        self.version = DEFAULT_PROTO_VERSION

        url = URL(uri)
        self.secure = url.scheme == "ipps"

        super().__init__(
            host=url.host,
            port=url.port,
            base_path=url.path,
            tls=self.secure,
            session=session,
        )

    def _message(self, operation: IppOperation, msg: dict):
        """Build a request message to be sent to the server."""
        base = {
            "version": self.version,
            "operation": operation,
            "request-id": None,  # will get added by serializer if one isn't given
            "operation-attributes-tag": {  # these are required to be in this order
                "attributes-charset": self.charset,
                "attributes-natural-language": self.language,
                "printer-uri": self.uri,
                "requesting-user-name": "PythonIPP",
            },
        }

        if msg is not dict:
            msg = {}

        return always_merger.merge(base, msg)

    async def execute(self, operation: IppOperation, message: dict) -> dict:
        """Send a request message to the server."""
        message = self._message(operation, message)
        return await self._request(data=message)

    async def get_attributes(self, attributes=None) -> dict:
        """Retreive the printer attributes from the server."""
        response_data = await self.execute(
            IppOperation.GET_PRINTER_ATTRIBUTES,
            {
                "operation-attributes-tag": {
                    "requested-attributes": attributes
                    if attributes
                    else DEFAULT_PRINTER_ATTRIBUTES,
                },
            },
        )

        if isinstance(response_data, dict):
            return next(iter(response_data["printers"] or []), {})

        return None

    async def get_jobs(
        self, which_jobs: str = "not-completed", my_jobs: bool = False, attributes=None
    ) -> dict:
        """Retreive the queued print jobs from the server."""
        response_data = await self.execute(
            IppOperation.GET_JOBS,
            {
                "operation-attributes-tag": {
                    "which-jobs": which_jobs,
                    "my-jobs": my_jobs,
                    "requested-attributes": attributes + ["job-id"]
                    if attributes
                    else DEFAULT_JOB_ATTRIBUTES,
                },
            },
        )

        if isinstance(response_data, dict):
            return {j["job-id"]: j for j in response_data["jobs"]}

        return None
