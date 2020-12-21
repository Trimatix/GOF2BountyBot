from . import ReactionMenu
from discord import Message, Member, User, Colour
from typing import Dict, Union, List
from .. import lib
from ..bbConfig import bbConfig


class InlineConfirmationMenu(ReactionMenu.InlineReactionMenu):
    def __init__(self, msg : Message, targetMember : Union[Member, User], timeoutSeconds : int,
                    titleTxt : str = "", desc : str = "", col : Colour = Colour.blue(), footerTxt : str = "", img : str = "",
                    thumb : str = "", icon : str = "", authorName : str = ""):
        
        super().__init__(msg, targetMember, timeoutSeconds, options={bbConfig.defaultAcceptEmoji: ReactionMenu.DummyReactionMenuOption("Yes", bbConfig.defaultAcceptEmoji),
                                                                        bbConfig.defaultRejectEmoji: ReactionMenu.DummyReactionMenuOption("No", bbConfig.defaultRejectEmoji)},
                            returnTriggers=[bbConfig.defaultAcceptEmoji, bbConfig.defaultRejectEmoji], titleTxt=titleTxt, desc=desc, col=col, footerTxt=footerTxt,
                            img=img, thumb=thumb, icon=icon, authorName=authorName)
