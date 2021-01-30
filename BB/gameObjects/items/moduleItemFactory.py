from ...bbConfig import bbData
from .modules import moduleItem, armourModule, boosterModule, cabinModule, cloakModule, compressorModule, gammaShieldModule, miningDrillModule, repairBeamModule, repairBotModule, scannerModule, shieldModule, spectralFilterModule, thrusterModule, tractorBeamModule, transfusionBeamModule, primaryWeaponModModule, jumpDriveModule, emergencySystemModule, signatureModule, shieldInjectorModule, timeExtenderModule

typeConstructors = {"armour": armourModule.ArmourModule.fromDict,
                    "booster": boosterModule.BoosterModule.fromDict,
                    "cabin": cabinModule.CabinModule.fromDict,
                    "cloak": cloakModule.CloakModule.fromDict,
                    "compressor": compressorModule.CompressorModule.fromDict,
                    "gamma shield": gammaShieldModule.GammaShieldModule.fromDict,
                    "mining drill": miningDrillModule.MiningDrillModule.fromDict,
                    "repair beam": repairBeamModule.RepairBeamModule.fromDict,
                    "repair bot": repairBotModule.RepairBotModule.fromDict,
                    "scanner": scannerModule.ScannerModule.fromDict,
                    "shield": shieldModule.ShieldModule.fromDict,
                    "spectral filter": spectralFilterModule.SpectralFilterModule.fromDict,
                    "thruster": thrusterModule.ThrusterModule.fromDict,
                    "tractor beam": tractorBeamModule.TractorBeamModule.fromDict,
                    "transfusion beam": transfusionBeamModule.TransfusionBeamModule.fromDict,
                    "weapon mod": primaryWeaponModModule.PrimaryWeaponModModule.fromDict,
                    "jump drive": jumpDriveModule.JumpDriveModule.fromDict,
                    "emergency system": emergencySystemModule.EmergencySystemModule.fromDict,
                    "signature": signatureModule.SignatureModule.fromDict,
                    "shield injector": shieldInjectorModule.ShieldInjectorModule.fromDict,
                    "time extender": timeExtenderModule.TimeExtenderModule.fromDict}


# the max number of each module type that can be equipped on a ship.
# TODO: This should probably be moved elsewhere, e.g bbConfig
maxModuleTypeEquips = {     armourModule.ArmourModule: 1,
                            boosterModule.BoosterModule: 1,
                            cabinModule.CabinModule: -1,
                            cloakModule.CloakModule: 1,
                            compressorModule.CompressorModule: -1,
                            gammaShieldModule.GammaShieldModule: 1,
                            miningDrillModule.MiningDrillModule: 1,
                            repairBeamModule.RepairBeamModule: 1,
                            repairBotModule.RepairBotModule: 1,
                            scannerModule.ScannerModule: 1,
                            shieldModule.ShieldModule: 1,
                            spectralFilterModule.SpectralFilterModule: 1,
                            thrusterModule.ThrusterModule: 1,
                            tractorBeamModule.TractorBeamModule: 1,
                            transfusionBeamModule.TransfusionBeamModule: 1,
                            primaryWeaponModModule.PrimaryWeaponModModule: 1,
                            jumpDriveModule.JumpDriveModule: 0,
                            emergencySystemModule.EmergencySystemModule: 1,
                            signatureModule.SignatureModule: 1,
                            shieldInjectorModule.ShieldInjectorModule: 1,
                            timeExtenderModule.TimeExtenderModule: 1}


def fromDict(moduleDict):
    """Factory function recreating any moduleItem or moduleItem subtype from a dictionary-serialized representation.
    If implemented correctly, this should act as the opposite to the original object's toDict method.
    If the requested module is builtIn, return the builtIn module object of the same name.

    :param dict moduleDict: A dictionary containg all information necessary to create the desired moduleItem object
    :return: The moduleItem object described in moduleDict
    :rtype: moduleItem
    """
    if "builtIn" in moduleDict and moduleDict["builtIn"]:
        return bbData.builtInModuleObjs[moduleDict["name"]]
    else:
        if "type" in moduleDict and moduleDict["type"] in typeConstructors:
            return typeConstructors[moduleDict["type"]](moduleDict)
        else:
            return moduleItem.ModuleItem.fromDict(moduleDict)