import numpy as np
import functools

class Board:

    shiftsL = np.array([
    (1, 0xFEFEFEFEFEFEFEFE), #LEFT
    (8, 0xFFFFFFFFFFFFFF00),
    (9, 0xFEFEFEFEFEFEFE00), 
    (7, 0x7F7F7F7F7F7F7F00)], dtype=np.uint64)

    shiftsR = np.array([
    (1, 0x7F7F7F7F7F7F7F7F), #RIGHT
    (8, 0x00FFFFFFFFFFFFFF),
    (9, 0x007F7F7F7F7F7F7F),
    (7, 0x00FEFEFEFEFEFEFE)], dtype=np.uint64)

    def __init__(self):
        self.history = np.array([[np.uint64(0b00010000 << 24 | 0b00001000 << 32), np.uint64(0b00001000 << 24 | 0b00010000 << 32)]])
        self.turn = np.bool(0) #True = White, False = Black
    
    @functools.lru_cache(None)
    def get_legal_moves(self, bitboard=None, turn=None):
        if bitboard == None: bitboard = self.history[-1]
        move_list = np.uint64(0)
        empty_positions = (~(bitboard[0] | bitboard[1])) & np.uint64(0xFFFFFFFFFFFFFFFF)
        opp = bitboard[int(not turn)]
        own = bitboard[int(turn)]
        for s, b in Board.shiftsL:
            w = opp & b
            t = w & (own << s)
            t |= w & (t << s)
            t |= w & (t << s)
            t |= w & (t << s)
            t |= w & (t << s)
            t |= w & (t << s)
            move_list |= (empty_positions & b & (t << s))
        for s, b in Board.shiftsR:
            w = opp & b
            t = w & (own >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            move_list |= (empty_positions & b & (t >> s))
        return move_list

    def play_move(self, move, bitboard=None, turn=None, change_turn=True, update_history=True):
        if bitboard == None or turn == None: 
            bitboard, turn = self.history[-1], self.turn
            if change_turn: self.turn = not self.turn
        opp = bitboard[int(not turn)]
        own = bitboard[int(turn)]
        captured_disks, new_disks = np.uint64(0), np.uint64(1 << move)
        print(new_disks)
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
            captured_disks |= t if bound else np.uint64(0)

        for s, b in Board.shiftsR:
            w = opp & b
            t = w & (new_disks >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            t |= w & (t >> s)
            bound = (b & (t >> s) & own)
            captured_disks |= t if bound else np.uint64(0)
        new_state = [0, 0]
        new_state[turn] = own ^ captured_disks
        new_state[not turn] = opp ^ captured_disks
        new_state = np.array(new_state, dtype=np.uint64)
        self.history = np.concatenate((self.history, np.atleast_2d(new_state)))
        return new_state

    def convert_to_movelist(self, moves):
        return np.array([i for i in range(64) if np.uint64(1 << i) & moves > 0])

    def convert_single_to_matrix(self, bitboard):
        x = lambda a : np.array([np.uint64(1 << i) & a > 0 for i in range(64)]).astype(np.int8)
        return np.reshape(x(bitboard), (8, 8))

    def convert_to_matrix(self, bitboard=None, turn=None): #converts bitboard to matrix from the perspective of the turn given
        if bitboard == None: bitboard = self.history[-1]
        x = lambda a : np.array([np.uint64(1 << i) & a > 0 for i in range(64)]).astype(np.int8)
        return np.reshape(np.zeros(64, dtype=np.int8) + x(bitboard[int(turn)]) - x(bitboard[int(not turn)]), (8, 8))

def main():
    b = Board()
    print(b.convert_to_matrix(None, False))
    print(b.convert_single_to_matrix(b.get_legal_moves(turn=False)))
    print(b.convert_to_movelist(b.get_legal_moves(turn=False)))
    b.play_move(19)
    print(b.convert_to_matrix(None, True))


if __name__ == '__main__':
    main()
