from . import ReactionMenu
from discord import Message, Member, User, Colour
from typing import Dict, Union, List
from .. import lib
from ..bbConfig import bbConfig


class InlineConfirmationMenu(ReactionMenu.SingleUserReactionMenu):
    def __init__(self, msg : Message, targetMember : Union[Member, User], timeoutSeconds : int,
                    titleTxt : str = "", desc : str = "", col : Colour = Colour.blue(), footerTxt : str = "", img : str = "",
                    thumb : str = "", icon : str = "", authorName : str = ""):
        
        super().__init__(msg, targetMember, timeoutSeconds, options={bbConfig.emojis.accept: ReactionMenu.DummyReactionMenuOption("Yes", bbConfig.emojis.accept),
                                                                        bbConfig.emojis.reject: ReactionMenu.DummyReactionMenuOption("No", bbConfig.emojis.reject)},
                            returnTriggers=[bbConfig.emojis.accept, bbConfig.emojis.reject], titleTxt=titleTxt, desc=desc, col=col, footerTxt=footerTxt,
                            img=img, thumb=thumb, icon=icon, authorName=authorName)
