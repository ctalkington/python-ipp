# pylint: disable=W0621
"""Asynchronous Python client for IPP."""
import asyncio

from pyipp import IPP


async def main() -> None:
    """Show example of connecting to your IPP print server."""
    async with IPP("ipps://EPSON761251.local:631/ipp/print") as ipp:
        # Get Printer Info
        printer = await ipp.printer()
        print(printer)

    async with IPP("ipp://hp6830.local:631/ipp/print") as ipp:
        # Get Printer Info
        printer = await ipp.printer()
        print(printer)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
