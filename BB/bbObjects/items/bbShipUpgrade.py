class bbShipUpgrade:
    name = ""
    value = 0

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name