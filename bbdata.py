class System:
    name = ""
    faction = ""
    neighbours = []
    security = -1
    coordinates = ()

    def __init__(self, name, faction, neighbours, security, coordinates):
        self.name = name
        self.faction = faction
        self.neighbours = neighbours
        self.security = security
        self.coordinates = coordinates


factions = ["terran", "vossk", "midorian", "nivelian", "neutral"]

bountyNames = {"terran": ["Pal Tyyrt", "Kehnor", "Gendol Ethor", "Korr Bekkt", "Hongar Meton"],
                "vossk": ["Mrrkt Nimkk", "Alvar Julen", "Vortt Baskk", "Oluchi Erland", "Orp Tsam"],
                "midorian": ["Toma Prakupy", "Nombur Talénah", "Bartholomeu Drew", "Doni Trillyx", "Mashon Redal"],
                "nivelian": ["Borsul Tarand", "Vilhelm Lindon", "Tamir Prakupy", "Merson Surr", "Ganfor Kant"]}

securityLevels = ["secure", "average", "risky", "dangerous"]

systems = { #Terran
            "Aquila": System("Aquila", "terran", ["Wolf-Reiser", "Loma", "Union"], 2, (9, 2)),
            "Augmenta": System("Augmenta", "terran", ["Weymire", "Magnetar", "V'ikka", "Buntta"], 0, (6, 6)), 
            "Beidan": System("Beidan", "terran", [], 0, (12, 6)),
            "Buntta": System("Buntta", "terran", ["Suteo", "Behen", "Augmenta", "V'ikka", "Pescal Inartu", "Pan"], 1, (5, 9)),
            "Magnetar": System("Magnetar", "terran", ["Union", "Oom'bak", "V'ikka", "Augmenta"], 0, (6, 8)),
            "Pan": System("Pan", "terran", ["Wolf", "Loma", "Union"], 2, (3, 11)),
            "Pescal Inartu": System("Pescal Inartu", "terran", ["Wolf", "Loma", "Union"], 2, (6, 12)),
            "Prospero‎": System("Prospero‎", "terran", ["Wolf", "Loma", "Union"], 2, (5, 10)),
            "Union‎": System("Union‎", "terran", ["Wolf", "Loma", "Union"], 1, (7, 4)),
            "Vulpes": System("Vulpes", "terran", ["Wolf", "Loma", "Union"], 2, (10, 7)),
            "Wolf-Reiser": System("Wolf-Reiser", "terran", ["Wolf", "Loma", "Union"], 0, (10, 3)),
            #Vossk
            "K'ontrr": System("K'ontrr", "vossk", ["S'kolptorr", "Ni'mrrod", "Me'enkk", "Wah'norr"], 3, (10, 11)),
            "Me'enkk": System("Me'enkk", "vossk", ["Ni'mrrod", "K'ontrr"], 3, (11, 12)),
            "Ni'mrrod": System("Ni'mrrod", "vossk", ["K'ontrr", "Me'enkk"], 3, (12, 12)),
            "Oom'bak": System("Oom'bak", "vossk", ["Magnetar", "Vulpes", "S'kolptorr", "V'ikka"], 1, (9, 8)),
            "S'kolptorr": System("S'kolptorr", "vossk", ["K'ontrr", "Oom'bak", "V'ikka"], 2, (9, 9)),
            "V'ikka": System("V'ikka", "vossk", ["Augmenta", "Buntta", "Magnetar", "Oom'bak", "S'kolptorr"], 1, (7, 8)),
            "Wah'norr": System("Wah'norr", "vossk", ["Ni'mrrod", "K'ontrr"], 3, (12, 8)),
            "Y'mirr": System("Y'mirr", "vossk", [], 3, (11, 9)),
            #Nivelian
            "Behen": System("Behen", "nivelian", ["Nesla", "Suteo", "Weymire"], 2, (3, 6)),
            "Pareah": System("Pareah", "nivelian", ["Nesla"], 1, (2, 5)),
            "Nesla": System("Nesla", "nivelian", ["Behen", "Pareah", "Weymire", "Shima"], 2, (4, 3)),
            "Suteo": System("Suteo", "nivelian", ["Behen", "Buntta"], 2, (3, 8)),
            "Weymire": System("Weymire", "nivelian", ["Augmenta", "Behen", "Union", "Nesla", "Shima"], 1, (6, 4)),
            #Midorian
            "Eanya": System("Eanya", "midorian", ["Eanya", "Ginoya"], 3, (2, 3)),
            "Ginoya": System("Ginoya", "midorian", ["Talidor", "Eanya"], 3, (2, 2)),
            "Loma": System("Loma", "midorian", ["Shima", "Union", "Aquila"], 3, (5, 1)),
            "Mido": System("Mido", "midorian", [], 3, (4, 2)),
            "Talidor": System("Talidor", "midorian", ["Ginoya"], 3, (3, 1)),
            #Neutral
            "Alda": System("Alda", "neutral", [], 3, (8, 13)),
            "Her Jaza": System("Her Jaza", "neutral", [], 3, (8, 12)),
            "Shima": System("Shima", "neutral", ["Loma", "Wemire", "Nesla"], 0, (5, 3)),
            "Skavac": System("Skavac", "neutral", [], 3, (10, 1)),
            "Skor Terpa": System("Skor Terpa", "neutral", [], 3, (7, 1))}
