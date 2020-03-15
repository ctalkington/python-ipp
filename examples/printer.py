# pylint: disable=W0621
"""Asynchronous Python client for IPP."""
import asyncio

from ipp import IPP


async def main():
    """Show example of connecting to your IPP print server."""
    async with IPP("ipps://192.168.1.92:631/ipp/print") as ipp:
        # Get Printer Info
        printer = await ipp.printer()
        print(printer)

        # Get Print Jobs
        jobs = await ipp.jobs()
        print(jobs)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
