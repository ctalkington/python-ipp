# pylint: disable=W0621
"""Asynchronous Python client for IPP."""
import asyncio

import aiofiles

from pyipp import IPP
from pyipp.enums import IppOperation


async def main() -> None:
    """Print a PDF document with media from tray-2."""

    pdf_file = "/path/to/pdf.pdf"
    async with aiofiles.open(pdf_file, mode="rb") as file:
        content = await file.read()

    async with IPP("ipp://192.168.1.92:631/ipp/print") as ipp:
        response = await ipp.execute(
            IppOperation.PRINT_JOB,
            {
                "operation-attributes-tag": {
                    "requesting-user-name": "Me",
                    "job-name": "My Test Job",
                    "document-format": "application/pdf",
                },
                "job-attributes-tag": {
                    "media-col": {
                        "media-source": "tray-2",
                    },
                },
                "data": content,
            },
        )

        print(response)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
