from ...bbConfig import bbData
from .modules import bbModule, bbArmourModule, bbBoosterModule, bbCabinModule, bbCloakModule, bbCompressorModule, bbGammaShieldModule, bbMiningDrillModule, bbRepairBeamModule, bbRepairBotModule, bbScannerModule, bbShieldModule, bbSpectralFilterModule, bbThrusterModule, bbTractorBeamModule, bbTransfusionBeamModule, bbWeaponModModule, bbJumpDriveModule, bbEmergencySystemModule, bbSignatureModule, bbShieldInjectorModule, bbTimeExtenderModule

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


def fromDict(moduleDict):
    if "builtIn" in moduleDict and moduleDict["builtIn"]:
        return bbData.builtInModuleObjs[moduleDict["name"]]
    else:
        if "type" in moduleDict and moduleDict["type"] in typeConstructors:
            return typeConstructors[moduleDict["type"]](moduleDict)
        else:
            return bbModule.fromDict(moduleDict)