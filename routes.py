from flask_restful import Resource, marshal_with, reqparse, abort

from models import Player, Game
from controllers import PlayerController as pc
from controllers import GameController as gc


class RestPlayer(Resource):
    @marshal_with(Player.serialize)
    def get(self, id):
        """ Get a player - example
        {
            'name': 'mario mario',
            'id': 123
        }
        """
        return pc.get(id) or abort(404)

    @marshal_with(Player.serialize)
    def post(self):
        """ Create a player, POST format:
        {
            'name': 'mario mario'
        }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='json', required=True)
        args = parser.parse_args()
        return pc.create(args['name'])

class RestGame(Resource):
    @marshal_with(Game.serialize)
    def get(self, id):
        """ Get a game - example
        {
            u'complete': False,
            u'current_frame': 1,
            u'current_player':
                {u'id': 62621, u'name': u'luigi'},
            u'frames': [
                {u'frames': [{u'score': 9, u'shots': [4, 5]}], u'pid': 61617},
                {u'frames': [], u'pid': 62621}
            ],
            u'id': 73360,
            u'players': [
                {u'id': 61617, u'name': u'mario'},
                {u'id': 62621, u'name': u'luigi'}
            ],
            u'started': True,
            u'totals': {u'61617': 9, u'62621': 0}
        }
        """
        return gc.get(id) or abort(404)

    @marshal_with(Game.serialize)
    def post(self):
        """ Create a game, POSTdata format:
        {
            'players': [123, 456, 789]
        }
        """
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
