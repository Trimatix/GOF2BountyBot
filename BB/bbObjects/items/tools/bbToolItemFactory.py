from . import bbToolItem, bbShipSkinTool, bbCrate


def fromDict(toolDict : dict) -> bbToolItem.bbToolItem:
    """Construct a bbToolItem from its dictionary-serialized representation.
    This method decodes which tool constructor is appropriate based on the 'type' attribute of the given dictionary.

    :param dict toolDict: A dictionary containing all information needed to construct the required bbToolItem. Critically, a name, type, and builtIn specifier.
    :return: A new bbToolItem object as described in toolDict
    :rtype: bbToolItem.bbToolItem
    :raise NameError: When toolDict does not contain a 'type' attribute.
    """

    toolTypeConstructors = {"bbShipSkinTool": bbShipSkinTool.bbShipSkinTool.fromDict,
                        "bbCrate": bbCrate.bbCrate.fromDict}
    
    if "type" not in toolDict:
        raise NameError("Required dictionary attribute missing: 'type'")
    return toolTypeConstructors[toolDict["type"]](toolDict)
