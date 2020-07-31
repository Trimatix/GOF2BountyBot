from ..bbItem import bbItem
from ....bbConfig import bbData

class bbModule(bbItem):
    def __init__(self, name, aliases, armour=0, armourMultiplier=1.0, shield=0, shieldMultiplier=1.0, dps=0,
                    dpsMultiplier=1.0, cargo=0, cargoMultiplier=1.0, handling=0, handlingMultiplier=1.0, value=0, wiki="", manufacturer="", icon="", emoji="", techLevel=-1, builtIn=False):
        super(bbModule, self).__init__(name, aliases, value=value, wiki=wiki, manufacturer=manufacturer, icon=icon, emoji=emoji, techLevel=techLevel, builtIn=builtIn)
        self.armour = armour
        self.armourMultiplier = armourMultiplier
        self.shield = shield
        self.shieldMultiplier = shieldMultiplier
        self.dps = dps
        self.dpsMultiplier = dpsMultiplier
        self.cargo = cargo
        self.cargoMultiplier = cargoMultiplier
        self.handling = handling
        self.handlingMultiplier = handlingMultiplier

    
    def statsStringShort(self):
        stats = "*"
        if self.armour != 0:
            stats += "Armour: " + ("+" if self.armourMultiplier > 0 else "-") + str(self.armour) + ", "
        if self.armourMultiplier != 1:
            stats += "Armour: " + ("+" if self.armourMultiplier >= 1 else "-") + str(round(((self.armourMultiplier - 1) * 100) if self.armourMultiplier > 1 else (self.armourMultiplier * 100))) + "%, "
        if self.shield != 0:
            stats += "Shield: " + ("+" if self.shield > 0 else "-") + str(self.shield) + ", "
        if self.shieldMultiplier != 1:
            stats += "Shield: " + ("+" if self.shieldMultiplier >= 1 else "-") + str(round(((self.shieldMultiplier - 1) * 100) if self.shieldMultiplier > 1 else (self.shieldMultiplier * 100))) + "%, "
        if self.dps != 0:
            stats += "Dps: " + ("+" if self.dps > 0 else "-") + str(self.dps) + ", "
        if self.dpsMultiplier != 1:
            stats += "Dps: " + ("+" if self.dpsMultiplier >= 1 else "-") + str(round(((self.dpsMultiplier - 1) * 100) if self.dpsMultiplier > 1 else (self.dpsMultiplier * 100))) + "%, "
        if self.cargo != 0:
            stats += "Cargo: " + ("+" if self.cargo > 0 else "-") + str(self.cargo) + ", "
        if self.cargoMultiplier != 1:
            stats += "Cargo: " + ("+" if self.cargoMultiplier >= 1 else "-") + str(round(((self.cargoMultiplier - 1) * 100) if self.cargoMultiplier > 1 else (self.cargoMultiplier * 100))) + "%, "
        if self.handling != 0:
            stats += "Handling: " + ("+" if self.handling > 0 else "-") + str(((1 - self.handling) * 100) if self.handling > 1 else (self.handling * 100)) + ", "
        if self.handlingMultiplier != 1:
            stats += "Handling: " + ("+" if self.handlingMultiplier >= 1 else "-") + str(round(((self.handlingMultiplier - 1) * 100) if self.handlingMultiplier > 1 else (self.handlingMultiplier * 100))) + "%, "

        return (stats[:-2] + "*") if stats != "*" else "*No effect*"

    
    def getType(self):
        return bbModule

    
    def toDict(self):
        itemDict = super(bbModule, self).toDict()
        if not self.builtIn:
            if self.armour != 0.0:
                itemDict["armour"] = self.armour

            if self.armourMultiplier != 1.0:
                itemDict["armourMultiplier"] = self.armourMultiplier

            if self.shield != 0.0:
                itemDict["shield"] = self.shield

            if self.shieldMultiplier != 1.0:
                itemDict["shieldMultiplier"] = self.shieldMultiplier

            if self.dps != 0.0:
                itemDict["dps"] = self.dps

            if self.dpsMultiplier != 1.0:
                itemDict["dpsMultiplier"] = self.dpsMultiplier

            if self.cargo != 1.0:
                itemDict["cargo"] = self.cargo

            if self.cargoMultiplier != 1.0:
                itemDict["cargoMultiplier"] = self.cargoMultiplier

            if self.handling != 0:
                itemDict["handling"] = self.handling

            if self.handlingMultiplier != 1.0:
                itemDict["handlingMultiplier"] = self.handlingMultiplier

        return itemDict


def fromDict(moduleDict):
    return bbModule(moduleDict["name"], moduleDict["aliases"] if "aliases" in moduleDict else [], armour=moduleDict["armour"] if "armour" in moduleDict else 0,
                    armourMultiplier=moduleDict["armourMultiplier"] if "armourMultiplier" in moduleDict else 1, shield=moduleDict["shield"] if "shield" in moduleDict else 0,
                    shieldMultiplier=moduleDict["shieldMultiplier"] if "shieldMultiplier" in moduleDict else 1, dps=moduleDict["dps"] if "dps" in moduleDict else 0,
                    dpsMultiplier=moduleDict["dpsMultiplier"] if "dpsMultiplier" in moduleDict else 1, cargo=moduleDict["cargo"] if "cargo" in moduleDict else 0,
                    cargoMultiplier=moduleDict["cargoMultiplier"] if "cargoMultiplier" in moduleDict else 1, handling=moduleDict["handling"] if "handling" in moduleDict else 0,
                    handlingMultiplier=moduleDict["handlingMultiplier"] if "handlingMultiplier" in moduleDict else 1, value=moduleDict["value"] if "value" in moduleDict else 0,
                    wiki=moduleDict["wiki"] if "wiki" in moduleDict else "", manufacturer=moduleDict["manufacturer"] if "manufacturer" in moduleDict else "", icon=moduleDict["icon"] if "icon" in moduleDict else bbData.rocketIcon,
                    emoji=moduleDict["emoji"] if "emoji" in moduleDict else "", techLevel=moduleDict["techLevel"] if "techLevel" in moduleDict else -1, builtIn=moduleDict["builtIn"] if "builtIn" in moduleDict else False)
