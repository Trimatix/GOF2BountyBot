from bbutil import System

factions = ["terran", "vossk", "midorian", "nivelian", "neutral"]
bountyFactions = ["terran", "vossk", "midorian", "nivelian"]

bountyNames = {"terran": ["Pal Tyyrt", "Kehnor", "Gendol Ethor", "Korr Bekkt", "Hongar Meton"],
                "vossk": ["Mrrkt Nimkk", "Alvar Julen", "Vortt Baskk", "Oluchi Erland", "Orp Tsam"],
                "midorian": ["Toma Prakupy", "Nombur Talenah", "Bartholomeu Drew", "Doni Trillyx", "Mashon Redal"],
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
                "Nombur Talenah": "https://cdn.discordapp.com/attachments/700683544103747594/711226703703310397/nombur_talenah.png",
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

longestBountyNameLength = 0
for fac in bountyNames:
    for name in bountyNames[fac]:
        if len(name) > longestBountyNameLength:
            longestBountyNameLength = len(name)

securityLevels = ["secure", "average", "risky", "dangerous"]

systems = { #Terran
            "Aquila": System("Aquila", "terran", ["Wolf-Reiser", "Loma", "Union"], 2, (9, 2)),
            "Augmenta": System("Augmenta", "terran", ["Weymire", "Magnetar", "V'Ikka", "Buntta"], 0, (6, 6)), 
            "Beidan": System("Beidan", "terran", [], 0, (12, 6)),
            "Buntta": System("Buntta", "terran", ["Suteo", "Behen", "Augmenta", "V'Ikka", "Pescal Inartu", "Pan"], 1, (5, 9)),
            "Magnetar": System("Magnetar", "terran", ["Union", "Oom'Bak", "V'Ikka", "Augmenta"], 0, (6, 8)),
            "Pan": System("Pan", "terran", ["Buntta", "Pescal Inartu"], 2, (3, 11)),
            "Pescal Inartu": System("Pescal Inartu", "terran", ["Pan", "Buntta"], 2, (6, 12)),
            "Prospero": System("Prospero", "terran", ["Union", "Vulpes"], 2, (5, 10)),
            "Union": System("Union", "terran", ["Loma", "Aquila", "Prospero", "Magnetar", "Weymire"], 1, (7, 4)),
            "Vulpes": System("Vulpes", "terran", ["Prospero", "Oom'Bak"], 2, (10, 7)),
            "Wolf-Reiser": System("Wolf-Reiser", "terran", ["Aquila"], 0, (10, 3)),
            #Vossk
            "K'Ontrr": System("K'Ontrr", "vossk", ["S'Kolptorr", "Ni'Mrrod", "Me'Enkk"], 3, (10, 11)),
            "Me'Enkk": System("Me'Enkk", "vossk", ["Ni'Mrrod", "K'Ontrr"], 3, (11, 12)),
            "Ni'Mrrod": System("Ni'Mrrod", "vossk", ["K'Ontrr", "Me'Enkk"], 3, (12, 12)),
            "Oom'Bak": System("Oom'Bak", "vossk", ["Magnetar", "Vulpes", "S'Kolptorr", "V'Ikka"], 1, (9, 8)),
            "S'Kolptorr": System("S'Kolptorr", "vossk", ["K'Ontrr", "Oom'Bak", "V'Ikka"], 2, (9, 9)),
            "V'Ikka": System("V'Ikka", "vossk", ["Augmenta", "Buntta", "Magnetar", "Oom'Bak", "S'Kolptorr"], 1, (7, 8)),
            "Wah'Norr": System("Wah'Norr", "vossk", [], 3, (12, 8)),
            "Y'Mirr": System("Y'Mirr", "vossk", [], 3, (11, 9)),
            #Nivelian
            "Behen": System("Behen", "nivelian", ["Nesla", "Suteo", "Weymire", "Buntta"], 2, (3, 6)),
            "Pareah": System("Pareah", "nivelian", ["Nesla"], 1, (2, 5)),
            "Nesla": System("Nesla", "nivelian", ["Behen", "Pareah", "Weymire", "Shima", "Eanya"], 2, (4, 3)),
            "Suteo": System("Suteo", "nivelian", ["Behen", "Buntta"], 2, (3, 8)),
            "Weymire": System("Weymire", "nivelian", ["Augmenta", "Behen", "Union", "Nesla", "Shima"], 1, (6, 4)),
            #Midorian
            "Eanya": System("Eanya", "midorian", ["Nesla", "Ginoya"], 3, (2, 3)),
            "Ginoya": System("Ginoya", "midorian", ["Talidor", "Eanya"], 3, (2, 2)),
            "Loma": System("Loma", "midorian", ["Shima", "Union", "Aquila"], 3, (5, 1)),
            "Mido": System("Mido", "midorian", [], 3, (4, 2)),
            "Talidor": System("Talidor", "midorian", ["Ginoya"], 3, (3, 1)),
            #Neutral
            "Alda": System("Alda", "neutral", [], 3, (8, 13)),
            "Her Jaza": System("Her Jaza", "neutral", [], 3, (8, 12)),
            "Shima": System("Shima", "neutral", ["Loma", "Weymire", "Nesla"], 0, (5, 3)),
            "Skavac": System("Skavac", "neutral", [], 3, (10, 1)),
            "Skor Terpa": System("Skor Terpa", "neutral", [], 3, (7, 1))}

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
                                "**leaderboard** *<-g|-c|-s|-w>*":"Show the credits leaderboard. Give `-g` for the global leaderboard, not just this server.\n> Give `-c` for the current credits balance leaderboard.\n> Give `-s` for the 'systems checked' leaderboard.\n> Give `-w` for the 'bounties won' leaderboard.\nE.g: `!bb leaderboard -gs`"},
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

numExtensions = ["th","st","nd","rd","th","th","th","th","th"]

terranIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013574331596850/terran.png"
vosskIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013681621893130/vossk.png"
midorianIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013601019691038/midorian.png"
nivelianIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013623257890857/nivelian.png"
neutralIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/rocket_1f680.png"
voidIcon = "https://cdn.discordapp.com/attachments/700683544103747594/711013699841687602/void.png"
errorIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/exclamation-mark_2757.png"
winIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/trophy_1f3c6.png"
rocketIcon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/248/rocket_1f680.png"