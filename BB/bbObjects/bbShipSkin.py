from ..bbConfig import bbData, bbConfig
import os
from ..shipRenderer import shipRenderer
from .. import lib
from discord import File
from typing import Dict, List
from ..baseClasses import bbSerializable


def _saveShip(ship):
    shipData = bbData.builtInShipData[ship]
    shipTL = shipData["techLevel"]
    shipPath = shipData["path"]
    del shipData["techLevel"]
    del shipData["path"]
    shipData["builtIn"] = False
    lib.jsonHandler.writeJSON(shipPath + os.sep + "META.json", shipData, prettyPrint=True)
    shipData["builtIn"] = True
    shipData["techLevel"] = shipTL
    shipData["saveDue"] = False
    shipData["path"] = shipPath


class bbShipSkin(bbSerializable.bbSerializable):
    def __init__(self, name : str, textureRegions : List[int], shipRenders : Dict[str, str], path : str, designer : str, wiki : str = "", disabledRegions : List[int] = []):
        self.name = name
        self.textureRegions = textureRegions
        self.compatibleShips = list(shipRenders.keys())
        self.shipRenders = shipRenders
        self.path = path
        if len(self.compatibleShips) > 0:
            self.averageTL = 0
            for ship in self.compatibleShips:
                self.averageTL += bbData.builtInShipData[ship]["techLevel"]
            self.averageTL = int(self.averageTL / len(self.compatibleShips))
        else:
            self.averageTL = -1
        self.designer = designer
        self.wiki = wiki
        self.hasWiki = wiki != ""
        self.disabledRegions = disabledRegions
        for region in disabledRegions:
            if region < 1:
                raise ValueError("Attempted to disable an invalid region number: " + str(region) + ", skin " + name)


    def toDict(self, **kwargs) -> dict:
        data = {"name": self.name, "textureRegions": self.textureRegions, "ships": self.shipRenders, "designer": self.designer}
        if self.hasWiki:
            data["wiki"] = self.wiki
        if self.disabledRegions:
            data["disabledRegions"] = self.disabledRegions
        return data


    def _save(self, **kwargs):
        lib.jsonHandler.writeJSON(self.path + os.sep + "META.json", self.toDict(**kwargs), prettyPrint=True)


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
            textureFiles = {0: self.path + os.sep + "1.jpg"}
            for textureNum in self.textureRegions:
                if textureNum <= shipData["textureRegions"]:
                    textureFiles[textureNum] = self.path + os.sep + str(textureNum + 1) + ".jpg"
            
            regionsToDisable = []
            if "textureRegions" in shipData and shipData["textureRegions"] > 0:
                for disabledRegionNum in self.disabledRegions:
                    if disabledRegionNum <= shipData["textureRegions"]:
                        regionsToDisable.append(disabledRegionNum)

            await shipRenderer.renderShip(self.name, shipData["path"], shipData["model"], textureFiles, regionsToDisable, bbConfig.skinRenderIconResolution[0], bbConfig.skinRenderIconResolution[1])
            # await shipRenderer.renderShip(self.name + "_emoji", shipData["path"], shipData["model"], [texPath], bbConfig.skinRenderEmojiResolution[0], bbConfig.skinRenderEmojiResolution[1])
            # os.remove(emojiTexPath)

            # with open(emojiRenderPath, "rb") as f:
            #     newEmoji = await rendersChannel.guild.create_custom_emoji(name=ship + "_+" + self.name, image=f.read(), reason="New skin '" + self.name + "' registered for ship '" + ship + "'")

            with open(renderPath, "rb") as f:
                renderMsg = await rendersChannel.send(ship + " +" + self.name, file=File(f))
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


    @classmethod
    def fromDict(cls, skinDict, **kwargs):
        if skinDict["name"] in bbData.builtInShipSkins:
            return bbData.builtInShipSkins[skinDict["name"]]
        return bbShipSkin(skinDict["name"], skinDict["textureRegions"], skinDict["ships"], skinDict["path"], skinDict["designer"], skinDict["wiki"] if "wiki" in skinDict else "",
                            disabledRegions=skinDict["disabledRegions"] if "disabledRegions" in skinDict else [])
