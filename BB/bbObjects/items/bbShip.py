from .. import bbAliasable

class bbShip(bbAliasable.Aliasable):
    armour = 0.0
    cargo = 0
    numSecondaries = 0
    handling = 0
    value = 0

    maxPrimaries = 0
    maxTurrets = 0
    maxModules = 0

    weapons = []
    modules = []
    turrets = []

    def __init__(self, name, maxPrimaries, maxTurrets, maxModules, armour=0.0, cargo=0, numSecondaries=0, handling=0, value=0, aliases=[], weapons=[], modules=[], turrets=[]):
        super(bbShip, self).__init__(name, aliases)

        if len(weapons) > maxPrimaries:
            ValueError("passed more weapons than can be stored on this ship - maxPrimaries")
        if len(modules) > maxModules:
            ValueError("passed more modules than can be stored on this ship - maxModules")
        if len(turrets) > maxTurrets:
            ValueError("passed more turrets than can be stored on this ship - maxTurrets")

        self.name = name
        self.maxPrimaries = maxPrimaries
        self.maxTurrets = maxTurrets
        self.maxModules = maxModules
        self.armour = armour
        self.cargo = cargo
        self.numSecondaries = numSecondaries
        self.handling = handling
        self.value = value


    def getNumWeaponsEquipped(self):
        return len(self.weapons)


    def canEquipMoreWeapons(self):
        return self.getNumWeaponsEquipped() < self.maxPrimaries

    
    def getNumModulesEquipped(self):
        return len(self.modules)


    def canEquipMoreModules(self):
        return self.getNumModulesEquipped() < self.maxModules

    
    def getNumTurretsEquipped(self):
        return len(self.turrets)


    def canEquipMoreTurrets(self):
        return self.getNumTurretsEquipped() < self.maxTurrets


    def equipWeapon(self, weapon):
        if not self.canEquipMoreWeapons():
            raise OverflowError("Attempted to equip a weapon but all weapon slots are full")
        self.weapons.append(weapon)
    

    def unequipWeaponObj(self, weapon):
        self.weapons.remove(weapon)


    def unequipWeaponIndex(self, index):
        self.weapons.pop(index)


    def getWeaponAtIndex(self, index):
        return self.weapons[index]


    def equipModule(self, module):
        if not self.canEquipMoreModules():
            raise OverflowError("Attempted to equip a module but all module slots are full")
        self.modules.append(module)
    

    def unequipModuleObj(self, module):
        self.modules.remove(module)


    def unequipModuleIndex(self, index):
        self.modules.pop(index)


    def getModuleAtIndex(self, index):
        return self.modules[index]


    def equipTurret(self, turret):
        if not self.canEquipMoreTurrets():
            raise OverflowError("Attempted to equip a turret but all turret slots are full")
        self.turrets.append(turret)
    

    def unequipTurretObj(self, turret):
        self.turrets.remove(turret)


    def unequipTurretIndex(self, index):
        self.turrets.pop(index)


    def getTurretAtIndex(self, index):
        return self.turrets[index]
