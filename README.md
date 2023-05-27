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

## Setting up development environment

This Python project is fully managed using the [Poetry](https://python-poetry.org) dependency
manager. But also relies on the use of NodeJS for certain checks during
development.

You need at least:

- Python 3.9+
- [Poetry](https://python-poetry.org/docs/#installation)
- NodeJS 18+ (including NPM)

To install all packages, including all development requirements:

```bash
npm install
poetry install
```

As this repository uses the [pre-commit](https://pre-commit.com/) framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```
