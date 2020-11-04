import json

def readJSON(dbFile : str) -> dict:
    """Read the json file with the given path, and return the contents as a dictionary.

    :param str dbFile: Path to the file to read
    :return: The contents of the requested json file, parsed into a python dictionary
    :rtype: dict 
    """
    f = open(dbFile, "r")
    txt = f.read()
    f.close()
    return json.loads(txt)


def writeJSON(dbFile : str, db : dict):
    """Write the given json-serializable dictionary to the given file path. All objects in the dictionary must be JSON-serializable.
    TODO: Check this makes the file if it doesnt exist

    :param str dbFile: Path to the file which db should be written to
    :param dict db: The json-serializable dictionary to write
    """
    txt = json.dumps(db)
    f = open(dbFile, "w")
    txt = f.write(txt)
    f.close()