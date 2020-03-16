# Python: Internet Printing Protocol (IPP) Client

Asynchronous Python client for Internet Printing Protocol (IPP).

## About

This package allows you to monitor printers that support the Internet Printing Protocol (IPP) programmatically.

## Installation

```bash
pip install pyipp
```

## Usage

```python
import asyncio

from pyipp import IPP, Printer


async def main():
    """Show example of connecting to your IPP print server."""
    async with IPP("ipps://EPSON123456.local:631/ipp/print") as ipp:
        printer: Printer = await ipp.printer()
        print(printer)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```
