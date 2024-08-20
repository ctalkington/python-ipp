# pylint: disable=W0621
"""Asynchronous Python client for IPP."""
import asyncio
from pathlib import Path

from pyipp import IPP
from pyipp.enums import IppOperation


async def main() -> None:
    """Show an example of printing on your IP print server."""
    content = Path("/path/to/pdf.pdf").read_bytes()

    # then the printer must be shared if CUPS is used
    async with IPP("ipp://192.168.1.92:631/ipp/print") as ipp:
        response = await ipp.execute(
            IppOperation.PRINT_JOB,
            {
                "operation-attributes-tag": {
                    "requesting-user-name": "Me",
                    "job-name": "My Test Job",
                    "document-format": "application/pdf",
                },
                "file": content,
            },
        )

        print(response)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
