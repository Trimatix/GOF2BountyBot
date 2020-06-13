# Shame, but i'd rather this than keep factionColours in bountybot.py
from discord import Colour

# all factions recognised by BB
factions = ["terran", "vossk", "midorian", "nivelian", "neutral"]
# all factions useable in bounties
bountyFactions = ["terran", "vossk", "midorian", "nivelian"]

# names of criminals in builtIn bounties
bountyNames = {"terran": ["Pal Tyyrt", "Kehnor", "Gendol Ethor", "Korr Bekkt", "Hongar Meton"],
                "vossk": ["Mrrkt Nimkk", "Alvar Julen", "Vortt Baskk", "Oluchi Erland", "Orp Tsam"],
                "midorian": ["Toma Prakupy", "Nombur Telénah", "Bartholomeu Drew", "Doni Trillyx", "Mashon Redal"],
                "nivelian": ["Borsul Tarand", "Vilhelm Lindon", "Tamir Prakupy", "Merson Surr", "Ganfor Kant"]}

# icons for builtIn criminals
bountyIcons = { # Terran
                "Pal Tyyrt": "https://cdn.discordapp.com/attachments/700683544103747594/711226618919780359/pal_tyyrt.png",
                "Kehnor": "https://cdn.discordapp.com/attachments/700683544103747594/711226614767419432/kehnor.png",
                "Gendol Ethor": "https://cdn.discordapp.com/attachments/700683544103747594/711226611608977490/gendol_ethor.png",
                "Korr Bekkt": "https://cdn.discordapp.com/attachments/700683544103747594/711226617254510602/korr_bekkt.png",
                "Hongar Meton": "https://cdn.discordapp.com/attachments/700683544103747594/711226613278441543/hongar_meton.png",
                "Trent Jameson": "https://cdn.discordapp.com/attachments/700683544103747594/711226622195269632/trent_jameson.png",
                "Qyrr Myfft": "https://cdn.discordapp.com/attachments/700683544103747594/711226620786114590/qyrr_myfft.png",

                # Midorian
                "Toma Prakupy": "https://cdn.discordapp.com/attachments/700683544103747594/711226704953344060/toma_prakupy.png",
                "Nombur Telénah": "https://cdn.discordapp.com/attachments/700683544103747594/711226703703310397/nombur_talenah.png",
                "Bartholomeu Drew": "https://cdn.discordapp.com/attachments/700683544103747594/711226697974022204/bartholomeu_drew.png",
                "Doni Trillyx": "https://cdn.discordapp.com/attachments/700683544103747594/711226699119067217/doni_trillyx.png",
                "Heinrich Wickel": "https://cdn.discordapp.com/attachments/700683544103747594/711226700305793085/heinrich_wickel.png",
                "Mashon Redal": "https://cdn.discordapp.com/attachments/700683544103747594/711226702122057768/mashon_redal.png",

                # Vossk
                "Mrrkt Nimkk": "https://cdn.discordapp.com/attachments/700683544103747594/711226820854284368/mrrkt_minkk.png",
                "Alvar Julen": "https://cdn.discordapp.com/attachments/700683544103747594/711226819461775360/alvar_julen.png",
                "Vortt Baskk": "https://cdn.discordapp.com/attachments/700683544103747594/711226826831298710/vortt_baskk.png",
                "Oluchi Erland": "https://cdn.discordapp.com/attachments/700683544103747594/711226822540394546/oluchi_erland.png",
                "Orp Tsam": "https://cdn.discordapp.com/attachments/700683544103747594/711226823966720041/orp_tsam.png",
                "Urr Sekant": "https://cdn.discordapp.com/attachments/700683544103747594/711226825488990258/urr_sakant.png",

                # Nivelian
                "Borsul Tarand": "https://cdn.discordapp.com/attachments/700683544103747594/711226764948537374/borsul_tarand.png",
                "Malon Sentendar": "https://cdn.discordapp.com/attachments/700683544103747594/711226767939207178/malon_sentendar.png",
                "Vilhelm Lindon": "https://cdn.discordapp.com/attachments/700683544103747594/711226772812726302/vilhelm_lindon.png",
                "Tamir Prakupy": "https://cdn.discordapp.com/attachments/700683544103747594/711226770707185664/tamir_prakupy.png",
                "Merson Surr": "https://cdn.discordapp.com/attachments/700683544103747594/711226769327521872/merson_surr.png",
                "Ganfor Kant": "https://cdn.discordapp.com/attachments/700683544103747594/711226766630584370/ganfor_kant.png"}

# find the length of the longest criminal name, to be used in padding during $COMMANDPREFIX$bounties
longestBountyNameLength = 0
for fac in bountyNames:
    for name in bountyNames[fac]:
        if len(name) > longestBountyNameLength:
            longestBountyNameLength = len(name)

# levels of security in bbSystems (bbSystem security is stored as an index in this list)
securityLevels = ["secure", "average", "risky", "dangerous"]

# map image URLS for $COMMANDPREFIX$map
mapImageWithGraphLink = "https://cdn.discordapp.com/attachments/700683544103747594/700683693215318076/gof2_coords.png"
mapImageNoGraphLink = 'https://cdn.discordapp.com/attachments/700683544103747594/700683699334807612/Gof2_supernova_map.png'

# intro for help commands
helpIntro = """:star: Here are my commands! Prefix commands with `$COMMANDPREFIX$` - for example: `$COMMANDPREFIX$help 2`
**<Angled brackets>** indicate *optional* arguments, **[square brackets]** indicate *required* arguments."""

# help strings for bb commands
helpDict = {"Miscellaneous":{"help": ("**help** *<command>*", "Display information about the requested command. If no command is given, all available commands are displayed."),
                            "balance": ("**balance** *<userTag>*", "Get the credits balance of yourself, or a tagged user if one is given."),
                            "stats": ("**stats** *<userTag>*", "Get various credits and bounty statistics about yourself, or a tagged user."),
                            "leaderboard": ("**leaderboard** *<-g|-c|-s|-w>*", "Show the credits leaderboard. Give `-g` for the global leaderboard, not just this server.\n> Give `-c` for the current credits balance leaderboard.\n> Give `-s` for the 'systems checked' leaderboard.\n> Give `-w` for the 'bounties won' leaderboard.\nE.g: `$COMMANDPREFIX$leaderboard -gs`"),
                            "pay": ("**pay [user] [amount]**", "Pay the mentioned user an amount of credits from your balance."),
                            "notify": ("**notify [type]** *<item>*", "Subscribe to pings when events take place. Currently, only `$notify bounties` is implemented, which will notify you when new bounties are available.")},
            
            "GOF2 Info":{   "map": ("**map**","Send the complete GOF2 starmap."),
                            "info": ("**info [object-type] [name]**", "Display information about something. object-type must be criminal, system, ship, weapon, module, turret, or turret. Also gives the usable aliases for an object."),
                            "make-route": ("**make-route [startSystem], [endSystem]**", "Find the shortest route from startSystem to endSystem.")},
            
            "Bounties":{    "bounties": ("**bounties** *<faction>*", "If no faction is given, name all currently active bounties.\nIf a faction is given, show detailed info about its active bounties."),
                            "route": ("**route [criminal name]**", "Get the named criminal's current route."),
                            "check": ("**check [system]**", "Check if any criminals are in the given system, arrest them, and get paid! 💰")},
            
            "Items":{       "hangar": ("**hangar** *<item-type>*", "Display the items in your hangar. Give an item type (ship/weapon/turret/module) to only list items of that type."),
                            "shop": ("**shop** *<item-type>*", "Display all items currently for sale. Shop stock is refreshed daily. Give an item type (ship/weapon/turret/module) to only list items of that type."),
                            "loadout": ("**loadout**", "Display your current ship and the items equipped onto it."),
                            "buy": ("**buy [item-type] [item-number]** *<transfer> <sell>*", "Buy the requested item from the shop. Item numbers can be gotten from `$COMMANDPREFIX$shop`. When buying a ship, specify `sell` to sell your active ship, and/or `transfer` to move your active items to the new ship."),
                            "sell": ("**sell [item-type] [item-number]** *<clear>*", "Sell the requested item from your hangar to the shop. Item numbers can be gotten from `$COMMANDPREFIX$hangar`. When selling a ship, specify `clear` to first remove all items from the ship."),
                            "equip": ("**equip [item-type] [item-num]** *<transfer>*", "Equip the requested item from your hangar onto your active ship. Item numbers can be gotten from `$COMMANDPREFIX$hanger`. When equipping a ship, specify `transfer` to move all items to the new ship."),
                            "unequip": ("**unequip [item-type] [item-num]**", "Unequip the requested item from your active ship, into your hanger. Item numbers can be gotten from `$COMMANDPREFIX$loadout`."),
                            "nameShip": ("**nameShip [nickname]**", "Give your active ship a nickname!"),
                            "unnameShip": ("**unnameShip**", "Reset your active ship's nickname.")}}

# intro for admin help commands
adminHelpIntro = """:star: Here are my administrator commands! Prefix commands with `$COMMANDPREFIX$` - for example: `$COMMANDPREFIX$help 2`
**<Angled brackets>** indicate *optional* arguments, **[square brackets]** indicate *required* arguments."""

