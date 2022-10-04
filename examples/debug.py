# pylint: disable=W0621
"""Asynchronous Python client for IPP."""
import asyncio

from pyipp import IPP
from pyipp.enums import IppOperation


async def main():
    """Show example of connecting to your IPP print server."""
    async with IPP("ipps://192.168.1.92:631/ipp/print") as ipp:
        response = await ipp.raw(
            IppOperation.GET_PRINTER_ATTRIBUTES,
            {
                "operation-attributes-tag": {
                    "requested-attributes": [
                        "printer-name",
                        "printer-type",
                        "printer-location",
                        "printer-info",
                        "printer-make-and-model",
                        "printer-state",
                        "printer-state-message",
                        "printer-state-reason",
                        "printer-uri-supported",
                        "device-uri",
                        "printer-is-shared",
                        "printer-more-info",
                    ],
                },
            },
        )

        with open("printer-attributes.bin", "wb") as file:
            file.write(response)
            file.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
