"""Models for IPP."""
from dataclasses import dataclass
from typing import List, Optional

from .parser import parse_ieee1284_device_id, parse_make_and_model

PRINTER_STATES = {3: "idle", 4: "printing", 5: "stopped"}


@dataclass(frozen=True)
class Info:
    """Object holding information from IPP."""

    command_set: str
    location: str
    name: str
    manufacturer: str
    model: str
    printer_name: str
    printer_info: str
    printer_uri_supported: list
    serial: Optional[str]
    uptime: int
    uuid: str
    version: str

    @staticmethod
    def from_dict(data: dict):
        """Return Info object from IPP response."""
        make_model = data.get("printer-make-and-model", "IPP Printer")
        device_id = data.get("printer-device-id", "")
        uuid = data.get("printer-uuid")

        make, model = parse_make_and_model(make_model)
        cmd = "Unknown"
        serial = None

        parsed_device_id = parse_ieee1284_device_id(device_id)

        if parsed_device_id.get("MFG") is not None:
            make = parsed_device_id["MFG"]

        if parsed_device_id.get("MDL") is not None:
            model = parsed_device_id["MDL"]

        if parsed_device_id.get("CMD") is not None:
            cmd = parsed_device_id["CMD"]

        if parsed_device_id.get("SN") is not None:
            serial = parsed_device_id["SN"]

        return Info(
            command_set=cmd,
            location=data.get("printer-location", ""),
            name=make_model,
            manufacturer=make,
            model=model,
            printer_name=data.get("printer-name", None),
            printer_info=data.get("printer-info", None),
            printer_uri_supported=data.get("printer-uri-supported", []),
            serial=serial,
            uptime=data.get("printer-up-time", 0),
            uuid=uuid[9:] if uuid else None,
            version=data.get("printer-firmware-string-version", None),
        )


@dataclass(frozen=True)
class Marker:
    """Object holding marker (ink) info from IPP."""

    marker_id: int
    marker_type: str
    name: str
    color: str
    level: int
    low_level: int
    high_level: int


@dataclass(frozen=True)
class State:
    """Object holding the IPP printer state."""

    printer_state: str
    reasons: str
    message: str

    @staticmethod
    def from_dict(data):
        """Return State object from IPP response."""
        state = data.get("printer-state", 0)
        reasons = data.get("printer-state-reasons", None)

        if reasons == "none":
            reasons = None

        return State(
            printer_state=PRINTER_STATES.get(state, state),
            reasons=reasons,
            message=data.get("printer-state-message", None),
        )


@dataclass(frozen=True)
class Printer:
    """Object holding the IPP printer information."""

    info: Info
    markers: List[Marker]
    state: State

    @staticmethod
    def from_dict(data):
        """Return Printer object from IPP response."""
        marker_colors = data.get("marker-colors", [])
        marker_levels = data.get("marker-levels", [])
        marker_high_levels = data.get("marker-high-levels", [])
        marker_low_levels = data.get("marker-low-levels", [])
        marker_types = data.get("marker-types", [])
        markers = [
            Marker(
                marker_id=marker_id,
                marker_type=marker_types[marker_id],
                name=marker,
                color=marker_colors[marker_id],
                level=marker_levels[marker_id],
                high_level=marker_high_levels[marker_id],
                low_level=marker_low_levels[marker_id],
            )
            for marker_id, marker in enumerate(data.get("marker-names", {}))
        ]
        markers.sort(key=lambda x: x.name)

        return Printer(
            info=Info.from_dict(data), markers=markers, state=State.from_dict(data)
        )
