from .wheels import LETTERS, ROTORS, REFLECTORS


class PlugBoard():

    def __init__(self, pairs=None):
        self.wiring = self.wire_pairs(pairs)
        self.forward_map = {}
        self.backward_map = {}
        self.set_wiring_map(self.wiring)
        super().__init__()

    def wire_pairs(self, pairs):
        if pairs is None:
            return LETTERS

        wiring = list(LETTERS)
        for pair in pairs.split():
            wiring[LETTERS.index(pair[0])] = pair[1]
            wiring[LETTERS.index(pair[1])] = pair[0]
        return "".join(wiring)

    def set_wiring_map(self, wiring):
        self.forward_map = {k: v for k, v in zip(LETTERS, wiring)}
        self.backward_map = {k: v for k, v in zip(wiring, LETTERS)}

    def convert_forward(self, index):
        ltr = LETTERS[index]
        ltr = self.forward_map[ltr]
        return LETTERS.index(ltr)

    def convert_backward(self, index):
        ltr = LETTERS[index]
        ltr = self.backward_map[ltr]
        return LETTERS.index(ltr)


class Rotor:

    def __init__(self, name, initial_position="A", offset="A"):
        self.wiring = ROTORS[name]["wiring"]
        self.notch = ROTORS[name]["notch"]
        self.letters = LETTERS
        self.set_ringstellung(offset)
        self.set_position(initial_position)

    def convert_forward(self, index):
        ltr = self.wiring[index]
        return self.letters.index(ltr)

    def convert_backward(self, index):
        ltr = self.letters[index]
        return self.wiring.index(ltr)

    def set_ringstellung(self, offset):
        if offset == "A":
            return None

        offset = LETTERS.index(offset)
        self.letters = self.letters[offset:] + self.letters[:offset]
        self.wiring = "".join(
            [chr(ord(LETTERS[0]) + (ord(ltr)-ord(LETTERS[0])+offset) % len(LETTERS)) for ltr in self.wiring])

    def set_position(self, initial_position):
        index = self.letters.index(initial_position)
        self.wiring = self.wiring[index:] + self.wiring[:index]
        self.letters = self.letters[index:] + self.letters[:index]

    def step(self):
        self.wiring = self.wiring[1:] + self.wiring[:1]
        self.letters = self.letters[1:] + self.letters[:1]


class Reflector:

    def __init__(self, name):
        self.wiring = REFLECTORS[name]
        self.wiring_map = {k: v for k, v in zip(LETTERS, self.wiring)}

    def reflect(self, index):
        reflected_ltr = self.wiring_map[LETTERS[index]]
        return LETTERS.index(reflected_ltr)
