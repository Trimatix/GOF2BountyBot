from ..bbConfig import bbData, bbConfig
import os
from ..shipRenderer import shipRenderer
from .. import bbUtil
from discord import File

def _saveShip(ship):
    shipData = bbData.builtInShipData[ship]
    shipTL = shipData["techLevel"]
    shipPath = shipData["path"]
    del shipData["techLevel"]
    del shipData["path"]
    shipData["builtIn"] = False
    bbUtil.writeJSON(shipPath + os.sep + "META.json", shipData, prettyPrint=True)
    shipData["builtIn"] = True
    shipData["techLevel"] = shipTL
    shipData["saveDue"] = False
    shipData["path"] = shipPath


class bbShipSkin:
    def __init__(self, name, textureRegions, shipRenders, path):
        self.name = name
        self.textureRegions = textureRegions
        self.compatibleShips = list(shipRenders.keys())
        self.shipRenders = shipRenders
        self.path = path


    def toDict(self):
        return {"name": self.name, "textureRegions": self.textureRegions, "ships": self.shipRenders}


    def _save(self):
        bbUtil.writeJSON(self.path + os.sep + "META.json", self.toDict(), prettyPrint=True)


    async def addShip(self, ship, rendersChannel):
        if ship not in bbData.builtInShipData:
            raise KeyError("Ship not found: '" + str(ship) + "'")
        
        shipData = bbData.builtInShipData[ship]

        if not shipData["skinnable"]:
            raise ValueError("Attempted to render a skin onto an non-skinnable ship: '" + str(ship) + "'")

        if ship not in self.shipRenders:
            _outputSkinFile = shipData["path"] + os.sep + "skins" + os.sep + self.name
            renderPath = _outputSkinFile + "-RENDER.png"
            # emojiRenderPath = _outputSkinFile + "_emoji-RENDER.png"
            texPath = _outputSkinFile + ".jpg"
            # emojiTexPath = _outputSkinFile + "_emoji.jpg"
            
            # if not os.path.isfile(renderPath):
            textureFiles = [self.path + os.sep + "1.jpg"]
            for i in range(self.textureRegions):
                textureFiles.append(self.path + os.sep + str(i+2) + ".jpg")
            shipRenderer.renderShip(self.name, shipData["path"], shipData["model"], textureFiles, bbConfig.skinRenderIconResolution[0], bbConfig.skinRenderIconResolution[1])
            # shipRenderer.renderShip(self.name + "_emoji", shipData["path"], shipData["model"], [texPath], bbConfig.skinRenderEmojiResolution[0], bbConfig.skinRenderEmojiResolution[1])
            # os.remove(emojiTexPath)

            # with open(emojiRenderPath, "rb") as f:
            #     newEmoji = await rendersChannel.guild.create_custom_emoji(name=ship + "_+" + self.name, image=f.read(), reason="New skin '" + self.name + "' registered for ship '" + ship + "'")

            with open(renderPath, "rb") as f:
                renderMsg = await rendersChannel.send(ship + " " + self.name, file=File(f))
                self.shipRenders[ship] = [renderMsg.attachments[0].url, renderMsg.id]#, str(newEmoji)]
            os.remove(renderPath)

        if ship not in self.compatibleShips:
            self.compatibleShips.append(ship)
            
        if self.name not in shipData["compatibleSkins"]:
            shipData["compatibleSkins"].append(self.name.lower())

        _saveShip(ship)
        self._save()

    
    async def removeShip(self, ship, rendersChannel):
        if ship not in bbData.builtInShipData:
            raise KeyError("Ship not found: '" + str(ship) + "'")
        
        shipData = bbData.builtInShipData[ship]

        if ship in self.compatibleShips:
            self.compatibleShips.remove(ship)
        
        if self.name in shipData["compatibleSkins"]:
            try:
                os.remove(shipData["path"] + os.sep + "skins" + os.sep + self.name + ".png")
            except FileNotFoundError:
                pass
            shipData["compatibleSkins"].remove(self.name.lower())

        if ship in self.shipRenders:
            # renderMsg = await rendersChannel.fetch_message(self.shipRenders[ship][1])
            # await renderMsg.delete()
            del self.shipRenders[ship]

        _saveShip(ship)
        self._save()


def fromDict(skinDict):
    if skinDict["name"] in bbData.builtInShipSkins:
        return bbData.builtInShipSkins[skinDict["name"]]
    return bbShipSkin(skinDict["name"], skinDict["textureRegions"], skinDict["ships"], skinDict["path"])
