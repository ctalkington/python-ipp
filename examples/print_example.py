# pylint: disable=W0621
"""Asynchronous Python client for IPP."""
import asyncio

from pyipp import IPP
from pyipp.enums import IppOperation


async def main() -> None:
    """Show example of printing via IPP print server."""
    pdf_file = "/path/to/pdf.pfd"
    with open(pdf_file, "rb") as f:  # noqa: PTH123, ASYNC230
        content = f.read()

    async with IPP("ipp://192.168.1.92:631/ipp/print") as ipp:
        response = await ipp.execute(
            IppOperation.PRINT_JOB,
            {
                "operation-attributes-tag": {
                    "requesting-user-name": "Me",
                    "job-name": "My Test Job",
                    "document-format": "application/pdf",
                },
                "data": content,
            },
        )

        print(response)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
