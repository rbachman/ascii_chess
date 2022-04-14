from chess import Board, Move
from chess import STARTING_FEN
from ascii_chess.models import CONFIG_SCHEMA, MATCH_SCHEMA
from ascii_chess.banners import WELCOME_BANNER, WINNER_BANNER
from os import system
from time import sleep
import requests

#Builtin Imports
import sqlite3, os
from uuid import uuid4
from collections import namedtuple

def _clear_screen():
    system('clear')

class ChessMatch(Board):

    def __init__(self, fen=STARTING_FEN) -> None:
        super().__init__(fen, chess960=False)

class ChessMove:

    def __init__(self, move: str, board: ChessMatch) -> None:
        super().__init__()
        
        self.move = move
        self.board = board

    def parse_move(self):
        try:
            return Move.from_uci(self.move)
        except ValueError:
            try:
                return self.board.parse_san(self.move)
            except:
                raise AssertionError("Illegal Move")


class MatchManager():

    def __init__(self) -> None:
        
        self.state = ConfigLoader()

    @property
    def inProgress(self):
        
        Match = namedtuple('Match', ['matchId', 'fen', 'player','level','result'])
        self.state.connection.execute("SELECT * FROM match WHERE result = 'IN-PROGRESS'")
        results = self.state.connection.fetchall()
        matches = [ Match._make(m) for m in results ]
        return matches 
    
    @property
    def match_data(self):
        return {
            "matchId": self.matchId,
            "fen": self.fen,
            "player": self.player,
            "level": self.level,
            "result": self.result
        }
        
    def save(self):
        self.state.save(self.match_data)

    def create_match(self):
        _clear_screen()
        print("[1] White")
        print("[2] Black")
        choice = int(input("> "))
        if choice == 2:
            color = 0
        elif choice == 1:
            color = 1
        else:
            raise ValueError
        _clear_screen()
        print("Select CPU Difficulty.  Valide Range 1 - 20")
        level = int(input("> "))
        assert level >= 1 <= 20

        resp = requests.post(f"{self.state.server_url}/match", json={"player": color, "level": level}).json()
        for k, v in resp.items():
            setattr(self, k, v)
        self.save()
    
    def resume_match(self):
        _clear_screen()
        print("Select match to resume:")
        for idx,match in enumerate(self.inProgress):
            print(f"[{idx + 1}] FEN: {match.fen}")
        selection = int(input("> "))
        match = self.inProgress[selection - 1]
        for k,v in match._asdict().items():
            setattr(self, k, v)

    def complete_match(self):
        #TODO: Get Result, save result
        pass

    def play(self):

        board = Board(fen=self.fen)
        while not board.outcome():
            valid = False
            while not valid:
                try:
                    _clear_screen()
                    print(board)
                    print("--"*8)
                    print("Enter Your move")
                    uci = input("> ")
                    move = Move.from_uci(uci)
                    assert move in board.legal_moves
                    valid = True
                except AssertionError:
                    print("Illegal Move")
                    sleep(3)
            board.push(move)
            setattr(self, 'fen', board.fen())
            self.save()
            resp = requests.put(f"{self.state.server_url}/match", json=self.match_data).json()
            for k, v in resp.items():
                setattr(self, k, v)
            self.save()
            board = Board(fen=self.fen)
        
        result = board.outcome().result()
        print(result)
        setattr(self,'result',result)
        self.save()
        if int(result[0]) == self.player:
            print(WINNER_BANNER)
        else:
            print(LOSER_BANNER)
        

class ConfigLoader():

    def __init__(self) -> None:

        print(WELCOME_BANNER)

        def _prereq():
            root_dir = f"{os.path.expanduser('~')}/.ascii_chess"
            bootstrapped = False
            while not bootstrapped:
                if not os.path.isdir(root_dir):
                    os.mkdir(root_dir)
                    db = sqlite3.connect(f"{root_dir}/ac.db")
                    connection = db.cursor()
                    connection.execute(CONFIG_SCHEMA)
                    connection.execute(MATCH_SCHEMA)
                    print("Ascii Chess Server URL (Must start with https://)")
                    server_url = input("> ")
                    connection.execute(f"INSERT INTO config(clientId, url) VALUES (\"{str(uuid4())}\", \"{server_url}\")")
                    db.commit()
                    bootstrapped = True
                else:
                    db = sqlite3.connect(f"{root_dir}/ac.db")
                    connection = db.cursor()
                    connection.execute("SELECT url FROM config")
                    try: 
                        server_url = connection.fetchone()[0]
                        bootstrapped=True
                    except Exception:
                        os.rmdir(root_dir)
            return server_url, db, connection
        
        self.server_url, self.db, self.connection = _prereq()


    def save(self, matchData):
        self.connection.execute(f"SELECT * FROM match WHERE matchId = \"{matchData.get('matchId')}\"")
        match = self.connection.fetchone()
        if match:
            self.connection.execute(f"UPDATE match SET fen = \"{matchData.get('fen')}\", result = \"{matchData.get('result')}\" WHERE matchId = \"{matchData.get('matchId')}\"")
        else:
            print(type(self.connection))
            self.connection.execute(f"INSERT INTO match (matchId, fen, player, level, result) VALUES (\"{matchData['matchId']}\",\"{matchData['fen']}\",{matchData['player']},{matchData['level']},\"{matchData['result']}\")")
        self.db.commit()
        

