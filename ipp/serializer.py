"""Data Serializer for IPP."""
import struct

from .const import CHARSET, CHARSET_LANGUAGE, DEFAULT_PROTO_VERSION
from .enums import IppOperation, IppTag
from .tags import ATTRIBUTE_TAG_MAP


def update_attribute_tag_map(attribute: str, tag: IppTag):
    """Update the attribute tag mapping."""
    ATTRIBUTE_TAG_MAP[attribute] = tag


def __construct_attibute_values(tag: IppTag, value):
    """Serialize the attribute values into IPP format."""
    bs = b''

    if tag in (IppTag.INTEGER, IppTag.ENUM):
        bs += struct.pack('>h', 4)
        bs += struct.pack('>i', value)
    elif tag == IppTag.BOOLEAN:
        bs += struct.pack('>h', 1)
        bs += struct.pack('>?', value)
    else:
        bs += struct.pack('>h', len(value))
        bs += value.encode('utf-8')

    return bs


def construct_attribute(name: str, value, tag=None):
    """Serialize the attribute into IPP format."""
    bs = b''

    if not tag:
        tag = ATTRIBUTE_TAG_MAP.get(name, None)

    if not tag:
        return bs

    if isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set):
        for index, v in enumerate(value):
            bs += struct.pack('>b', tag.value)

            if index == 0:
                bs += struct.pack('>h', len(name))
                bs += name.encode('utf-8')
            else:
                bs += struct.pack('>h', 0)

            bs += __construct_attibute_values(tag, v)
    else:
        bs = struct.pack('>b', tag.value)

        bs += struct.pack('>h', len(name))
        bs += name.encode('utf-8')

        bs += __construct_attibute_values(tag, value)

    return bs


def encode_dict(data: dict) -> Any:
    version = data["version"] or DEFAULT_PROTO_VERSION
    operation = data["operation"]
    request_id = data["id"]

    encoded = struct.pack('>bb', *version)
    encoded += struct.pack('>h', operation.value)
    encoded += struct.pack('>i', request_id)

    encoded += struct.pack('>b', IppTag.OPERATION.value)

    encoded += construct_attribute('attributes-charset', CHARSET)
    encoded += construct_attribute('attributes-natural-language', CHARSET_LANGUAGE)

    if isinstance(data["operation-attributes-tag"], dict):
        for attr, value in data["operation-attributes-tag"].items():
            data += construct_attribute(attr, value)

    if isinstance(data["job-attributes-tag"], dict):
        data += struct.pack('>b', IppTag.JOB.value)

        for attr, value in data["job-attributes-tag"].items():
            data += construct_attribute(attr, value)

    if isinstance(data["printer-attributes-tag"], dict):
        data += struct.pack('>b', IppTag.PRINTER.value)

        for attr, value in data["printer-attributes-tag"].items():
            data += construct_attribute(attr, value)

    data += struct.pack('>b', IppTag.END.value)

    return encoded

def encode(
    operation: IppOperation, request_id: int, operation_attributes=None, job_attributes=None, printer_attributes=None
):
    data = struct.pack('>bb', *PROTO_VERSION)
    data += struct.pack('>h', operation.value)
    data += struct.pack('>i', request_id)

    data += struct.pack('>b', IppTag.OPERATION.value)

    data += construct_attribute('attributes-charset', CHARSET)
    data += construct_attribute('attributes-natural-language', CHARSET_LANGUAGE)

    if isinstance(operation_attributes, dict):
        for attr, value in operation_attributes.items():
            data += construct_attribute(attr, value)

    if isinstance(job_attributes, dict):
        data += struct.pack('>b', IppTag.JOB.value)

        for attr, value in job_attributes.items():
            data += construct_attribute(attr, value)

    if isinstance(printer_attributes, dict):
        data += struct.pack('>b', IppTag.PRINTER.value)

        for attr, value in printer_attributes.items():
            data += construct_attribute(attr, value)

    data += struct.pack('>b', IppTag.END.value)

    return data