# help strings for admin bb commands
adminHelpDict = {"Miscellaneous":{  "admin-help": ("**admin-help**", "Display information about admin-only commands."),
                                        "set-announce-channel": ("**set-announce-channel** *<off>*", "Set the channel where BountyBot will send announcements (e.g new bounties)\n> Use `$COMMANDPREFIX$set-announce-channel off` to disable announcements."),
                                        "set-play-channel": ("**set-play-channel** *<off>*", "Set the channel where BountyBot will send info about completed bounties\n> Use `$COMMANDPREFIX$set-play-channel off` to disable completed bounty announcements."),
                                        "set-bounty-notify-role": ("**set-bounty-notify-role [role]**", "Set a role to ping when new bounties are created. **[role]** can be either a role mention, or a role ID."),
                                        "remove-bounty-notify-role": ("**remove-bounty-notify-role**", "Stop pinging the bounty notify role when new bounties are created.")}}

# string extensions for numbers, e.g 11th, 1st, 23rd...
numExtensions = ["th","st","nd","rd","th","th","th","th","th","th"]

# icons for factions
terranIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013574331596850/terran.png"
vosskIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013681621893130/vossk.png"
midorianIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013601019691038/midorian.png"
nivelianIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013623257890857/nivelian.png"
neutralIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/rocket_1f680.png"
voidIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013699841687602/void.png"
errorIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/exclamation-mark_2757.png"
winIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/trophy_1f3c6.png"
rocketIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/rocket_1f680.png"

# list associating faction names with icons
factionIcons = {"terran":terranIcon, "vossk":vosskIcon, "midorian":midorianIcon, "nivelian":nivelianIcon, "neutral":neutralIcon}

# colours to use in faction-related embed strips
factionColours = {"terran":Colour.gold(), "vossk":Colour.dark_green(), "midorian":Colour.dark_red(), "nivelian":Colour.teal(), "neutral":Colour.purple()}

