import json
from ..bbDatabases import bbUserDB, bbGuildDB, bbBountyDB, reactionMenuDB
from ..bbConfig import bbConfig


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


def loadUsersDB(filePath : str) -> bbUserDB.bbUserDB:
    """Build a bbUserDB from the specified JSON file.

    :param str filePath: path to the JSON file to load. Theoretically, this can be absolute or relative.
    :return: a bbUserDB as described by the dictionary-serialized representation stored in the file located in filePath.
    """
    return bbUserDB.fromDict(readJSON(filePath))


def loadGuildsDB(filePath : str) -> bbGuildDB.bbGuildDB:
    """Build a bbGuildDB from the specified JSON file.

    :param str filePath: path to the JSON file to load. Theoretically, this can be absolute or relative.
    :return: a bbGuildDB as described by the dictionary-serialized representation stored in the file located in filePath.
    """
    return bbGuildDB.fromDict(readJSON(filePath))


def loadBountiesDB(filePath : str) -> bbBountyDB.bbBountyDB:
    """Build a bbBountyDB from the specified JSON file.

    :param str filePath: path to the JSON file to load. Theoretically, this can be absolute or relative.
    :return: a bbBountyDB as described by the dictionary-serialized representation stored in the file located in filePath.
    """
    return bbBountyDB.fromDict(readJSON(filePath), bbConfig.maxBountiesPerFaction, dbReload=True)


async def loadReactionMenusDB(filePath : str) -> reactionMenuDB.reactionMenuDB:
    """Build a reactionMenuDB from the specified JSON file.
    This method must be called asynchronously, to allow awaiting of discord message fetching functions.

    :param str filePath: path to the JSON file to load. Theoretically, this can be absolute or relative.
    :return: a reactionMenuDB as described by the dictionary-serialized representation stored in the file located in filePath.
    """
    return await reactionMenuDB.fromDict(readJSON(filePath))


def saveDB(dbPath : str, db):
    """Call the given database object's toDict method, and save the resulting dictionary to the specified JSON file.
    TODO: child database classes to a single ABC, and type check to that ABC here before saving

    :param str dbPath: path to the JSON file to save to. Theoretically, this can be absolute or relative.
    :param db: the database object to save
    """
    writeJSON(dbPath, db.toDict())


async def saveDBAsync(dbPath : str, db):
    """This function should be used in place of saveDB for database objects whose toDict method is asynchronous.
    This function is currently unused.

    Await the given database object's toDict method, and save the resulting dictionary to the specified JSON file.
    TODO: child database classes to a single ABC, and type check to that ABC here before saving

    :param str dbPath: path to the JSON file to save to. Theoretically, this can be absolute or relative.
    :param db: the database object to save
    """
    writeJSON(dbPath, await db.toDict())