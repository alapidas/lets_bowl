from models import Player, Game, Frame, ModelException
from persistence import DB

from flask_restful import abort

# TODO: The controller is tightly coupled to the HTTP handlers.  It would be
# nicer to have a shim inbetween that could translate errors (would decouple
# the two)

class Controller(object):
    """ Main controller object to subclass other controllers from.  Contains
    some common logic.

    TODO: De-dupe the create methods - requires a factory of sorts to create the
    model objects
    """

    # override this is the subclass to be the main class that the controller
    # is responsible for
    klass = None

    @classmethod
    def get(cls, id):
        """ Get a model object.  Takes an int ID of the object """
        return DB.get(cls.klass).get(id)


class PlayerController(Controller):
    """ The controller for players """

    klass = Player

    @staticmethod
    def create(name):
        """ Create a player.  Takes a player name.  Returns a valid flask_restful
        response. """
        p = Player(name)
        DB.players[p.id] = p
        p = DB.players.get(p.id)
        return p


class GameController(Controller):
    """ The controller for games """

    klass = Game

    @staticmethod
    def create(players):
        """ Create a game.  Requires a list of player IDs.  Returns a valid flask_restful
        response """
        if not players:
            abort(422, message="Must provide a list of players to create a game")
        players = [DB.players.get(id) or id for id in players[:]]
        bad_players = filter(lambda p: type(p) == int, players)
        if len(bad_players) > 0:
            abort(422, message="Cannot create game with nonexistent player(s): %s" %
                  ", ".join(str(p) for p in bad_players))
        g = Game(players)
        DB.games[g.id] = g
        return DB.games.get(g.id)

    @staticmethod
    def frame_for_player(gid, pid, shots):
        """ Add a frame to a player's frames in a game.  Takes the game ID, player
        ID, and a list of shots for the frame.  Returns a full copy of the game.
        """
        game = DB.get(Game).get(gid)
        if not game:
            abort(422, message="Unable to locate game %s" % gid)
        player = DB.get(Player).get(pid)
        if not player:
            abort(422, message="Unable to locate player %s" % pid)
        if player not in game.players:
            abort(400, message="Player %s is not participating in game %s" %
                  (player.name, gid))
        # convert to model shots
        shots = [ Frame.Shot.convert(shot) for shot in shots[:] ]
        try:
            game.post_frame(player, shots)
        except ModelException as e:
            abort (500, e.message)
        return DB.get(Game).get(gid)