builtInShipData = {# Terran
                    "Inflict": {"name": "Inflict", "manufacturer": "terran", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 4, "armour": 150, "cargo": 45, "numSecondaries": 1, "handling": 125, "value": 30900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Inflict", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694046057824296/inflict.png"},
                    "Furious": {"name": "Furious", "manufacturer": "terran", "maxPrimaries": 1, "maxTurrets": 1, "maxModules": 6, "armour": 176, "cargo": 108, "numSecondaries": 2, "handling": 112, "value": 75800, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Furious", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694028752126162/furious.png"},
                    "Taipan": {"name": "Taipan", "manufacturer": "terran", "maxPrimaries": 3, "maxTurrets": 0, "maxModules": 5, "armour": 176, "cargo": 50, "numSecondaries": 2, "handling": 113, "value": 100100, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Taipan", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694066626691082/taipan.png"},
                    "Hera": {"name": "Hera", "manufacturer": "terran", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 7, "armour": 152, "cargo": 64, "numSecondaries": 2, "handling": 108, "value": 107000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Hera", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694040021958749/hera.png"},
                    "Teneta": {"name": "Teneta", "manufacturer": "terran", "maxPrimaries": 2, "maxTurrets": 1, "maxModules": 7, "armour": 192, "cargo": 65, "numSecondaries": 4, "handling": 105, "value": 125400, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Teneta", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694071647141968/teneta.png"},
                    "Cormorant": {"name": "Cormorant", "manufacturer": "terran", "maxPrimaries": 0, "maxTurrets": 1, "maxModules": 8, "armour": 200, "cargo": 350, "numSecondaries": 4, "handling": 45, "value": 168900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Cormorant", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694018580938812/cormorant.png"},
                    "Anaan": {"name": "Anaan", "manufacturer": "terran", "maxPrimaries": 2, "maxTurrets": 1, "maxModules": 7, "armour": 220, "cargo": 240, "numSecondaries": 1, "handling": 65, "value": 176900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Anaan", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694009571573820/anaan.png"},
                    "Groza": {"name": "Groza", "manufacturer": "terran", "maxPrimaries": 3, "maxTurrets": 0, "maxModules": 8, "armour": 160, "cargo": 130, "numSecondaries": 3, "handling": 117, "value": 251600, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Groza", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694034305253447/groza.png"},
                    "Razor 6": {"name": "Razor 6", "manufacturer": "terran", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 6, "armour": 135, "cargo": 60, "numSecondaries": 1, "handling": 130, "value": 294900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Razor_6", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694059517345985/razor_6.png"},
                    "Phantom": {"name": "Phantom", "manufacturer": "terran", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 9, "armour": 200, "cargo": 52, "numSecondaries": 1, "handling": 150, "value": 1450000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Phantom", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694051963142215/phantom.png"},
                    "Ward": {"name": "Ward", "manufacturer": "terran", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 10, "armour": 145, "cargo": 65, "numSecondaries": 2, "handling": 95, "value": 1654800, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Ward", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694086897500220/ward.png"},
                    "Gryphon": {"name": "Gryphon", "manufacturer": "terran", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 10, "armour": 220, "cargo": 90, "numSecondaries": 2, "handling": 130, "value": 2100000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Gryphon", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720783815328399399/gryphon.png"},
                    "Veteran": {"name": "Veteran", "manufacturer": "terran", "maxPrimaries": 3, "maxTurrets": 1, "maxModules": 12, "armour": 200, "cargo": 110, "numSecondaries": 4, "handling": 92, "value": 2488400, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Veteran", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694081897889793/veteran.png"},
                    "Dark Angel": {"name": "Dark Angel", "manufacturer": "terran", "maxPrimaries": 4, "maxTurrets": 14, "maxModules": 14, "armour": 350, "cargo": 85, "numSecondaries": 2, "handling": 125, "value": 7227000, "aliases": ["Dark", "Angel", "DarkAngel"], "wiki": "https://galaxyonfire.fandom.com/wiki/Dark_Angel", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720783955455901775/dark_angel.png"},
                    "Rhino": {"name": "Rhino", "manufacturer": "terran", "maxPrimaries": 0, "maxTurrets": 1, "maxModules": 9, "armour": 1200, "cargo": 480, "numSecondaries": 2, "handling": 30, "value": 700000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Rhino", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720784079750168615/rhino.png"},
                    
                    # Vossk
                    "H'Soc": {"name": "H'Soc", "manufacturer": "vossk", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 7, "armour": 210, "cargo": 45, "numSecondaries": 2, "handling": 140, "value": 150000, "aliases": ["Soc", "HSoc"], "wiki": "https://galaxyonfire.fandom.com/wiki/H%27Soc", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694188659966022/hsoc.png"},
                    "Ni'Tirrk": {"name": "Ni'Tirrk", "manufacturer": "vossk", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 8, "armour": 280, "cargo": 80, "numSecondaries": 4, "handling": 128, "value": 250000, "aliases": ["Tirrk", "NTirrk"], "wiki": "https://galaxyonfire.fandom.com/wiki/N%27Tirrk", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720784330632200322/ntirrk.png"},
                    "K'Suuk": {"name": "K'Suuk", "manufacturer": "vossk", "maxPrimaries": 3, "maxTurrets": 0, "maxModules": 12, "armour": 255, "cargo": 55, "numSecondaries": 2, "handling": 125, "value": 1950000, "aliases": ["Suukk", "KSuukk"], "wiki": "https://galaxyonfire.fandom.com/wiki/K%27Suukk", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694205990568055/ksuukk.png"},
                    "S'Kanarr": {"name": "S'Kanarr", "manufacturer": "vossk", "maxPrimaries": 4, "maxTurrets": 1, "maxModules": 11, "armour": 315, "cargo": 150, "numSecondaries": 2, "handling": 70, "value": 7250000, "aliases": ["Kanarr", "SKanarr"], "wiki": "https://galaxyonfire.fandom.com/wiki/S%27Kanarr", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694223308980314/skanarr.png"},
                    "Na'Srrk": {"name": "Na'Srrk", "manufacturer": "vossk", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 12, "armour": 280, "cargo": 70, "numSecondaries": 4, "handling": 145, "value": 5400000, "aliases": ["srrk", "Nasrrk"], "wiki": "https://galaxyonfire.fandom.com/wiki/Na%27srrk", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720785069672890408/nasrrk.png"},
                    
                    # Nivelian
                    "Night Owl": {"name": "Night Owl", "manufacturer": "nivelian", "maxPrimaries": 1, "maxTurrets": 0, "maxModules": 4, "armour": 125, "cargo": 40, "numSecondaries": 2, "handling": 150, "value": 26500, "aliases": ["Night", "Owl", "NightOwl"], "wiki": "https://galaxyonfire.fandom.com/wiki/Night_Owl", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693855728697445/night_owl.png"},
                    "Type 43": {"name": "Type 43", "manufacturer": "nivelian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 6, "armour": 175, "cargo": 30, "numSecondaries": 3, "handling": 132, "value": 72500, "aliases": ["Type", "43", "Type43"], "wiki": "https://galaxyonfire.fandom.com/wiki/Type_43", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693873512546404/type_43.png"},
                    "Salvéhn": {"name": "Salvéhn", "manufacturer": "nivelian", "maxPrimaries": 2, "maxTurrets": 1, "maxModules": 6, "armour": 156, "cargo": 110, "numSecondaries": 1, "handling": 102, "value": 94500, "aliases": ["Salvehn"], "wiki": "https://galaxyonfire.fandom.com/wiki/Salvéhn", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693866533093526/salvehn.png"},
                    "Hatsuyuki": {"name": "Hatsuyuki", "manufacturer": "nivelian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 8, "armour": 115, "cargo": 28, "numSecondaries": 2, "handling": 145, "value": 171900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Hatsuyuki", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693848577409145/hatsuyuki.png"},
                    "Dace": {"name": "Dace", "manufacturer": "nivelian", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 5, "armour": 170, "cargo": 38, "numSecondaries": 1, "handling": 162, "value": 235600, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Dace", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693815752523796/dace.png"},
                    "Wraith": {"name": "Wraith", "manufacturer": "nivelian", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 9, "armour": 180, "cargo": 65, "numSecondaries": 2, "handling": 140, "value": 1750000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Wraith", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693879891951636/wraith.png"},
                    "Kinzer": {"name": "Kinzer", "manufacturer": "nivelian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 10, "armour": 180, "cargo": 45, "numSecondaries": 4, "handling": 120, "value": 2128000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Kinzer", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720785556925317140/kinzer.png"},
                    "Aegir": {"name": "Aegir", "manufacturer": "nivelian", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 11, "armour": 190, "cargo": 70, "numSecondaries": 4, "handling": 100, "value": 2712900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Aegir", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693803932975135/aegir.png"},
                    "Ghost": {"name": "Ghost", "manufacturer": "nivelian", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 14, "armour": 530, "cargo": 50, "numSecondaries": 2, "handling": 135, "value": 6000000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Ghost", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720785665402601522/ghost.png"},
                    "Scimitar": {"name": "Scimitar", "manufacturer": "nivelian", "maxPrimaries": 3, "maxTurrets": 0, "maxModules": 15, "armour": 400, "cargo": 40, "numSecondaries": 2, "handling": 104, "value": 5800000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Scimitar", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720785793337262180/scimitar.png"},
                    "Specter": {"name": "Specter", "manufacturer": "nivelian", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 16, "armour": 800, "cargo": 65, "numSecondaries": 2, "handling": 138, "value": 30000000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Specter", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720785904540581989/specter.png"},
                    
                    # Midorian
                    "Betty": {"name": "Betty", "manufacturer": "midorian", "maxPrimaries": 1, "maxTurrets": 0, "maxModules": 3, "armour": 95, "cargo": 25, "numSecondaries": 1, "handling": 120, "value": 16038, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Betty", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693735158972476/betty.png"},
                    "Hector": {"name": "Hector", "manufacturer": "midorian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 5, "armour": 105, "cargo": 42, "numSecondaries": 1, "handling": 148, "value": 38016, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Hector", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693749134655528/hector.png"},
                    "Badger": {"name": "Badger", "manufacturer": "midorian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 5, "armour": 135, "cargo": 55, "numSecondaries": 2, "handling": 112, "value": 38709, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Badger", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693707795595284/badger.png"},
                    "Cicero": {"name": "Cicero", "manufacturer": "midorian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 6, "armour": 125, "cargo": 25, "numSecondaries": 1, "handling": 155, "value": 51975, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Cicero", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693741052231821/cicero.png"},
                    "Berger CrossXT": {"name": "Berger CrossXT", "manufacturer": "midorian", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 6, "armour": 165, "cargo": 45, "numSecondaries": 2, "handling": 128, "value": 87318, "aliases": ["CrossXT", "Cross XT", "Berger XT", "BergerCrossXT", "Berger Cross XT", "BergerCross XT"], "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_CrossXT", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693724694184136/berger_crossxt.png"},
                    "Nuyang II": {"name": "Nuyang II", "manufacturer": "midorian", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 9, "armour": 225, "cargo": 105, "numSecondaries": 2, "handling": 90, "value": 930303, "aliases": ["Nuyang", "NuyangII", "Nuyang2", "Nuyang 2"], "wiki": "https://galaxyonfire.fandom.com/wiki/Nuyang_II", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693758605393980/nuyang_ii.png"},
                    
                    # Pirate
                    "Wasp": {"name": "Wasp", "manufacturer": "pirate", "maxPrimaries": 1, "maxTurrets": 0, "maxModules": 3, "armour": 100, "cargo": 30, "numSecondaries": 1, "handling": 160, "value": 19500, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Wasp", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693960422719558/wasp.png"},
                    "Hiro": {"name": "Hiro", "manufacturer": "pirate", "maxPrimaries": 1, "maxTurrets": 0, "maxModules": 4, "armour": 160, "cargo": 52, "numSecondaries": 2, "handling": 150, "value": 32600, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Hiro", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693933042303046/hiro.png"},
                    "Azov": {"name": "Azov", "manufacturer": "pirate", "maxPrimaries": 2, "maxTurrets": 1, "maxModules": 5, "armour": 150, "cargo": 55, "numSecondaries": 2, "handling": 128, "value": 61900, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Azov", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693920509460531/azov.png"},
                    "Tyrion": {"name": "Tyrion", "manufacturer": "pirate", "maxPrimaries": 1, "maxTurrets": 0, "maxModules": 9, "armour": 155, "cargo": 52, "numSecondaries": 4, "handling": 145, "value": 316400, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Tyrion", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693949009887392/tyrion.png"},
                    "Hernstein": {"name": "Hernstein", "manufacturer": "pirate", "maxPrimaries": 2, "maxTurrets": 1, "maxModules": 8, "armour": 210, "cargo": 180, "numSecondaries": 2, "handling": 75, "value": 327800, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Hernstein", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693928273117294/hernstein.png"},
                    "Velasco": {"name": "Velasco", "manufacturer": "pirate", "maxPrimaries": 3, "maxTurrets": 1, "maxModules": 8, "armour": 170, "cargo": 95, "numSecondaries": 2, "handling": 125, "value": 684300, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Velasco", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693956186210304/velasco.png"},
                    "Mantis": {"name": "Mantis", "manufacturer": "pirate", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 12, "armour": 240, "cargo": 75, "numSecondaries": 4, "handling": 117, "value": 4136800, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Mantis", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693938536841247/mantis.png"},
                    
                    # Grey
                    "Vol Noor": {"name": "Vol Noor", "manufacturer": "grey", "maxPrimaries": 2, "maxTurrets": 0, "maxModules": 7, "armour": 165, "cargo": 75, "numSecondaries": 2, "handling": 110, "value": 105000, "aliases": ["Vol", "Noor", "VolNoor"], "wiki": "https://galaxyonfire.fandom.com/wiki/Vol_Noor", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693658877165598/vol_noor.png"},
                    
                    # Void
                    "VoidX": {"name": "VoidX", "manufacturer": "void", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 15, "armour": 450, "cargo": 30, "numSecondaries": 4, "handling": 155, "value": 8115900, "aliases": ["Void", "X", "Void X"], "wiki": "https://galaxyonfire.fandom.com/wiki/VoidX", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720694144158138418/voidx.png"},
                    
                    # Deep Science
                    "Cronus": {"name": "Cronus", "manufacturer": "deep science", "maxPrimaries": 2, "maxTurrets": 7, "maxModules": 190, "armour": 190, "cargo": 95, "numSecondaries": 2, "handling": 120, "value": 1200000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Cronus", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693576509554818/cronus.png"},
                    "Typhon": {"name": "Typhon", "manufacturer": "deep science", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 12, "armour": 175, "cargo": 40, "numSecondaries": 0, "handling": 145, "value": 2500000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Typhon", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693589973270603/nemesis.png"},
                    "Nemesis": {"name": "Nemesis", "manufacturer": "deep science", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 14, "armour": 235, "cargo": 105, "numSecondaries": 1, "handling": 95, "value": 6800000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Nemesis", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720693603428728862/typhon.png"},
                    
                    # Most Wanted
                    "Blue Fyre": {"name": "Blue Fyre", "manufacturer": "most wanted", "maxPrimaries": 3, "maxTurrets": 0, "maxModules": 13, "armour": 270, "cargo": 125, "numSecondaries": 3, "handling": 116, "value": 4455000, "aliases": ["Blue", "Fyre", "BlueFyre", "Blue Fire", "BlueFire"], "wiki": "https://galaxyonfire.fandom.com/wiki/Blue_Fyre", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720787143596834816/blue_fyre.png"},
                    "Gator Custom": {"name": "Gator Custom", "manufacturer": "most wanted", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 12, "armour": 335, "cargo": 320, "numSecondaries": 2, "handling": 95, "value": 5148000, "aliases": ["Gator", "Custom", "GatorCustom"], "wiki": "https://galaxyonfire.fandom.com/wiki/Gator_Custom", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720787254632644608/gator_custom.png"},
                    "Amboss": {"name": "Amboss", "manufacturer": "most wanted", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 14, "armour": 305, "cargo": 80, "numSecondaries": 4, "handling": 110, "value": 6732000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Amboss", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720786108773826640/amboss.png"},
                    "Bloodstar": {"name": "Bloodstar", "manufacturer": "most wanted", "maxPrimaries": 4, "maxTurrets": 1, "maxModules": 14, "armour": 460, "cargo": 180, "numSecondaries": 4, "handling": 88, "value": 13365000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Bloodstar", "builtIn":False, "icon": "https://cdn.discordapp.com/attachments/700683544103747594/720786243725688832/bloodstar.png"},
                    
                    # Kaamo Club
                    "Groza Mk II": {"name": "Groza Mk II", "manufacturer": "kaamo club", "maxPrimaries": 5, "maxTurrets": 0, "maxModules": 11, "armour": 450, "cargo": 90, "numSecondaries": 1, "handling": 122, "value": 7130000, "aliases": ["Groza Mk 2", "Groza Mark 2", "Groza Mark II", "Groza MkII", "Groza Mk2", "Groza Mk.2", "Groza Mk. II"], "wiki": "https://galaxyonfire.fandom.com/wiki/Groza_Mk_II", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720787464901361670/groza_mk_ii.png"},
                    "Darkzov": {"name": "Darkzov", "manufacturer": "kaamo club", "maxPrimaries": 4, "maxTurrets": 1, "maxModules": 14, "armour": 420, "cargo": 70, "numSecondaries": 1, "handling": 130, "value": 7236000, "aliases": [], "wiki": "https://galaxyonfire.fandom.com/wiki/Darkzov", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720786415679569950/darkzov.png"},
                    "Berger Cross Special": {"name": "Berger Cross Special", "manufacturer": "kaamo club", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 14, "armour": 410, "cargo": 55, "numSecondaries": 4, "handling": 130, "value": 7335900, "aliases": ["Berger Cross Special", "Berger Special", "Cross Special"], "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_Cross_Special", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720787569541120010/berger_cross_special.png"},
                    "Phantom XT": {"name": "Phantom XT", "manufacturer": "kaamo club", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 14, "armour": 425, "cargo": 60, "numSecondaries": 1, "handling": 150, "value": 7430000, "aliases": ["PhantomXT"], "wiki": "https://galaxyonfire.fandom.com/wiki/Phantom_XT", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720787685035212830/phantom_xt.png"},
                    "Teneta R.E.D.": {"name": "Teneta R.E.D.", "manufacturer": "kaamo club", "maxPrimaries": 4, "maxTurrets": 1, "maxModules": 13, "armour": 545, "cargo": 70, "numSecondaries": 2, "handling": 117, "value": 7610000, "aliases": ["Teneta RED", "Teneta R.E.D"], "wiki": "https://galaxyonfire.fandom.com/wiki/Teneta_R.E.D.", "builtIn":False, "icon":"https://cdn.discordapp.com/attachments/700683544103747594/720787774328012840/teneta_r.e.d..png"},
                    "Kinzer RS": {"name": "Kinzer RS", "manufacturer": "kaamo club", "maxPrimaries": 4, "maxTurrets": 0, "maxModules": 15, "armour": 420, "cargo": 65, "numSecondaries": 4, "handling": 125, "value": 8930000, "aliases": ["KinzerRS"], "wiki": "https://galaxyonfire.fandom.com/wiki/Kinzer_RS", "builtIn":False, "icon": "https://cdn.discordapp.com/attachments/700683544103747594/720787863171629056/kinzer_rs.png"}}
                    
builtInModuleData = {   # armour
                        "E2 Exoclad": {"name": "E2 Exoclad", "aliases": ["E2", "Exoclad", "Exoclad E2"], "armour": 40, "value": 1070, "wiki": "https://galaxyonfire.fandom.com/wiki/E2_Exoclad", "builtIn":False},
                        "E4 Ultra Lamina": {"name": "E4 Ultra Lamina", "aliases": ["E4", "Lamina", "E4 Ultra", "E4 Lamina", "Ultra Lamina"], "armour": 80, "value": 4705, "wiki": "https://galaxyonfire.fandom.com/wiki/E4_Ultra_Lamina", "builtIn":False},
                        "E6 D-X Plating": {"name": "E6 D-X Plating", "aliases": ["E6", "D-X Plating", "E6 Plating", "E6 D-X"], "armour": 110, "value": 20171, "wiki": "https://galaxyonfire.fandom.com/wiki/E6_D-X_Plating", "builtIn":False},
                        "D'iol": {"name": "D'iol", "aliases": ["Diol"], "armour": 160, "value": 51449, "wiki": "https://galaxyonfire.fandom.com/wiki/D%27iol", "builtIn":False},
                        "T'yol": {"name": "T'yol", "aliases": ["Tyol"], "armour": 250, "value": 117922, "wiki": "https://galaxyonfire.fandom.com/wiki/T%27yol", "builtIn":False},
                        
                        # boosters
                        "Linear Boost": {"name": "Linear Boost", "aliases": ["Linear"], "value": 5704, "wiki": "https://galaxyonfire.fandom.com/wiki/Linear_Boost", "builtIn":False},
                        "Cyclotron Boost": {"name": "Cyclotron Boost", "aliases": ["Cyclotron"], "value": 11553, "wiki": "https://galaxyonfire.fandom.com/wiki/Cyclotron_Boost", "builtIn":False},
                        "Synchrotron Boost": {"name": "Synchrotron Boost", "aliases": ["Synchrotron"], "value": 22373, "wiki": "https://galaxyonfire.fandom.com/wiki/Synchrotron_Boost", "builtIn":False},
                        "Me'al": {"name": "Me'al", "aliases": ["Meal"], "value": 46897, "wiki": "https://galaxyonfire.fandom.com/wiki/Me%27al", "builtIn":False},
                        "Polytron Boost": {"name": "Polytron Boost", "aliases": ["Polytron"], "value": 86815, "wiki": "https://galaxyonfire.fandom.com/wiki/Polytron_Boost", "builtIn":False},
                        
                        # cabins
                        "Small Cabin": {"name": "Small Cabin", "aliases": [], "value": 3170, "wiki": "https://galaxyonfire.fandom.com/wiki/Small_Cabin", "builtIn":False},
                        "Medium Cabin": {"name": "Medium Cabin", "aliases": [], "value": 6347, "wiki": "https://galaxyonfire.fandom.com/wiki/Medium_Cabin", "builtIn":False},
                        "Large Cabin": {"name": "Large Cabin", "aliases": [], "value": 14190, "wiki": "https://galaxyonfire.fandom.com/wiki/Large_Cabin", "builtIn":False},

                        # cloaks
                        "U'tool": {"name": "U'tool", "aliases": ["Utool"], "value": 47367, "wiki": "https://galaxyonfire.fandom.com/wiki/", "builtIn":False},
                        "Sight Suppressor II": {"name": "Sight Suppressor II", "aliases": ["Sight Suppressor 2", "Sight 2", "Suppressor II", "Suppressor II"], "value": 29599, "wiki": "https://galaxyonfire.fandom.com/wiki/", "builtIn":False},
                        "Yin Co. Shadow Ninja": {"name": "Yin Co. Shadow Ninja", "aliases": ["Shadow Ninja", "Yin", "Yin Co Shadow Ninja"], "value": 69183, "wiki": "https://galaxyonfire.fandom.com/wiki/", "builtIn":False},

                        # compressors
                        "ZMI Optistore": {"name": "ZMI Optistore", "aliases": ["Optistore"], "cargoMultiplier":1.15, "value": 2576, "wiki": "https://galaxyonfire.fandom.com/wiki/ZMI_Optistore", "builtIn":False},
                        "Autopacker 2": {"name": "Autopacker 2", "aliases": ["Autopacker"], "cargoMultiplier":1.25, "value": 5747, "wiki": "https://galaxyonfire.fandom.com/wiki/Autopacker_2", "builtIn":False},
                        "Ultracompact": {"name": "Ultracompact", "aliases": [], "cargoMultiplier":1.4, "value": 14992, "wiki": "https://galaxyonfire.fandom.com/wiki/Ultracompact", "builtIn":False},
                        "Shrinker BT": {"name": "Shrinker BT", "aliases": ["Shrinker", "BT"], "cargoMultiplier":1.75, "value": 28571, "wiki": "https://galaxyonfire.fandom.com/wiki/Shrinker_BT", "builtIn":False},
                        "Rhoda Blackhole": {"name": "Rhoda Blackhole", "aliases": ["Blackhole", "Black Hole", "Rhoda Black Hole"], "cargoMultiplier":2, "value": 66305, "wiki": "https://galaxyonfire.fandom.com/wiki/Rhoda_Blackhole", "builtIn":False},
                        
                        # gamma shields
                        "Gamma Shield I": {"name": "Gamma Shield I", "aliases": ["Gamma Shield 1", "Gamma I", "Gamma 1"], "value": 27526, "wiki": "https://galaxyonfire.fandom.com/wiki/Gamma_Shield_I", "builtIn":False},
                        "Gamma Shield II": {"name": "Gamma Shield II", "aliases": ["Gamma Shield 2", "Gamma 2", "Gamma II"], "value": 43202, "wiki": "https://galaxyonfire.fandom.com/wiki/Gamma_Shield_II", "builtIn":False},

                        # mining drills
                        "IMT Extract 1.3": {"name": "IMT Extract 1.3", "aliases": ["IMT 1.3", "Extract 1.3"], "value": 4347, "wiki": "https://galaxyonfire.fandom.com/wiki/IMT_Extract_1.3", "builtIn":False},
                        "IMT Extract 2.7": {"name": "IMT Extract 2.7", "aliases": ["IMT 2.7", "Extract 2.7"], "value": 17297, "wiki": "https://galaxyonfire.fandom.com/wiki/IMT_Extract_2.7", "builtIn":False},
                        "K'yuul": {"name": "K'yuul", "aliases": ["Kyuul"], "value": 37743, "wiki": "https://galaxyonfire.fandom.com/wiki/K%27yuul", "builtIn":False},
                        "IMT Extract 4.0X": {"name": "IMT Extract 4.0X", "aliases": ["IMT Extract 4", "IMT 4.0X", "IMT 4", "Extract 4.0X", "Extract 4"], "value": 73093, "wiki": "https://galaxyonfire.fandom.com/wiki/IMT_Extract_4.0X", "builtIn":False},
                        "Gunant's Drill": {"name": "Gunant's Drill", "aliases": ["Gunant's", "Gunants", "Gunants Drill"], "value": 209353, "wiki": "https://galaxyonfire.fandom.com/wiki/Gunant%27s_Drill", "builtIn":False},

                        # repair beams
                        "Nirai SPP-C1": {"name": "Nirai SPP-C1", "aliases": ["SPP-C1", "Nirai C1"], "value": 68336, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_SPP-C1", "builtIn":False},
                        "Nirai SPP-M50": {"name": "Nirai SPP-M50", "aliases": ["SPP-M50", "Nirai M50"], "value": 365681, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_SPP-M50", "builtIn":False},

                        # repair bots
                        "Ketar Repair Bot": {"name": "Ketar Repair Bot", "aliases": ["Repair Bot", "Ketar Bot"], "value": 15285, "wiki": "https://galaxyonfire.fandom.com/wiki/Ketar_Repair_Bot", "builtIn":False},
                        "Ketar Repair Bot II": {"name": "Ketar Repair Bot II", "aliases": ["Katar Repair Bot 2", "Repair Bot 2", "Repair Bot II", "Ketar Bot 2", "Ketar Bot II"], "value": 141949, "wiki": "https://galaxyonfire.fandom.com/wiki/Ketar_Repair_Bot_II", "builtIn":False},

                        # scanners
                        "Telta Quickscan": {"name": "Telta Quickscan", "aliases": ["Quickscan"], "value": 2438, "wiki": "https://galaxyonfire.fandom.com/wiki/Telta_Quickscan", "builtIn":False},
                        "Telta Ecoscan": {"name": "Telta Ecoscan", "aliases": ["Ecoscan"], "value": 8647, "wiki": "https://galaxyonfire.fandom.com/wiki/Telta_Ecoscan", "builtIn":False},
                        "Hiroto Proscan": {"name": "Hiroto Proscan", "aliases": ["Proscan"], "value": 38955, "wiki": "https://galaxyonfire.fandom.com/wiki/Hiroto_Proscan", "builtIn":False},
                        "Hiroto Ultrascan": {"name": "Hiroto Ultrascan", "aliases": ["Ultrascan"], "value": 95309, "wiki": "https://galaxyonfire.fandom.com/wiki/Hiroto_Ultrascan", "builtIn":False},

                        # shields
                        "Targe Shield": {"name": "Targe Shield", "aliases": ["Targe"], "shield": 50, "value": 1620, "wiki": "https://galaxyonfire.fandom.com/wiki/Targe_Shield", "builtIn":False},
                        "Riot Shield": {"name": "Riot Shield", "aliases": ["Riot"], "shield": 80, "value": 5306, "wiki": "https://galaxyonfire.fandom.com/wiki/Riot_Shield", "builtIn":False},
                        "H'Belam": {"name": "H'Belam", "aliases": ["HBelam"], "shield": 120, "value": 13043, "wiki": "https://galaxyonfire.fandom.com/wiki/H%27Belam", "builtIn":False},
                        "Beamshield II": {"name": "Beamshield II", "aliases": ["Beamshield 2", "Beamshield"], "shield": 150, "value": 39331, "wiki": "https://galaxyonfire.fandom.com/wiki/Beamshield_II", "builtIn":False},
                        "Fluxed Matter Shield": {"name": "Fluxed Matter Shield", "aliases": ["Fluxed", "Matter Shield", "Fluxed Shield"], "shield": 220, "value": 101914, "wiki": "https://galaxyonfire.fandom.com/wiki/Fluxed_Matter_Shield", "builtIn":False},
                        "Particle Shield": {"name": "Particle Shield", "aliases": ["Particle"], "shield": 380, "value": 189194, "wiki": "https://galaxyonfire.fandom.com/wiki/Particle_Shield", "builtIn":False},

                        # spectral filters
                        "Spectral Filter SA-1": {"name": "Spectral Filter SA-1", "aliases": ["Spectral SA-1", "Spectral Filter SA-1", "Filter SA-1", "Spectral SA1", "Filter SA1"], "value": 43856, "wiki": "https://galaxyonfire.fandom.com/wiki/Spectral_Filter_SA-1", "builtIn":False},
                        "Spectral Filter ST-X": {"name": "Spectral Filter ST-X", "aliases": ["Spectral SA-X", "Spectral Filter SA-X", "Filter SA-X", "Spectral SAX", "Filter SAX"], "value": 154662, "wiki": "https://galaxyonfire.fandom.com/wiki/Spectral_Filter_ST-X", "builtIn":False},
                        "Spectral Filter Omega": {"name": "Spectral Filter Omega", "aliases": ["Spectral Omega", "Filter Omega", "Omega"], "value": 485406, "wiki": "https://galaxyonfire.fandom.com/wiki/Spectral_Filter_Omega", "builtIn":False},

                        # thrusters
                        "Static Thrust": {"name": "Static Thrust", "aliases": [], "handlingMultiplier":1.2, "value": 1398, "wiki": "https://galaxyonfire.fandom.com/wiki/Static_Thrust", "builtIn":False},
                        "Pendular Thrust": {"name": "Pendular Thrust", "aliases": [], "handlingMultiplier":1.4, "value": 2957, "wiki": "https://galaxyonfire.fandom.com/wiki/Pendular_Thrust", "builtIn":False},
                        "D'ozzt Thrust": {"name": "D'ozzt Thrust", "aliases": [], "handlingMultiplier":1.7, "value": 5762, "wiki": "https://galaxyonfire.fandom.com/wiki/D%27ozzt_Thrust", "builtIn":False},
                        "Mp'zzzm Thrust": {"name": "Mp'zzzm Thrust", "aliases": [], "handlingMultiplier":2, "value": 18731, "wiki": "https://galaxyonfire.fandom.com/wiki/Mp%27zzzm_Thrust", "builtIn":False},
                        "Pulsed Plasma Thrust": {"name": "Pulsed Plasma Thrust", "aliases": [], "handlingMultiplier":2.3, "value": 31015, "wiki": "https://galaxyonfire.fandom.com/wiki/Pulsed_Plasma_Thrust", "builtIn":False},

                        # tractor beams
                        'AB-1 "Retractor"': {"name": 'AB-1 "Retractor"', "aliases": ["Retractor", '"Retractor"', "AB-1 Retractor"], "value": 8962, "wiki": 'https://galaxyonfire.fandom.com/wiki/AB-1_"Retractor"', "builtIn":False},
                        'AB-2 "Glue Gun"': {"name": 'AB-2 "Glue Gun"', "aliases": ["Glue Gun", '"Glue Gun"', "AB-2 Glue Gun"], "value": 27464, "wiki": 'https://galaxyonfire.fandom.com/wiki/AB-2_"Glue Gun"', "builtIn":False},
                        'AB-3 "Kingfisher"': {"name": 'AB-3 "Kingfisher"', "aliases": ["Kingfisher", '"Kingfisher"', "AB-3 Kingfisher"], "value": 61448, "wiki": 'https://galaxyonfire.fandom.com/wiki/AB-3_"Kingfisher"', "builtIn":False},
                        'AB-4 "Octopus"': {"name": 'AB-4 "Octopus"', "aliases": ["Octopus", '"Octopus"', "AB-4 Octopus"], "value": 199026, "wiki": 'https://galaxyonfire.fandom.com/wiki/AB-4_"Octopus"', "builtIn":False},

                        # transfusion beams
                        "Crimson Drain": {"name": "Crimson Drain", "aliases": ["Crimson", "Drain"], "value": 8735, "wiki": "https://galaxyonfire.fandom.com/wiki/Crimson_Drain", "builtIn":False},
                        "Pandora Leech": {"name": "Pandora Leech", "aliases": ["Pandora", "Leech"], "value": 80537, "wiki": "https://galaxyonfire.fandom.com/wiki/Pandora_Leech", "builtIn":False},
                        
                        # weapon mods
                        "Nirai Overcharge": {"name": "Nirai Overcharge", "aliases": ["Overcharge"], "dpsMultiplier":1.1, "value": 29224, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_Overcharge", "builtIn":False},
                        "Nirai Overdrive": {"name": "Nirai Overdrive", "aliases": ["Overdrive"], "dpsMultiplier":1.1, "value": 30143, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_Overdrive", "builtIn":False},

                        # hyperdrives
                        "Khador Drive": {"name": "Khador Drive", "aliases": ["Khador"], "value": 310037, "wiki": "https://galaxyonfire.fandom.com/wiki/Khador_Drive", "builtIn":False}}
                        
builtInWeaponData = {   # Lasers
                        "Nirai Impulse EX 1": {"name": "Nirai Impulse EX 1", "aliases": ["Impulse EX 1", "Nirai EX 1", "EX 1", "Impulse 1", "Impulse EX1", "EX1", "Nirai Impulse EX1"], "dps":7.5, "value":2500, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_Impulse_EX_1", "builtIn":False},
                        "Nirai Impulse EX 2": {"name": "Nirai Impulse EX 2", "aliases": ["Impulse EX 2", "Nirai EX 2", "EX 2", "Impulse 2", "Impules EX2", "EX2", "Nirai Impulse EX2"], "dps":12.5, "value":6727, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_Impulse_EX_2", "builtIn":False},
                        "Nirai Charged Pulse": {"name": "Nirai Charged Pulse", "aliases": ["Charged Pulse", "Pulse", "Nirai Pulse"], "dps":15.78, "value":11465, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_Charged_Pulse", "builtIn":False},
                        "V'skorr": {"name": "V'skorr", "aliases": ["vskorr"], "dps":14, "value":9528, "wiki": "https://galaxyonfire.fandom.com/wiki/V%27skorr", "builtIn":False},
                        "Sh'koom": {"name": "Sh'koom", "aliases": ["shkoom"], "dps":16.66, "value":14195, "wiki": "https://galaxyonfire.fandom.com/wiki/Sh%27koom", "builtIn":False},
                        "Berger Focus I": {"name": "Berger Focus I", "aliases": ["berger focus" "berger focus 1" "focus 1" "focus I"], "dps":17.77, "value":22816, "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_Focus_I", "builtIn":False},
                        "Berger Focus II A1": {"name": "Berger Focus II A1", "aliases": ["berger focus 2 A1", "berger focus 2", "berger focus II", "berger focus A1", "focus 2", "focus 2 A1"], "dps":20, "value":31946, "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_Focus_II_A1", "builtIn":False},
                        "Berger Retribution": {"name": "Berger Retribution", "aliases": ["retribution"], "dps":24, "value":37744, "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_Retribution", "builtIn":False},
                        "Berger Converge IV": {"name": "Berger Converge IV", "aliases": ["converge IV", "berger converge 4", "converge 4", "berger converge", "converge"], "dps":32.94, "value":88969, "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_Converge_IV", "builtIn":False},
                        "Disruptor Laser": {"name": "Disruptor Laser", "aliases": ["disruptor"], "dps":60, "value":387090, "wiki": "https://galaxyonfire.fandom.com/wiki/Disruptor_Laser", "builtIn":False},
                        "Dark Matter Laser": {"name": "Dark Matter Laser", "aliases": ["dark matter", "dark laser", "matter laser"], "dps":88.23, "value":523757, "wiki": "https://galaxyonfire.fandom.com/wiki/Dark_Matter_Laser", "builtIn":False},
                        
                        'M6 A1 "Wolf"': {"name": 'M6 A1 "Wolf"', "aliases": ["M6 A1", "Wolf", "M6 Wolf", "A1 Wolf", "M6 A1 Wolf", '"Wolf"', 'M6 "Wolf"', 'A1 "Wolf"'], "dps":22.5, "value":38838, "wiki": 'https://galaxyonfire.fandom.com/wiki/M6_A1_"Wolf"', "builtIn":False},
                        'M6 A2 "Cougar"': {"name": 'M6 A2 "Cougar"', "aliases": ["M6 A2", "Cougar", "M6 Cougar", "A2 Cougar", "M6 A2 Cougar", '"Cougar"', 'M6 "Cougar"', 'A2 "Cougar"'], "dps":24.28, "value":46160, "wiki": 'https://galaxyonfire.fandom.com/wiki/M6_A2_"Cougar"', "builtIn":False},
                        'M6 A3 "Wolverine"': {"name": 'M6 A3 "Wolverine"', "aliases": ["M6 A3", "Wolverine", "M6 Wolverine", "A3 Wolverine", "M6 A3 Wolverine", '"Wolverine"', 'M6 "Wolverine"', 'A3 "Wolverine"'], "dps":34, "value":68725, "wiki": 'https://galaxyonfire.fandom.com/wiki/M6_A3_"Wolverine"', "builtIn":False},
                        'M6 A4 "Raccoon"': {"name": 'M6 A4 "Raccoon"', "aliases": ["M6 A4", "Raccoon", "M6 Raccoon", "A4 Raccoon", "M6 A4 Raccoon", '"Raccoon"', 'M6 "Raccoon"', 'A4 "Raccoon"'], "dps":92.3, "value":552747, "wiki": 'https://galaxyonfire.fandom.com/wiki/M6_A4_"Raccoon"', "builtIn":False},
                        
                        # Blasters
                        "N'saan": {"name": "N'saan", "aliases": ["Nsaan"], "dps":13.33, "value":12894, "wiki": "https://galaxyonfire.fandom.com/wiki/N%27saan", "builtIn":False},
                        "K'booskk": {"name": "K'booskk", "aliases": ["Kbooskk"], "dps":15.90, "value":16743, "wiki": "https://galaxyonfire.fandom.com/wiki/K%27booskk", "builtIn":False},
                        "Sh'gaal": {"name": "Sh'gaal", "aliases": ["Shgaal"], "dps":20.93, "value":24527, "wiki": "https://galaxyonfire.fandom.com/wiki/Sh%27gaal", "builtIn":False},
                        "H'nookk": {"name": "H'nookk", "aliases": ["Hnookk"], "dps":27.27, "value":47478, "wiki": "https://galaxyonfire.fandom.com/wiki/H%27nookk", "builtIn":False},
                        "Gram Blaster": {"name": "Gram Blaster", "aliases": ["Gram"], "dps":40, "value":41703, "wiki": "https://galaxyonfire.fandom.com/wiki/Gram_Blaster", "builtIn":False},
                        "Ridil Blaster": {"name": "Ridil Blaster", "aliases": ["Ridil"], "dps":48, "value":67535, "wiki": "https://galaxyonfire.fandom.com/wiki/Ridil_Blaster", "builtIn":False},
                        "Tyrfing Blaster": {"name": "Tyrfing Blaster", "aliases": ["Tyrfing"], "dps":59.09, "value":97683, "wiki": "https://galaxyonfire.fandom.com/wiki/Tyrfing_Blaster", "builtIn":False},
                        "Mimung Blaster": {"name": "Mimung Blaster", "aliases": ["Mimung"], "dps":69.59, "value":369763, "wiki": "https://galaxyonfire.fandom.com/wiki/Mimung_Blaster", "builtIn":False},
                        
                        # EMP Blasters
                        "Luna EMP Mk I": {"name": "Luna EMP Mk I", "aliases": ["Luna Mk I", "Luna EMP", "Luna", "EMP Mk I", "EMP I"], "dps":8.57, "value":5942, "wiki": "https://galaxyonfire.fandom.com/wiki/Luna_EMP_Mk_I", "builtIn":False},
                        "Sol EMP Mk II": {"name": "Sol EMP Mk II", "aliases": ["Sol Mk II", "Sol EMP", "Sol", "EMP Mk II", "EMP II"], "dps":11.11, "value":12517, "wiki": "https://galaxyonfire.fandom.com/wiki/Sol_EMP_Mk_II", "builtIn":False},
                        "Dia EMP Mk III": {"name": "Dia EMP Mk III", "aliases": ["Dia Mk III", "Dia EMP", "Dia", "EMP Mk III", "EMP III"], "dps":17.77, "value":40736, "wiki": "https://galaxyonfire.fandom.com/wiki/Dia_EMP_Mk_III", "builtIn":False},
                        
                        # Auto Cannons
                        "Micro Gun MK I": {"name": "Micro Gun MK I", "aliases": ["Micro MK I", "Micro I"], "dps":9.09, "value":2577, "wiki": "https://galaxyonfire.fandom.com/wiki/Micro_Gun_MK_I", "builtIn":False},
                        "Micro Gun MK II": {"name": "Micro Gun MK II", "aliases": ["Micro MK II", "Micro II"], "dps":11.76, "value":5538, "wiki": "https://galaxyonfire.fandom.com/wiki/Micro_Gun_MK_II", "builtIn":False},
                        "64MJ Railgun": {"name": "64MJ Railgun", "aliases": ["64MJ Railgun", "64 Rail"], "dps":14.28, "value":15343, "wiki": "https://galaxyonfire.fandom.com/wiki/64MJ_Railgun", "builtIn":False},
                        "Scram Cannon": {"name": "Scram Cannon", "aliases": ["scram"], "dps":20.00, "value":47203, "wiki": "https://galaxyonfire.fandom.com/wiki/Scram_Cannon", "builtIn":False},
                        "128MJ Railgun": {"name": "128MJ Railgun", "aliases": ["128MJ Railgun", "128 Rail"], "dps":25.00, "value":24675, "wiki": "https://galaxyonfire.fandom.com/wiki/128MJ_Railgun", "builtIn":False},
                        "Mass Driver MD 10": {"name": "Mass Driver MD 10", "aliases": ["MD 10", "MD10", "Mass Driver 10", "Mass Driver MD10"], "dps":44.44, "value":114314, "wiki": "https://galaxyonfire.fandom.com/wiki/Mass_Driver_MD_10", "builtIn":False},
                        "Mass Driver MD 12": {"name": "Mass Driver MD 12", "aliases": ["MD 12", "MD12", "Mass Driver 12", "Mass Driver MD12"], "dps":70.00, "value":423181, "wiki": "https://galaxyonfire.fandom.com/wiki/Mass_Driver_MD_12", "builtIn":False},
                        
                        # Thermal Fusion Cannons
                        "Thermic o5": {"name": "Thermic o5", "aliases": ["o5", "Thermic"], "dps":10.00, "value":9959, "wiki": "https://galaxyonfire.fandom.com/wiki/Thermic_o5", "builtIn":False},
                        "ReHeat o10": {"name": "ReHeat o10", "aliases": ["o10", "ReHeat"], "dps":23.52, "value":35724, "wiki": "https://galaxyonfire.fandom.com/wiki/ReHeat_o10", "builtIn":False},
                        "MaxHeat o20": {"name": "MaxHeat o20", "aliases": ["o20", "MaxHeat"], "dps":33.33, "value":86204, "wiki": "https://galaxyonfire.fandom.com/wiki/MaxHeat_o20", "builtIn":False},
                        "SunFire o50": {"name": "SunFire o50", "aliases": ["o50", "SunFire"], "dps":41.66, "value":183413, "wiki": "https://galaxyonfire.fandom.com/wiki/SunFire_o50", "builtIn":False},
                        
                        # Scatter Guns
                        "Nirai .50AS": {"name": "Nirai .50AS", "aliases": [".50AS", "50AS", "Nirai 50AS"], "dps":18.57, "value":44092, "wiki": "https://galaxyonfire.fandom.com/wiki/Nirai_.50AS", "builtIn":False},
                        "Berger FlaK 9-9": {"name": "Berger FlaK 9-9", "aliases": ["Berger FlaK 9-9", "Berger FlaK", "Berger 9-9", "Flak 9-9", "9-9"], "dps":25.33, "value":135058, "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_FlaK_9-9", "builtIn":False},
                        "Icarus Heavy AS": {"name": "Icarus Heavy AS", "aliases": ["Icarus Heavy AS", "Icarus Heavy", "Icarus AS", "Heavy AS", "Icarus"], "dps":33.33, "value":356787, "wiki": "https://galaxyonfire.fandom.com/wiki/Icarus_Heavy_AS", "builtIn":False}}

builtInUpgradeData = {  "+30 Cargo Space": {"name": "+30 Cargo Space", "shipToUpgradeValueMult":0.3, "cargo": 30, "builtIn":False, "wiki":"https://galaxyonfire.fandom.com/wiki/Kaamo_Club#Ship_Upgrades"},
                        "+20 Handling": {"name": "+20 Handling", "shipToUpgradeValueMult":0.2, "handling": 20, "builtIn":False, "wiki":"https://galaxyonfire.fandom.com/wiki/Kaamo_Club#Ship_Upgrades"},
                        "Extra Equipment Slot": {"name": "Extra Equipment Slot", "shipToUpgradeValueMult":0.4, "maxModules": 1, "builtIn":False, "wiki":"https://galaxyonfire.fandom.com/wiki/Kaamo_Club#Ship_Upgrades"},
                        "+40 Armor": {"name": "+40 Armor", "shipToUpgradeValueMult":0.2, "armour": 40, "builtIn":False, "wiki":"https://galaxyonfire.fandom.com/wiki/Kaamo_Club#Ship_Upgrades"}}

# data for builtIn criminals to be used in bbCriminal.fromDict
# criminals marked as not builtIn to allow for dictionary init. The criminal object is then marked as builtIn during package __init__.py
builtInCriminalData = {"Pal Tyyrt": {"name":"Pal Tyyrt", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226618919780359/pal_tyyrt.png", "aliases":["tyyrt"], "wiki":"https://galaxyonfire.fandom.com/wiki/Pal_Tyyrt", "builtIn":False, "isPlayer":False},
                "Kehnor": {"name":"Kehnor", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226614767419432/kehnor.png", "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Kehnor", "builtIn":False, "isPlayer":False},
                "Gendol Ethor": {"name":"Gendol Ethor", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226611608977490/gendol_ethor.png", "aliases":["gendol","ethor"], "wiki":"https://galaxyonfire.fandom.com/wiki/Gendol_Ethor", "builtIn":False, "isPlayer":False},
                "Korr Bekkt": {"name":"Korr Bekkt", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226617254510602/korr_bekkt.png", "aliases":["korr", "bekkt"], "wiki":"https://galaxyonfire.fandom.com/wiki/Korr_Bekkt", "builtIn":False, "isPlayer":False},
                "Hongar Meton": {"name":"Hongar Meton", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226613278441543/hongar_meton.png", "aliases":["hongar", "meton"], "wiki":"https://galaxyonfire.fandom.com/wiki/Hongar_Meton", "builtIn":False, "isPlayer":False},
                "Trent Jameson": {"name":"Trent Jameson", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226622195269632/trent_jameson.png", "aliases":["trent", "jameson"], "wiki":"https://galaxyonfire.fandom.com/wiki/Trent_Jameson", "builtIn":False, "isPlayer":False},
                "Qyrr Myfft": {"name":"Qyrr Myfft", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226620786114590/qyrr_myfft.png", "aliases":["qyrr","myfft"], "wiki":"https://galaxyonfire.fandom.com/wiki/Qyrr_Myfft", "builtIn":False, "isPlayer":False},

                # Midorian
                "Toma Prakupy": {"name":"Toma Prakupy", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226704953344060/toma_prakupy.png", "aliases":["toma"], "wiki":"https://galaxyonfire.fandom.com/wiki/Toma_Prakupy", "builtIn":False, "isPlayer":False},
                "Nombur Telénah": {"name":"Nombur Telénah", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226703703310397/nombur_talenah.png", "aliases":["nombur","telenah","telénah"], "wiki":"https://galaxyonfire.fandom.com/wiki/Nombur_Telénah", "builtIn":False, "isPlayer":False},
                "Bartholomeu Drew": {"name":"Bartholomeu Drew", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226697974022204/bartholomeu_drew.png", "aliases":["bart","bartholomeu","drew"], "wiki":"https://galaxyonfire.fandom.com/wiki/Bartholomeu_Drew", "builtIn":False, "isPlayer":False},
                "Doni Trillyx": {"name":"Doni Trillyx", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226699119067217/doni_trillyx.png", "aliases":["doni","trillyx"], "wiki":"https://galaxyonfire.fandom.com/wiki/Doni_Trillyx", "builtIn":False, "isPlayer":False},
                "Heinrich Wickel": {"name":"Heinrich Wickel", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226700305793085/heinrich_wickel.png", "aliases":["heinrich","wickel"], "wiki":"https://galaxyonfire.fandom.com/wiki/Heinrich_Wickel", "builtIn":False, "isPlayer":False},
                "Mashon Redal": {"name":"Mashon Redal", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226702122057768/mashon_redal.png", "aliases":["mashon","redal"], "wiki":"https://galaxyonfire.fandom.com/wiki/Mashon_Redal", "builtIn":False, "isPlayer":False},

                # Vossk
                "Mrrkt Nimkk": {"name":"Mrrkt Nimkk", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226820854284368/mrrkt_minkk.png", "aliases":["mrrkt","nimkk"], "wiki":"https://galaxyonfire.fandom.com/wiki/Mrrkt_Nimkk", "builtIn":False, "isPlayer":False},
                "Alvar Julen": {"name":"Alvar Julen", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226819461775360/alvar_julen.png", "aliases":["alvar","julen"], "wiki":"https://galaxyonfire.fandom.com/wiki/Alvar_Julen", "builtIn":False, "isPlayer":False},
                "Vortt Baskk": {"name":"Vortt Baskk", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226826831298710/vortt_baskk.png", "aliases":["vortt","baskk"], "wiki":"https://galaxyonfire.fandom.com/wiki/Vortt_Baskk", "builtIn":False, "isPlayer":False},
                "Oluchi Erland": {"name":"Oluchi Erland", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226822540394546/oluchi_erland.png", "aliases":["oluchi","erland"], "wiki":"https://galaxyonfire.fandom.com/wiki/Oluchi_Erland", "builtIn":False, "isPlayer":False},
                "Orp Tsam": {"name":"Orp Tsam", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226823966720041/orp_tsam.png", "aliases":["orp", "tsam"], "wiki":"https://galaxyonfire.fandom.com/wiki/Orp_Tsam", "builtIn":False, "isPlayer":False},
                "Urr Sekant": {"name":"Urr Sekant", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226825488990258/urr_sakant.png", "aliases":["urr", "sekant"], "wiki":"https://galaxyonfire.fandom.com/wiki/Urr_Sakant", "builtIn":False, "isPlayer":False},

                # Nivelian
                "Borsul Tarand": {"name":"Borsul Tarand", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226764948537374/borsul_tarand.png", "aliases":["borsul","tarand"], "wiki":"https://galaxyonfire.fandom.com/wiki/Borsul_Tarand", "builtIn":False, "isPlayer":False},
                "Malon Sentendar": {"name":"Malon Sentendar", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226767939207178/malon_sentendar.png", "aliases":["malon","sendendar"], "wiki":"https://galaxyonfire.fandom.com/wiki/Malon_Sentendar", "builtIn":False, "isPlayer":False},
                "Vilhelm Lindon": {"name":"Vilhelm Lindon", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226772812726302/vilhelm_lindon.png", "aliases":["vilhelm","lindon"], "wiki":"https://galaxyonfire.fandom.com/wiki/Vilhelm_lindon", "builtIn":False, "isPlayer":False},
                "Tamir Prakupy": {"name":"Tamir Prakupy", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226770707185664/tamir_prakupy.png", "aliases":["tamir"], "wiki":"https://galaxyonfire.fandom.com/wiki/Tamir_Prakupy", "builtIn":False, "isPlayer":False},
                "Merson Surr": {"name":"Merson Surr", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226769327521872/merson_surr.png", "aliases":["merson","surr"], "wiki":"https://galaxyonfire.fandom.com/wiki/Merson_Surr", "builtIn":False, "isPlayer":False},
                "Ganfor Kant": {"name":"Ganfor Kant", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226766630584370/ganfor_kant.png", "aliases":["ganfor","kant"], "wiki":"https://galaxyonfire.fandom.com/wiki/Ganfor_Kant", "builtIn":False, "isPlayer":False}}

# data for builtIn systems to be used in bbSystem.fromDict
builtInSystemData = { #Terran
            "Aquila": {"name":"Aquila", "faction":"terran", "neighbours":["Wolf-Reiser", "Loma", "Union"], "security":2, "coordinates":(9, 2), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Aquila_system"},
            "Augmenta": {"name":"Augmenta", "faction":"terran", "neighbours":["Weymire", "Magnetar", "V'Ikka", "Buntta"], "security":0, "coordinates":(6, 6), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Augmenta_system"},
            "Beidan": {"name":"Beidan", "faction":"terran", "neighbours":[], "security":0, "coordinates":(12, 6), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Beidan"},
            "Buntta": {"name":"Buntta", "faction":"terran", "neighbours":["Suteo", "Behén", "Augmenta", "V'Ikka", "Pescal Inartu", "Pan"], "security":1, "coordinates":(5, 9), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Buntta"},
            "Magnetar": {"name":"Magnetar", "faction":"terran", "neighbours":["Union", "Oom'Bak", "V'Ikka", "Augmenta"], "security":0, "coordinates":(6, 8), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Magnetar_system"},
            "Pan": {"name":"Pan", "faction":"terran", "neighbours":["Buntta", "Pescal Inartu"], "security":2, "coordinates":(3, 11), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Pan"},
            "Pescal Inartu": {"name":"Pescal Inartu", "faction":"terran", "neighbours":["Pan", "Buntta"], "security":2, "coordinates":(6, 12), "aliases":["pescal","inartu"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Pescal_Inartu"},
            "Prospero": {"name":"Prospero", "faction":"terran", "neighbours":["Union", "Vulpes"], "security":2, "coordinates":(5, 10), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Prospero"},
            "Union": {"name":"Union", "faction":"terran", "neighbours":["Loma", "Aquila", "Prospero", "Magnetar", "Weymire"], "security":1, "coordinates":(7, 4), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Union_system"},
            "Vulpes": {"name":"Vulpes", "faction":"terran", "neighbours":["Prospero", "Oom'Bak"], "security":2, "coordinates":(10, 7), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Vulpes"},
            "Wolf-Reiser": {"name":"Wolf-Reiser", "faction":"terran", "neighbours":["Aquila"], "security":0, "coordinates":(10, 3), "aliases":["wolfreiser","wolf","reiser"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Wolf-Reiser"},
            
            #Vossk
            "K'Ontrr": {"name":"K'Ontrr", "faction":"vossk", "neighbours":["S'Kolptorr", "Ni'Mrrod", "Me'Enkk"], "security":3, "coordinates":(10, 11), "aliases":["kontrr"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:K'Ontrr"},
            "Me'Enkk": {"name":"Me'Enkk", "faction":"vossk", "neighbours":["Ni'Mrrod", "K'Ontrr"], "security":3, "coordinates":(11, 12), "aliases":["meenkk"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Me'Enkk"},
            "Ni'Mrrod": {"name":"Ni'Mrrod", "faction":"vossk", "neighbours":["K'Ontrr", "Me'Enkk"], "security":3, "coordinates":(12, 12), "aliases":["nimrrod"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Ni'Mrrod"},
            "Oom'Bak": {"name":"Oom'Bak", "faction":"vossk", "neighbours":["Magnetar", "Vulpes", "S'Kolptorr", "V'Ikka"], "security":1, "coordinates":(9, 8), "aliases":["oombak"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Oom'Bak"},
            "S'Kolptorr": {"name":"S'Kolptorr", "faction":"vossk", "neighbours":["K'Ontrr", "Oom'Bak", "V'Ikka"], "security":2, "coordinates":(9, 9), "aliases":["skolptorr"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:S'Kolptorr"},
            "V'Ikka": {"name":"V'Ikka", "faction":"vossk", "neighbours":["Augmenta", "Buntta", "Magnetar", "Oom'Bak", "S'Kolptorr"], "security":1, "coordinates":(7, 8), "aliases":["vikka"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:V'Ikka"},
            "Wah'Norr": {"name":"Wah'Norr", "faction":"vossk", "neighbours":[], "security":3, "coordinates":(12, 8), "aliases":["wahnorr"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Wah'Norr"},
            "Y'Mirr": {"name":"Y'Mirr", "faction":"vossk", "neighbours":[], "security":3, "coordinates":(11, 9), "aliases":["ymirr"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Y'Mirr"},
            
            #Nivelian
            "Behén": {"name":"Behén", "faction":"nivelian", "neighbours":["Nesla", "Suteo", "Weymire", "Buntta"], "security":2, "coordinates":(3, 6), "aliases":["behen"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Behén"},
            "Paréah": {"name":"Paréah", "faction":"nivelian", "neighbours":["Nesla"], "security":1, "coordinates":(2, 5), "aliases":["pareah"], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Paréah"},
            "Nesla": {"name":"Nesla", "faction":"nivelian", "neighbours":["Behén", "Paréah", "Weymire", "Shima", "Eanya"], "security":2, "coordinates":(4, 3), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Nesla"},
            "Suteo": {"name":"Suteo", "faction":"nivelian", "neighbours":["Behén", "Buntta"], "security":2, "coordinates":(3, 8), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Suteo"},
            "Weymire": {"name":"Weymire", "faction":"nivelian", "neighbours":["Augmenta", "Behén", "Union", "Nesla", "Shima"], "security":1, "coordinates":(6, 4), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Weymire"},
            
            #Midorian
            "Eanya": {"name":"Eanya", "faction":"midorian", "neighbours":["Nesla", "Ginoya"], "security":3, "coordinates":(2, 3), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Eanya"},
            "Ginoya": {"name":"Ginoya", "faction":"midorian", "neighbours":["Talidor", "Eanya"], "security":3, "coordinates":(2, 2), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Ginoya"},
            "Loma": {"name":"Loma", "faction":"midorian", "neighbours":["Shima", "Union", "Aquila"], "security":3, "coordinates":(5, 1), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Loma"},
            "Mido": {"name":"Mido", "faction":"midorian", "neighbours":[], "security":3, "coordinates":(4, 2), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Mido"},
            "Talidor": {"name":"Talidor", "faction":"midorian", "neighbours":["Ginoya"], "security":3, "coordinates":(3, 1), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Talidor"},
            
            #Neutral
            "Alda": {"name":"Alda", "faction":"neutral", "neighbours":[], "security":3, "coordinates":(8, 13), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Alda"},
            "Her Jaza": {"name":"Her Jaza", "faction":"neutral", "neighbours":[], "security":3, "coordinates":(8, 12), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Her_Jaza"},
            "Shima": {"name":"Shima", "faction":"neutral", "neighbours":["Loma", "Weymire", "Nesla"], "security":0, "coordinates":(5, 3), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Shima"},
            "Skavac": {"name":"Skavac", "faction":"neutral", "neighbours":[], "security":3, "coordinates":(10, 1), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Skavac"},
            "Skor Terpa": {"name":"Skor Terpa", "faction":"neutral", "neighbours":[], "security":3, "coordinates":(7, 1), "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Category:Skor_Terpa"}
        }

builtInTurretData = { # Manual
                        "Hammerhead D1": {"name": "Hammerhead D1", "aliases": ["D1"], "dps": 20, "value": 24174, "wiki": "https://galaxyonfire.fandom.com/wiki/Hammerhead_D1", "builtIn":False},
                        "Hammerhead D2A2": {"name": "Hammerhead D2A2", "aliases": ["D2A2", "D2", "Hammerhead D2"], "dps": 35.71, "value": 77097, "wiki": "https://galaxyonfire.fandom.com/wiki/Hammerhead_D2A2", "builtIn":False},
                        "L'ksaar": {"name": "L'ksaar", "aliases": ["Lksaar"], "dps": 48, "value": 149317, "wiki": "https://galaxyonfire.fandom.com/wiki/L%27ksaar", "builtIn":False},
                        "Matador TS": {"name": "Matador TS", "aliases": ["Matador", "TS"], "dps": 90, "value": 485350, "wiki": "https://galaxyonfire.fandom.com/wiki/Matador_TS", "builtIn":False},

                        # Auto
                        "Berger AGT 20mm": {"name": "Berger AGT 20mm", "aliases": ["Berger AGT", "Berger 20mm", "20mm", "AGT", "AGT 20mm"], "dps": 40, "value": 227040, "wiki": "https://galaxyonfire.fandom.com/wiki/Berger_AGT_20mm", "builtIn":False},
                        "Skuld AT XR": {"name": "Skuld AT XR", "aliases": ["Skuld XR", "Skuld", "AT XR", "Skuld AT", "XR"], "dps": 47.36, "value": 407793, "wiki": "https://galaxyonfire.fandom.com/wiki/Skuld_AT_XR", "builtIn":False},
                        'HH-AT "Archimedes"': {"name": 'HH-AT "Archimedes"', "aliases": ["HH-AT", "HHAT Archimedes", "Archimedes", '"Archimedes"'], "dps": 53.33, "value": 586176, "wiki": 'https://galaxyonfire.fandom.com/wiki/HH-AT_"Archimedes"', "builtIn":False},

                        # plasma collectors
                        "PE Proton": {"name": "PE Proton", "aliases": ["Proton"], "dps":0, "value": 43856, "wiki": "https://galaxyonfire.fandom.com/wiki/PE_Proton", "builtIn":False},
                        "PE Ambipolar-5": {"name": "PE Ambipolar-5", "aliases": ["Ambipolar", "PE Ambipolar 5", "PE Ambipolar"], "dps":0, "value": 115169, "wiki": "https://galaxyonfire.fandom.com/wiki/PE_Ambipolar-5", "builtIn":False},
                        "PE Fusion H2": {"name": "PE Fusion H2", "aliases": ["Fusion", "PE Fusion"], "dps":0, "value": 631720, "wiki": "https://galaxyonfire.fandom.com/wiki/PE_Fusion_H2", "builtIn":False}}

# To be populated during package init
builtInSystemObjs = {}
builtInCriminalObjs = {}
# builtInShipObjs = {}
builtInModuleObjs = {}
builtInWeaponObjs = {}
builtInUpgradeObjs = {}
builtInTurretObjs = {}

rankedShipKeys = []
rankedModuleObjs = []
rankedWeaponObjs = []
rankedTurretObjs = []
