class bbShipUpgrade:
    name = ""
    value = 0
    applied = False

    armour = 0.0
    armourMultiplier = 1.0

    cargo = 0
    cargoMultiplier = 1.0

    numSecondaries = 0
    numSecondariesMultiplier = 1.0

    handling = 0
    handlingMultiplier = 1.0

    maxPrimaries = 0
    maxPrimariesMultiplier = 1.0
    
    maxTurrets = 0
    maxTurretsMultiplier = 1.0

    maxModules = 0
    maxModulesMultiplier = 1.0

    
    def __init__(self, name, value,
                    armour=0.0, armourMultiplier=1.0, cargo=0, cargoMultiplier=1.0, numSecondaries=0, numSecondariesMultiplier=1.0,
                    handling=0, handlingMultiplier=1.0, maxPrimaries=0, maxPrimariesMultiplier=1.0, maxTurrets=0, maxTurretsMultiplier=1.0,
                    maxModules=0, maxModulesMultiplier=1.0):
        self.name = name
        self.value = value

        self.armour = armour
        self.armourMultiplier = armourMultiplier

        self.cargo = cargo
        self.cargoMultiplier = cargoMultiplier

        self.numSecondaries = numSecondaries
        self.numSecondariesMultiplier = numSecondariesMultiplier

        self.handling = handling
        self.handlingMultiplier = handlingMultiplier

        self.maxPrimaries = maxPrimaries
        self.maxPrimariesMultiplier = maxPrimariesMultiplier
        
        self.maxTurrets = maxTurrets
        self.maxTurretsMultiplier = maxTurretsMultiplier

        self.maxModules = maxModules
        self.maxModulesMultiplier = maxModulesMultiplier



    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name