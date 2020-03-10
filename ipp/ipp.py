"""Asynchronous Python client for IPP."""
import asyncio
from socket import gaierror
from typing import Any, Mapping, Optional

import aiohttp
import async_timeout
from yarl import URL

from .__version__ import __version__
from .exceptions import IPPConnectionError, IPPError
from .parser import parse as parse_response
from .serializer import encode_dict


class IPP:
    """Main class for handling connections with IPP."""

    def __init__(
        self,
        host: str,
        base_path: str = "/ipp/printer",
        password: str = None,
        port: int = 631,
        request_timeout: int = 8,
        session: aiohttp.client.ClientSession = None,
        tls: bool = False,
        username: str = None,
        verify_ssl: bool = True,
        user_agent: str = None,
    ) -> None:
        """Initialize connection with IPP."""
        self._session = session
        self._close_session = False

        self.base_path = base_path
        self.host = host
        self.password = password
        self.port = port
        self.request_timeout = request_timeout
        self.tls = tls
        self.username = username
        self.verify_ssl = verify_ssl
        self.user_agent = user_agent

        if user_agent is None:
            self.user_agent = f"PythonIPP/{__version__}"

    async def _request(
        self,
        uri: str = "",
        data: Optional[Any] = None,
        params: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Handle a request to a IPP device."""
        scheme = "https" if self.tls else "http"

        method = "POST"
        url = URL.build(
            scheme=scheme, host=self.host, port=self.port, path=self.base_path
        ).join(URL(uri))

        auth = None
        if self.username and self.password:
            auth = aiohttp.BasicAuth(self.username, self.password)

        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/ipp",
            "Accept": "application/ipp, text/plain, */*",
        }

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        if data is None:
            data = {}

        if isinstance(data, dict):
            data = encode_dict(data)

        try:
            with async_timeout.timeout(self.request_timeout):
                response = await self._session.request(
                    method,
                    url,
                    auth=auth,
                    data=data,
                    params=params,
                    headers=headers,
                    ssl=self.verify_ssl,
                )
        except asyncio.TimeoutError as exception:
            raise IPPConnectionError(
                "Timeout occurred while connecting to IPP device."
            ) from exception
        except (aiohttp.ClientError, gaierror) as exception:
            raise IPPConnectionError(
                "Error occurred while communicating with IPP device."
            ) from exception

        if (response.status // 100) in [4, 5]:
            contents = await response.read()
            response.close()

            raise IPPError(response.status, {"message": contents.decode("utf8")})

        content_type = response.headers.get("Content-Type", "")

        if "application/ipp" in content_type:
            contents = await response.read()
            contents = parse_response(contents)

            if contents["status-code"] != 0:
                raise IPPError(
                    contents["status-code"],
                    # {"message": contents["operation-attributes"]["status-message"]},
                )

            return contents

        return await response.text()

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> "IPP":
        """Async enter."""
        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close()
