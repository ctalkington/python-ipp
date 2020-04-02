"""Response Parser for IPP."""
import struct
from typing import Any, Dict, Tuple, cast

from .enums import IppDocumentState, IppJobState, IppPrinterState, IppTag


def parse_ieee1284_device_id(device_id: str) -> Dict[str, Any]:
    """Parse IEEE 1284 device id for common device info."""
    if device_id == "":
        return {}

    device_id = device_id.strip(";")
    device_info: Dict[str, Any] = dict(
        cast(Tuple[str, str], x.split(":", 2)) for x in device_id.split(";")
    )

    if not device_info.get("MANUFACTURER") and device_info.get("MFG"):
        device_info["MANUFACTURER"] = device_info["MFG"]

    if not device_info.get("MODEL") and device_info.get("MDL"):
        device_info["MODEL"] = device_info["MDL"]

    if not device_info.get("COMMAND SET") and device_info.get("CMD"):
        device_info["COMMAND SET"] = device_info["CMD"]

    return device_info


def parse_attribute(data: bytes, offset: int):
    """Parse attribute from IPP data.

    1 byte: Tag - b
    2 byte: Name Length - h
    N bytes: Name - direct access
    2 byte: Value Length -h
    N bytes: Value - direct access
    """

    attribute = {"tag": struct.unpack_from(">b", data, offset)[0]}
    offset += 1

    attribute["name-length"] = struct.unpack_from(">h", data, offset)[0]
    offset += 2

    offset_length = offset + attribute["name-length"]
    attribute["name"] = data[offset:offset_length].decode("utf-8")
    offset += attribute["name-length"]

    attribute["value-length"] = struct.unpack_from(">h", data, offset)[0]
    offset += 2

    if attribute["tag"] in (IppTag.ENUM.value, IppTag.INTEGER.value):
        attribute["value"] = struct.unpack_from(">i", data, offset)[0]

        if attribute["tag"] == IppTag.ENUM.value:
            if attribute["name"] == "job-state":
                attribute["value"] = IppJobState(attribute["value"])
            elif attribute["name"] == "printer-state":
                attribute["value"] = IppPrinterState(attribute["value"])
            elif attribute["name"] == "document-state":
                attribute["value"] = IppDocumentState(attribute["value"])

        offset += 4
    elif attribute["tag"] == IppTag.BOOLEAN.value:
        attribute["value"] = struct.unpack_from(">?", data, offset)[0]
        offset += 1
    elif attribute["tag"] == IppTag.DATE.value:
        attribute["value"] = struct.unpack_from(
            ">" + "b" * attribute["value-length"], data, offset
        )[0]
        offset += attribute["value-length"]
    elif attribute["tag"] == IppTag.RESERVED_STRING.value:
        if attribute["value-length"] > 0:
            offset_length = offset + attribute["value-length"]
            attribute["value"] = data[offset:offset_length].decode("utf-8")
            offset += attribute["value-length"]
        else:
            attribute["value"] = None
    elif attribute["tag"] == IppTag.RANGE.value:
        attribute["value"] = []
        for i in range(int(attribute["value-length"] / 4)):
            attribute["value"].append(struct.unpack_from(">i", data, offset + i * 4)[0])
        offset += attribute["value-length"]
    elif attribute["tag"] == IppTag.RESOLUTION.value:
        attribute["value"] = struct.unpack_from(">iib", data, offset)
        offset += attribute["value-length"]
    else:
        offset_length = offset + attribute["value-length"]
        attribute["value"] = data[offset:offset_length].decode("utf-8")
        offset += attribute["value-length"]

    return attribute, offset


def parse(raw_data: bytes, contains_data=False):
    r"""Parse raw IPP data.

    1 byte: Protocol Major Version - b
    1 byte: Protocol Minor Version - b
    2 byte: Operation ID/Status Code - h
    4 byte: Request ID - i

    1 byte: Operation Attribute Byte (\0x01)

    N Mal: Attributes

    1 byte: Attribute End Byte (\0x03)
    """

    data: Dict[str, Any] = {}
    offset = 0

    data["version"] = struct.unpack_from(">bb", raw_data, offset)
    offset += 2

    data["status-code"] = struct.unpack_from(">h", raw_data, offset)[0]
    offset += 2

    data["request-id"] = struct.unpack_from(">i", raw_data, offset)[0]
    offset += 4

    data["operation-attributes"] = []
    data["jobs"] = []
    data["printers"] = []
    data["data"] = b""

    attribute_key = ""
    previous_attribute_name = ""
    tmp_data: Dict[str, Any] = {}

    while struct.unpack_from("b", raw_data, offset)[0] != IppTag.END.value:
        # check for operation, job or printer attribute start byte
        # if tmp data and attribute key is set, another operation was sent
        # add it and reset tmp data
        if struct.unpack_from("b", raw_data, offset)[0] == IppTag.OPERATION.value:
            if tmp_data and attribute_key:
                data[attribute_key].append(tmp_data)
                tmp_data = {}

            attribute_key = "operation-attributes"
            offset += 1
        elif struct.unpack_from("b", raw_data, offset)[0] == IppTag.JOB.value:
            if tmp_data and attribute_key:
                data[attribute_key].append(tmp_data)
                tmp_data = {}

            attribute_key = "jobs"
            offset += 1
        elif struct.unpack_from("b", raw_data, offset)[0] == IppTag.PRINTER.value:
            if tmp_data and attribute_key:
                data[attribute_key].append(tmp_data)
                tmp_data = {}

            attribute_key = "printers"
            offset += 1

        attribute, new_offset = parse_attribute(raw_data, offset)

        # if attribute has a name -> add it
        # if attribute doesn't have a name -> it is part of an array
        if attribute["name"]:
            tmp_data[attribute["name"]] = attribute["value"]
            previous_attribute_name = attribute["name"]
        elif previous_attribute_name:
            # check if attribute is already an array
            # else convert it to an array
            if isinstance(tmp_data[previous_attribute_name], list):
                tmp_data[previous_attribute_name].append(attribute["value"])
            else:
                tmp_value = tmp_data[previous_attribute_name]
                tmp_data[previous_attribute_name] = [tmp_value, attribute["value"]]

        offset = new_offset

    if isinstance(data[attribute_key], list):
        data[attribute_key].append(tmp_data)

    if isinstance(data["operation-attributes"], list):
        data["operation-attributes"] = data["operation-attributes"][0]

    if contains_data:
        offset_start = offset + 1
        data["data"] = raw_data[offset_start:]

    return data


def parse_make_and_model(make_and_model: str) -> Tuple[str, str]:
    """Parse make and model for separate device make and model."""
    make_and_model = make_and_model.strip()

    if make_and_model == "":
        return ("Unknown", "Unknown")

    make = "Unknown"
    model = "Unknown"
    found_make = False
    known_makes = ["brother", "canon", "epson", "hp", "xerox"]

    test_against = make_and_model.lower()
    for known_make in known_makes:
        if test_against.startswith(known_make):
            found_make = True
            mlen = len(known_make)
            make = make_and_model[:mlen]
            model = make_and_model[mlen:].strip()
            break

    if not found_make:
        split = make_and_model.split(None, 1)
        make = split[0]

        if len(split) == 2:
            model = split[1].strip()

    return (make, model)
