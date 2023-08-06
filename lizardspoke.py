from itertools import repeat
from random import choice
from sys import argv
from time import sleep

from prettytable import ALL, PrettyTable

from anticheat import Anticheat

WELCOME_MESSAGE = 'Game against CPU started! Let me remind you the rules:'
FAREWELL_MESSAGE = 'GG WP'
HMAC_MESSAGE = 'CPU has made its mind (HMAC:{})'
INVALID_MOVES_NUMBER_MESSAGE = 'Game requires an odd number of moves >= 3 ({} given)' 
REPEARING_MOVES_MESSAGE = 'All moves should be unique!'
WRONG_INPUT_MESSAGE = 'Invalid move or command!'
MENU_HEADER = 'Available moves:\n'
MENU_FOOTER = '\n0 - exit\n? - help\nEnter your move:'


class Ruleset:
    def __init__(self, moves: list[str]):
        moves_number = len(moves)
        if moves_number < 3 or moves_number % 2 == 0:
            raise ValueError(INVALID_MOVES_NUMBER_MESSAGE.format(moves_number))
        if len(set(moves)) < moves_number:
            raise ValueError(REPEARING_MOVES_MESSAGE)
        self.moves_number = moves_number
        self.moves = moves
        self._moves_mapping = {move: index for index, move in enumerate(moves)}
        self.menu = MENU_HEADER + '\n'.join(
            [f'{i+1} - {move}' for i, move in enumerate(self.moves)]
        ) + MENU_FOOTER

    def compare_moves(self, move1: str, move2: str) -> int:
        difference = self._moves_mapping[move1] - self._moves_mapping[move2]
        if difference == 0:
            return 0
        threshold = self.moves_number // 2
        if 0 < difference <= threshold or difference < -threshold:
            return 1
        return 2

    def generate_rules_table(self) -> PrettyTable:
        rules = PrettyTable(field_names = ['P1\P2'] + self.moves)
        rules.hrules = ALL
        rules.add_rows(
            [[move1] + [f'P{winner} wins' if winner else 'Draw' for winner in map(
                self.compare_moves, repeat(move1), self.moves
            )] for move1 in self.moves]
        )
        return rules
    
    def parse(self, move):
        if move in self.moves:
            return move
        move = int(move)
        if move < 1 or move > self.moves_number:
            raise ValueError()
        return self.moves[move-1]


class SinglePlayerSession:
    OUTCOMES = ['Draw!', 'CPU won!', 'You won!']
    
    def __init__(self, moves):
        try:
            self.game = Ruleset(moves)
        except ValueError as e:
            raise ValueError(e)
        self.anticheat = Anticheat()
        print(WELCOME_MESSAGE, self.game.generate_rules_table(), sep='\n')
        self.player_move = None

    def play_round(self):
        cpu_move = choice(self.game.moves)
        hmac, key = self.anticheat.encipher(cpu_move)
        print(HMAC_MESSAGE.format(hmac), self.game.menu, sep='\n')
        while True:
            self.player_move = input()
            if self.player_move == '0':
                return 0
            if self.player_move == '?':
                print(self.game.generate_rules_table(), self.game.menu, sep='\n')
            else:
                try:
                    self.player_move = self.game.parse(self.player_move)
                    break
                except ValueError:
                    print(WRONG_INPUT_MESSAGE)
        print(
            self.OUTCOMES[self.game.compare_moves(cpu_move, self.player_move)],
            f'Your move: {self.player_move}; CPU move: {cpu_move}',
            f'HMAC key: {key}\n',
            sep='\n'
        )
            
    def exit(self):
        print(FAREWELL_MESSAGE)


def play_singleplayer(moves):
    try:
        session = SinglePlayerSession(moves)
    except ValueError as e:
        return print(e)
    while session.player_move != '0':
        session.play_round()
        sleep(2)
    session.exit()


if __name__ == '__main__':
    play_singleplayer(argv[1:])
