from ...bbConfig import bbData
from .modules import moduleItem, bbArmourModule, bbBoosterModule, bbCabinModule, bbCloakModule, bbCompressorModule, bbGammaShieldModule, bbMiningDrillModule, bbRepairBeamModule, bbRepairBotModule, bbScannerModule, bbShieldModule, bbSpectralFilterModule, bbThrusterModule, bbTractorBeamModule, bbTransfusionBeamModule, primaryWeaponModModule, bbJumpDriveModule, bbEmergencySystemModule, bbSignatureModule, bbShieldInjectorModule, bbTimeExtenderModule

typeConstructors = {"armour": bbArmourModule.bbArmourModule.fromDict,
                    "booster": bbBoosterModule.bbBoosterModule.fromDict,
                    "cabin": bbCabinModule.bbCabinModule.fromDict,
                    "cloak": bbCloakModule.bbCloakModule.fromDict,
                    "compressor": bbCompressorModule.bbCompressorModule.fromDict,
                    "gamma shield": bbGammaShieldModule.bbGammaShieldModule.fromDict,
                    "mining drill": bbMiningDrillModule.bbMiningDrillModule.fromDict,
                    "repair beam": bbRepairBeamModule.bbRepairBeamModule.fromDict,
                    "repair bot": bbRepairBotModule.bbRepairBotModule.fromDict,
                    "scanner": bbScannerModule.bbScannerModule.fromDict,
                    "shield": bbShieldModule.bbShieldModule.fromDict,
                    "spectral filter": bbSpectralFilterModule.bbSpectralFilterModule.fromDict,
                    "thruster": bbThrusterModule.bbThrusterModule.fromDict,
                    "tractor beam": bbTractorBeamModule.bbTractorBeamModule.fromDict,
                    "transfusion beam": bbTransfusionBeamModule.bbTransfusionBeamModule.fromDict,
                    "weapon mod": primaryWeaponModModule.PrimaryWeaponModModule.fromDict,
                    "jump drive": bbJumpDriveModule.bbJumpDriveModule.fromDict,
                    "emergency system": bbEmergencySystemModule.bbEmergencySystemModule.fromDict,
                    "signature": bbSignatureModule.bbSignatureModule.fromDict,
                    "shield injector": bbShieldInjectorModule.bbShieldInjectorModule.fromDict,
                    "time extender": bbTimeExtenderModule.bbTimeExtenderModule.fromDict}


# the max number of each module type that can be equipped on a ship.
# TODO: This should probably be moved elsewhere, e.g bbConfig
maxModuleTypeEquips = {     bbArmourModule.bbArmourModule: 1,
                            bbBoosterModule.bbBoosterModule: 1,
                            bbCabinModule.bbCabinModule: -1,
                            bbCloakModule.bbCloakModule: 1,
                            bbCompressorModule.bbCompressorModule: -1,
                            bbGammaShieldModule.bbGammaShieldModule: 1,
                            bbMiningDrillModule.bbMiningDrillModule: 1,
                            bbRepairBeamModule.bbRepairBeamModule: 1,
                            bbRepairBotModule.bbRepairBotModule: 1,
                            bbScannerModule.bbScannerModule: 1,
                            bbShieldModule.bbShieldModule: 1,
                            bbSpectralFilterModule.bbSpectralFilterModule: 1,
                            bbThrusterModule.bbThrusterModule: 1,
                            bbTractorBeamModule.bbTractorBeamModule: 1,
                            bbTransfusionBeamModule.bbTransfusionBeamModule: 1,
                            primaryWeaponModModule.PrimaryWeaponModModule: 1,
                            bbJumpDriveModule.bbJumpDriveModule: 0,
                            bbEmergencySystemModule.bbEmergencySystemModule: 1,
                            bbSignatureModule.bbSignatureModule: 1,
                            bbShieldInjectorModule.bbShieldInjectorModule: 1,
                            bbTimeExtenderModule.bbTimeExtenderModule: 1}


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