from .import bbSerializable

typeConstructors = {}

def fromDict(data : dict) -> bbSerializable.bbSerializable:
    if "type" not in data or data["type"] == "":
        raise NameError("Not given a type")
    elif data["type"] not in typeConstructors:
        raise KeyError("Unrecognised item type: " + str(data["type"]))