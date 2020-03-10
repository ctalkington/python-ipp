# pylint: disable=W0621
"""Asynchronous Python client for IPP."""
import asyncio

from ipp import Printer


async def main():
    """Show example of connecting to your IPP print server."""
    async with Printer("ipps://192.168.1.92:631/ipp/print") as printer:
        # Get Printer Attributes
        attributes = await printer.get_attributes()
        print(attributes)

        # Get Printer JObs
        jobs = await printer.get_jobs()
        print(jobs)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
