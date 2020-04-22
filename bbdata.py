from bbutil import System

factions = ["terran", "vossk", "midorian", "nivelian", "neutral"]
bountyFactions = ["terran", "vossk", "midorian", "nivelian"]

bountyNames = {"terran": ["Pal Tyyrt", "Kehnor", "Gendol Ethor", "Korr Bekkt", "Hongar Meton"],
                "vossk": ["Mrrkt Nimkk", "Alvar Julen", "Vortt Baskk", "Oluchi Erland", "Orp Tsam"],
                "midorian": ["Toma Prakupy", "Nombur Talénah", "Bartholomeu Drew", "Doni Trillyx", "Mashon Redal"],
                "nivelian": ["Borsul Tarand", "Vilhelm Lindon", "Tamir Prakupy", "Merson Surr", "Ganfor Kant"]}

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
            "Behen": System("Behen", "nivelian", ["Nesla", "Suteo", "Weymire"], 2, (3, 6)),
            "Pareah": System("Pareah", "nivelian", ["Nesla"], 1, (2, 5)),
            "Nesla": System("Nesla", "nivelian", ["Behen", "Pareah", "Weymire", "Shima"], 2, (4, 3)),
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
- system-info [system]
    | Display information about a given system.
- make-route [startSystem], [endSystem]
    | Find the shortest route from startSystem to endSystem.

[   BOUNTIES    ]

- bounties <faction>
    | If no faction is given, name all currently active bounties.
    | If a faction is given, show detailed info about its active bounties.
- route [faction] [name]
    | Get the named criminal's route, from the faction's bounty board.
- check [system]
    | Check if any criminals are in the given system, arrest them, and get paid!```"""

adminHelpStr = """*--=* __***BountyBot Admin Commands***__ *=--*
:star: Here are my administrator commands! Prefix commands with `!bb` - for example: `!bb help`
**<Angled brackets>** indicate *optional* arguments, **[square brackets]** indicate *required* arguments.```ini
- admin-help
   | Display information about admin-only commands.
- setchannel
    | Set the channel where BountyBot will send announcements (e.g new bounties)```"""

numExtensions = ["th","st","nd","rd","th","th","th","th","th"]