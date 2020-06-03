# Shame, but i'd rather this than keep factionColours in bountybot.py
from discord import Colour

factions = ["terran", "vossk", "midorian", "nivelian", "neutral"]
bountyFactions = ["terran", "vossk", "midorian", "nivelian"]

bountyNames = {"terran": ["Pal Tyyrt", "Kehnor", "Gendol Ethor", "Korr Bekkt", "Hongar Meton"],
                "vossk": ["Mrrkt Nimkk", "Alvar Julen", "Vortt Baskk", "Oluchi Erland", "Orp Tsam"],
                "midorian": ["Toma Prakupy", "Nombur Telénah", "Bartholomeu Drew", "Doni Trillyx", "Mashon Redal"],
                "nivelian": ["Borsul Tarand", "Vilhelm Lindon", "Tamir Prakupy", "Merson Surr", "Ganfor Kant"]}

                # Terran
bountyIcons = {"Pal Tyyrt": "https://cdn.discordapp.com/attachments/700683544103747594/711226618919780359/pal_tyyrt.png",
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

builtInCriminalData = {"Pal Tyyrt": {"name":"Pal Tyyrt", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226618919780359/pal_tyyrt.png", "aliases":["tyyrt"], "wiki":"https://galaxyonfire.fandom.com/wiki/Pal_Tyyrt", "builtIn":True, "isPlayer":False},
                "Kehnor": {"name":"Kehnor", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226614767419432/kehnor.png", "aliases":[], "wiki":"https://galaxyonfire.fandom.com/wiki/Kehnor", "builtIn":True, "isPlayer":False},
                "Gendol Ethor": {"name":"Gendol Ethor", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226611608977490/gendol_ethor.png", "aliases":["gendol","ethor"], "wiki":"https://galaxyonfire.fandom.com/wiki/Gendol_Ethor", "builtIn":True, "isPlayer":False},
                "Korr Bekkt": {"name":"Korr Bekkt", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226617254510602/korr_bekkt.png", "aliases":["korr", "bekkt"], "wiki":"https://galaxyonfire.fandom.com/wiki/Korr_Bekkt", "builtIn":True, "isPlayer":False},
                "Hongar Meton": {"name":"Hongar Meton", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226613278441543/hongar_meton.png", "aliases":["hongar", "meton"], "wiki":"https://galaxyonfire.fandom.com/wiki/Hongar_Meton", "builtIn":True, "isPlayer":False},
                "Trent Jameson": {"name":"Trent Jameson", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226622195269632/trent_jameson.png", "aliases":["trent", "jameson"], "wiki":"https://galaxyonfire.fandom.com/wiki/Trent_Jameson", "builtIn":True, "isPlayer":False},
                "Qyrr Myfft": {"name":"Qyrr Myfft", "faction":"terran", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226620786114590/qyrr_myfft.png", "aliases":["qyrr","myfft"], "wiki":"https://galaxyonfire.fandom.com/wiki/Qyrr_Myfft", "builtIn":True, "isPlayer":False},

                # Midorian
                "Toma Prakupy": {"name":"Toma Prakupy", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226704953344060/toma_prakupy.png", "aliases":["toma"], "wiki":"https://galaxyonfire.fandom.com/wiki/Toma_Prakupy", "builtIn":True, "isPlayer":False},
                "Nombur Telénah": {"name":"Nombur Telénah", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226703703310397/nombur_talenah.png", "aliases":["nombur","telenah","telénah"], "wiki":"https://galaxyonfire.fandom.com/wiki/Nombur_Telénah", "builtIn":True, "isPlayer":False},
                "Bartholomeu Drew": {"name":"Bartholomeu Drew", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226697974022204/bartholomeu_drew.png", "aliases":["bart","bartholomeu","drew"], "wiki":"https://galaxyonfire.fandom.com/wiki/Bartholomeu_Drew", "builtIn":True, "isPlayer":False},
                "Doni Trillyx": {"name":"Doni Trillyx", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226699119067217/doni_trillyx.png", "aliases":["doni","trillyx"], "wiki":"https://galaxyonfire.fandom.com/wiki/Doni_Trillyx", "builtIn":True, "isPlayer":False},
                "Heinrich Wickel": {"name":"Heinrich Wickel", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226700305793085/heinrich_wickel.png", "aliases":["heinrich","wickel"], "wiki":"https://galaxyonfire.fandom.com/wiki/Heinrich_Wickel", "builtIn":True, "isPlayer":False},
                "Mashon Redal": {"name":"Mashon Redal", "faction":"midorian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226702122057768/mashon_redal.png", "aliases":["mashon","redal"], "wiki":"https://galaxyonfire.fandom.com/wiki/Mashon_Redal", "builtIn":True, "isPlayer":False},

                # Vossk
                "Mrrkt Nimkk": {"name":"Mrrkt Nimkk", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226820854284368/mrrkt_minkk.png", "aliases":["mrrkt","nimkk"], "wiki":"https://galaxyonfire.fandom.com/wiki/Mrrkt_Nimkk", "builtIn":True, "isPlayer":False},
                "Alvar Julen": {"name":"Alvar Julen", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226819461775360/alvar_julen.png", "aliases":["alvar","julen"], "wiki":"https://galaxyonfire.fandom.com/wiki/Alvar_Julen", "builtIn":True, "isPlayer":False},
                "Vortt Baskk": {"name":"Vortt Baskk", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226826831298710/vortt_baskk.png", "aliases":["vortt","baskk"], "wiki":"https://galaxyonfire.fandom.com/wiki/Vortt_Baskk", "builtIn":True, "isPlayer":False},
                "Oluchi Erland": {"name":"Oluchi Erland", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226822540394546/oluchi_erland.png", "aliases":["oluchi","erland"], "wiki":"https://galaxyonfire.fandom.com/wiki/Oluchi_Erland", "builtIn":True, "isPlayer":False},
                "Orp Tsam": {"name":"Orp Tsam", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226823966720041/orp_tsam.png", "aliases":["orp", "tsam"], "wiki":"https://galaxyonfire.fandom.com/wiki/Orp_Tsam", "builtIn":True, "isPlayer":False},
                "Urr Sekant": {"name":"Urr Sekant", "faction":"vossk", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226825488990258/urr_sakant.png", "aliases":["urr", "sekant"], "wiki":"https://galaxyonfire.fandom.com/wiki/Urr_Sakant", "builtIn":True, "isPlayer":False},

                # Nivelian
                "Borsul Tarand": {"name":"Borsul Tarand", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226764948537374/borsul_tarand.png", "aliases":["borsul","tarand"], "wiki":"https://galaxyonfire.fandom.com/wiki/Borsul_Tarand", "builtIn":True, "isPlayer":False},
                "Malon Sentendar": {"name":"Malon Sentendar", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226767939207178/malon_sentendar.png", "aliases":["malon","sendendar"], "wiki":"https://galaxyonfire.fandom.com/wiki/Malon_Sentendar", "builtIn":True, "isPlayer":False},
                "Vilhelm Lindon": {"name":"Vilhelm Lindon", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226772812726302/vilhelm_lindon.png", "aliases":["vilhelm","lindon"], "wiki":"https://galaxyonfire.fandom.com/wiki/Vilhelm_lindon", "builtIn":True, "isPlayer":False},
                "Tamir Prakupy": {"name":"Tamir Prakupy", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226770707185664/tamir_prakupy.png", "aliases":["tamir"], "wiki":"https://galaxyonfire.fandom.com/wiki/Tamir_Prakupy", "builtIn":True, "isPlayer":False},
                "Merson Surr": {"name":"Merson Surr", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226769327521872/merson_surr.png", "aliases":["merson","surr"], "wiki":"https://galaxyonfire.fandom.com/wiki/Merson_Surr", "builtIn":True, "isPlayer":False},
                "Ganfor Kant": {"name":"Ganfor Kant", "faction":"nivelian", "icon":"https://cdn.discordapp.com/attachments/700683544103747594/711226766630584370/ganfor_kant.png", "aliases":["ganfor","kant"], "wiki":"https://galaxyonfire.fandom.com/wiki/Ganfor_Kant", "builtIn":True, "isPlayer":False}}

# To be populated during package init
builtInCriminalObjs = {}

longestBountyNameLength = 0
for fac in bountyNames:
    for name in bountyNames[fac]:
        if len(name) > longestBountyNameLength:
            longestBountyNameLength = len(name)

securityLevels = ["secure", "average", "risky", "dangerous"]

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

# To be populated during package init
builtInSystemObjs = {}

mapImageWithGraphLink = "https://cdn.discordapp.com/attachments/700683544103747594/700683693215318076/gof2_coords.png"
mapImageNoGraphLink = 'https://cdn.discordapp.com/attachments/700683544103747594/700683699334807612/Gof2_supernova_map.png'

helpStr = """*--=* __***BountyBot Commands***__ *=--*
:star: Here are my commands! Prefix commands with `!bb` - for example: `!bb help`
**<Angled brackets>** indicate *optional* arguments, **[square brackets]** indicate *required* arguments.```ini
[ MISCELLANEOUS ]

- help
    | Display information about all available commands.
- balance <userTag>
    | Get the credits balance of yourself, or a tagged user if one is given.
- stats <userTag>
    | Get various credits and bounty statistics about yourself, or a tagged user.
- leaderboard <-g|c|s|w>
    | Show the credits leaderboard. Give -g for the global leaderboard, not just this server.
    | Give -c for the CURRENT credits leaderboard, -s for the 'systems checked' leaderboard.
    | Give -w for the 'bounties won' leaderboard.                   E.g: !bb leaderboard -gs

[   GOF2 INFO   ]

- map
    | Send the complete GOF2 starmap.
- system [system]
    | Display information about a given system.
- make-route [startSystem], [endSystem]
    | Find the shortest route from startSystem to endSystem.
- criminal [criminal name]
    | Get information about a criminal, including their wiki page and name aliases.

[   BOUNTIES    ]

- bounties <faction>
    | If no faction is given, name all currently active bounties.
    | If a faction is given, show detailed info about its active bounties.
- route [name]
    | Get the named criminal's current route.
- check [system]
    | Check if any criminals are in the given system, arrest them, and get paid!```"""

helpIntro = """:star: Here are my commands! Prefix commands with `!bb` - for example: `!bb help`
**<Angled brackets>** indicate *optional* arguments, **[square brackets]** indicate *required* arguments."""

helpDict = {"__Miscellaneous__":{"**help**":"Display information about all available commands.",
                                "**balance** *<userTag>*":"Get the credits balance of yourself, or a tagged user if one is given.",
                                "**stats** *<userTag>*":"Get various credits and bounty statistics about yourself, or a tagged user.",
                                "**leaderboard** *<-g|-c|-s|-w>*":"Show the credits leaderboard. Give `-g` for the global leaderboard, not just this server.\n> Give `-c` for the current credits balance leaderboard.\n> Give `-s` for the 'systems checked' leaderboard.\n> Give `-w` for the 'bounties won' leaderboard.\nE.g: `!bb leaderboard -gs`",
                                "**criminal [name]**": "Get information about a named criminal.\nAlso gives the criminal's usable aliases for the bounties system."},
            "__GOF2 Info__":{"**map**":"Send the complete GOF2 starmap.",
                            "**system [system]**": "Display information about a given system.",
                            "**make-route [startSystem], [endSystem]**": "Find the shortest route from startSystem to endSystem."},
            "__Bounties__":{"**bounties** *<faction>*": "If no faction is given, name all currently active bounties.\nIf a faction is given, show detailed info about its active bounties.",
                            "**route [criminal name]**":"Get the named criminal's current route.",
                            "**check [system]**":"Check if any criminals are in the given system, arrest them, and get paid! 💰"}}

adminHelpStr = """*--=* __***BountyBot Admin Commands***__ *=--*
:star: Here are my administrator commands! Prefix commands with `!bb` - for example: `!bb help`
**<Angled brackets>** indicate *optional* arguments, **[square brackets]** indicate *required* arguments.```ini
- admin-help
   | Display information about admin-only commands.
- setchannel
    | Set the channel where BountyBot will send announcements (e.g new bounties)```"""

adminHelpIntro = """:star: Here are my administrator commands! Prefix commands with `!bb` - for example: `!bb help`
**<Angled brackets>** indicate *optional* arguments, **[square brackets]** indicate *required* arguments."""

adminHelpDict = {"__Miscellaneous__":{"**admin-help**":"Display information about admin-only commands.",
                                    "**set-announce-channel** *<off>*":"Set the channel where BountyBot will send announcements (e.g new bounties)\n> Use `!bb set-announce-channel off` to disable announcements.",
                                    "**set-play-channel** *<off>*":"Set the channel where BountyBot will send info about completed bounties\n> Use `!bb set-play-channel off` to disable completed bounty announcements."}}

numExtensions = ["th","st","nd","rd","th","th","th","th","th","th"]

terranIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013574331596850/terran.png"
vosskIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013681621893130/vossk.png"
midorianIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013601019691038/midorian.png"
nivelianIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013623257890857/nivelian.png"
neutralIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/rocket_1f680.png"
voidIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013699841687602/void.png"
errorIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/exclamation-mark_2757.png"
winIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/trophy_1f3c6.png"
rocketIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/rocket_1f680.png"

factionIcons = {"terran":terranIcon, "vossk":vosskIcon, "midorian":midorianIcon, "nivelian":nivelianIcon, "neutral":neutralIcon}
factionColours = {"terran":Colour.gold(), "vossk":Colour.dark_green(), "midorian":Colour.dark_red(), "nivelian":Colour.teal(), "neutral":Colour.purple()}
