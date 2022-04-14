from chess import Board, Move, LegalMoveGenerator
from chess import STARTING_FEN
import json
from random import choice

def _prep_response(code, resp_data):
    return {
        "statusCode": code,
        "body": json.dumps(resp_data)
    }
def new_match_handler(id, data):
    match = Board(fen=STARTING_FEN)
    data.update({"matchId": id, "result": "IN-PROGRESS"})
    if data.get('player'):
        data.update({"fen": match.fen()})     
    else:
        move = choice(list(match.legal_moves))
        match.push(move)
        data.update({"fen": match.fen()})
    return _prep_response(200, data)
        
def update_match_handler(id, data):
    match = Board(fen=data.get('fen'))
    move = choice(list(match.legal_moves))
    match.push(move)
    data.update({"fen": match.fen()})
    return _prep_response(200, data)


def delete_match_handler(id, data):
    #TODO: Implement
    raise NotImplemented

router = {
    "POST/match": new_match_handler,
    "PUT/match": update_match_handler,
    "DELETE/match": delete_match_handler,
}

def handler(event, context):

    print(event)
    route_key = f"{event.get('httpMethod')}{event.get('path')}"
    data = json.loads(event.get('body'))
    return router[route_key](context.aws_request_id, data)
