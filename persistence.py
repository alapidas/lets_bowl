import random

from models import Player, Game, Frame


class DB(object):
    """ Our fake DB.  Meant to be a singleton.  Do not instantiate.  """
    # Maps of IDs to respective objects
    players = {}
    games = {}
    frames = {}

    @staticmethod
    def get(klass):
        """ Get the appropriate db 'table' for the class """
        return {
            Player: DB.players,
            Game: DB.games,
            Frame: DB.frames
        }[klass]


random.seed()
