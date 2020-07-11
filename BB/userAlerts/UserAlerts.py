class UserAlert:
    def __init__(self, state):
        self.state = state


# class UA_Shop_Refresh(UserAlert):
#     def __init__(self, state):
#         super(UA_Shop_Refresh, self).__init__(state)


class UA_Duels_Challenge_Incoming_New(UserAlert):
    def __init__(self, state):
        super(UA_Duels_Challenge_Incoming_New, self).__init__(state)

class UA_Duels_Challenge_Incoming_Cancel(UserAlert):
    def __init__(self, state):
        super(UA_Duels_Challenge_Incoming_Cancel, self).__init__(state)


class UA_System_Updates_Major(UserAlert):
    def __init__(self, state):
        super(UA_System_Updates_Major, self).__init__(state)

class UA_System_Updates_Minor(UserAlert):
    def __init__(self, state):
        super(UA_System_Updates_Minor, self).__init__(state)

class UA_System_Misc(UserAlert):
    def __init__(self, state):
        super(UA_System_Misc, self).__init__(state)


userAlertsIDsTypes = {  #"shop_refresh": UA_Shop_Refresh,

                        "duels_challenge_incoming_new": UA_Duels_Challenge_Incoming_New,
                        "duels_challenge_incoming_cancel": UA_Duels_Challenge_Incoming_Cancel,
                        
                        "system_updates_major": UA_System_Updates_Major,
                        "system_updates_minor": UA_System_Updates_Minor,
                        "system_misc": UA_System_Misc}

userAlertsTypesIDs = {  #UA_Shop_Refresh: "shop_refresh",

                        UA_Duels_Challenge_Incoming_New: "duels_challenge_incoming_new",
                        UA_Duels_Challenge_Incoming_Cancel: "duels_challenge_incoming_cancel",
                        
                        UA_System_Updates_Major: "system_updates_major",
                        UA_System_Updates_Minor: "system_updates_minor",
                        UA_System_Misc: "system_misc"}

userAlertsTypesNames = {#UA_Shop_Refresh: "new shop stock",

                        UA_Duels_Challenge_Incoming_New: "new duel challenges",
                        UA_Duels_Challenge_Incoming_Cancel: "cancelled duel challenges",
                        
                        UA_System_Updates_Major: "BountyBot major updates",
                        UA_System_Updates_Minor: "BountyBot minor updates",
                        UA_System_Misc: "BountyBot misc. announcements"}