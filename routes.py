from flask_restful import Resource, marshal_with, reqparse, abort

from models import Player, Game
from controllers import PlayerController as pc
from controllers import GameController as gc


class RestPlayer(Resource):
    @marshal_with(Player.serialize)
    def get(self, id):
        return pc.get(id) or abort(404)

    @marshal_with(Player.serialize)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='json', required=True)
        args = parser.parse_args()
        return pc.create(args['name'])

class RestGame(Resource):
    @marshal_with(Game.serialize)
    def get(self, id):
        return gc.get(id) or abort(404)

    @marshal_with(Game.serialize)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('players', type=list, location='json', required=True)
        args = parser.parse_args()
        return gc.create(args['players'])

class RestFrameRecorder(Resource):
    """ This REST resource is purpouse-built for recording frames.
    {
        "shots": [7, "/"]
    }
    """
    @marshal_with(Game.serialize)
    def post(self, gid, pid):
        parser = reqparse.RequestParser()
        parser.add_argument('shots', type=list, location='json', required=True)
        args = parser.parse_args()
        return gc.frame_for_player(gid, pid, args['shots'])
