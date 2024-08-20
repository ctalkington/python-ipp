# pylint: disable=W0621
"""Asynchronous Python client for IPP."""
import asyncio
from pathlib import Path

from pyipp import IPP
from pyipp.enums import IppOperation


async def main() -> None:
    """Show an example of add or modifying printer on your IP print server."""
    content = Path("/path/to/driver.ppd").read_bytes()

    async with IPP(
        host="ipp://127.0.0.1:631/printers/My_New_Printer",
        username="",
        password="",
    ) as ipp:
        response = await ipp.execute(
            IppOperation.CUPS_ADD_MODIFY_PRINTER,
            {
                "printer-attributes-tag": {
                    "device-uri": "socket://192.168.0.12:9100",
                    "printer-info": "My awesome printer",
                    "printer-location": "office",
                },
                "file": content,
            },
        )

        print(response)


if __name__ == "__main__":
    asyncio.run(main())
