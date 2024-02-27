# pylint: disable=W0621
"""Asynchronous Python client for IPP."""
import asyncio

from pyipp import IPP
from pyipp.enums import IppOperation


async def main() -> None:
    """Show example of executing operation against your IPP print server."""
    async with IPP("ipps://192.168.1.92:631/ipp/print") as ipp:
        response = await ipp.execute(
            IppOperation.GET_PRINTER_ATTRIBUTES,
            {
                "version": (2, 0),  # try (1, 1) for older devices
                "operation-attributes-tag": {
                    "requested-attributes": [
                        "printer-device-id",
                        "printer-name",
                        "printer-type",
                        "printer-location",
                        "printer-info",
                        "printer-make-and-model",
                        "printer-state",
                        "printer-state-message",
                        "printer-state-reason",
                        "printer-supply",
                        "printer-up-time",
                        "printer-uri-supported",
                        "device-uri",
                        "printer-is-shared",
                        "printer-more-info",
                        "printer-firmware-string-version",
                        "marker-colors",
                        "marker-high-levels",
                        "marker-levels",
                        "marker-low-levels",
                        "marker-names",
                        "marker-types",
                    ],
                },
            },
        )

        print(response)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
