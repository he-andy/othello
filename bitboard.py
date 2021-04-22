import numpy as np
import functools

class Board:

    shiftsL = np.array([
    (1, 0xFEFEFEFEFEFEFEFE), #LEFT
    (8, 0xFFFFFFFFFFFFFF00),
    (9, 0xFEFEFEFEFEFEFE00), 
    (7, 0x7F7F7F7F7F7F7F00)]).astype(np.uint64)

    shiftsR = np.array([
    (1, 0x7F7F7F7F7F7F7F7F), #RIGHT
    (8, 0x00FFFFFFFFFFFFFF),
    (9, 0x007F7F7F7F7F7F7F),
    (7, 0x00FEFEFEFEFEFEFE)]).astype(np.uint64)

    def __init__(self):
        self.history = np.array([[np.uint64(0b00010000 << 24 | 0b00001000 << 32), np.uint64(0b00001000 << 24 | 0b00010000 << 32)]])
        self.turn = np.bool(0)
    
    def convert2D(self, boards):
        pass
    
    @functools.lru_cache(None)
    def get_legal_moves(self, turn):
        current_state = self.history[-1]
        empty_positions = ~(current_state[0] | current_state[1]) & 0xFFFFFFFFFFFFFFFF
        opp = current_state[not turn]
        own = current_state[turn]
        moves = np.uint64(0)
        for s, b in Board.shiftsL:
            w = opp & b
            t = w & (own << s)
            t |= w & (t << s)
            t |= w & (t << s)
            t |= w & (t << s)
            t |= w & (t << s)
            t |= w & (t << s)
            moves |= (empty_positions & b & (t << s))
        for s, b in Board.shiftsR:
            w = opp & b
            t = w & (own >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            moves |= (empty_positions & b & (t >> s))
        return moves

    def play_move(self, turn, move):
        current_state = self.history[-1]
        opp = current_state[not turn]
        own = current_state[turn]

        captured_disks, new_disks = 0, 1 << move
        own |= new_disks
        for s, b in Board.shiftsL:
            w = opp & b
            t = w & (new_disks << s)
            t |= w & (t << s)
            t |= w & (t << s)
            t |= w & (t << s)
            t |= w & (t << s)
            t |= w & (t << s)
            bound = (b & (t << s) & own)
            captured_disks |= t if bound else 0
        for s, b in Board.shiftsR:
            w = opp & b
            t = w & (new_disks >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            bound = (b & (t >> s) & own)
            captured_disks |= t if bound else 0
        new_state = [0, 0]
        new_state[turn] = own ^ captured_disks
        new_state[not turn] = opp ^ captured_disks
        return np.array(new_state, dtype=np.uint64)
        
def main():
    b = Board()

if __name__ == '__main__':
    main()
