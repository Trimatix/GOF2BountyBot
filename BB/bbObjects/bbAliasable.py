from abc import ABC, abstractmethod


class Aliasable (ABC):
    def __init__(self, name, aliases, forceAllowEmpty=False):
        if not name and not forceAllowEmpty:
            raise RuntimeError("ALIAS_CONS_NONAM: Attempted to create an aliasable with an empty name")
        self.name = name

        for alias in range(len(aliases)):
            if not aliases[alias] and not forceAllowEmpty:
                raise RuntimeError("ALIAS_CONS_EMPTALIAS: Attempted to create an aliasable with an empty alias")
            aliases[alias] = aliases[alias].lower()
        self.aliases = aliases

        if name.lower() not in aliases:
            self.aliases += [name.lower()]
    
    def __eq__(self, other):
        return type(other) == self.getType() and self.isCalled(other.name) or other.isCalled(self.name)

    def isCalled(self, name):
        return name.lower() == self.name.lower() or name.lower() in self.aliases

    def removeAlias(self, name):
        if name.lower() in self.aliases:
            self.aliases.remove(name.lower())

    def addAlias(self, name):
        if name.lower() not in self.aliases:
            self.aliases.append(name.lower())

    @abstractmethod
    def getType(self):
        pass
