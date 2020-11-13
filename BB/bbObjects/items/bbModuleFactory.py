from ...bbConfig import bbData
from .modules import bbModule, bbArmourModule, bbBoosterModule, bbCabinModule, bbCloakModule, bbCompressorModule, bbGammaShieldModule, bbMiningDrillModule, bbRepairBeamModule, bbRepairBotModule, bbScannerModule, bbShieldModule, bbSpectralFilterModule, bbThrusterModule, bbTractorBeamModule, bbTransfusionBeamModule, bbWeaponModModule, bbJumpDriveModule, bbEmergencySystemModule, bbSignatureModule, bbShieldInjectorModule, bbTimeExtenderModule
from ... import lib

typeConstructors = {"armour": bbArmourModule.fromDict,
                    "booster": bbBoosterModule.fromDict,
                    "cabin": bbCabinModule.fromDict,
                    "cloak": bbCloakModule.fromDict,
                    "compressor": bbCompressorModule.fromDict,
                    "gamma shield": bbGammaShieldModule.fromDict,
                    "mining drill": bbMiningDrillModule.fromDict,
                    "repair beam": bbRepairBeamModule.fromDict,
                    "repair bot": bbRepairBotModule.fromDict,
                    "scanner": bbScannerModule.fromDict,
                    "shield": bbShieldModule.fromDict,
                    "spectral filter": bbSpectralFilterModule.fromDict,
                    "thruster": bbThrusterModule.fromDict,
                    "tractor beam": bbTractorBeamModule.fromDict,
                    "transfusion beam": bbTransfusionBeamModule.fromDict,
                    "weapon mod": bbWeaponModModule.fromDict,
                    "jump drive": bbJumpDriveModule.fromDict,
                    "emergency system": bbEmergencySystemModule.fromDict,
                    "signature": bbSignatureModule.fromDict,
                    "shield injector": bbShieldInjectorModule.fromDict,
                    "time extender": bbTimeExtenderModule.fromDict}


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
                            bbWeaponModModule.bbWeaponModModule: 1,
                            bbJumpDriveModule.bbJumpDriveModule: 0,
                            bbEmergencySystemModule.bbEmergencySystemModule: 1,
                            bbSignatureModule.bbSignatureModule: 1,
                            bbShieldInjectorModule.bbShieldInjectorModule: 1,
                            bbTimeExtenderModule.bbTimeExtenderModule: 1}


def fromDict(moduleDict):
    """Factory function recreating any bbModule or bbModule subtype from a dictionary-serialized representation.
    If implemented correctly, this should act as the opposite to the original object's toDict method.
    If the requested module is builtIn, return the builtIn module object of the same name.

    :param dict moduleDict: A dictionary containg all information necessary to create the desired bbModule object
    :return: The bbModule object described in moduleDict
    :rtype: bbModule
    """
    if "builtIn" in moduleDict and moduleDict["builtIn"]:
        return bbData.builtInModuleObjs[moduleDict["name"]]
    else:
        if "type" in moduleDict and moduleDict["type"] in typeConstructors:
            return typeConstructors[moduleDict["type"]](moduleDict)
        else:
            return bbModule.fromDict(moduleDict)