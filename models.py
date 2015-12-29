import sys
import random
from collections import OrderedDict
from itertools import cycle

from flask_restful import fields, marshal

from enum import IntEnum


class ModelException(Exception):
    pass


class RestableMixin(object):
    """ A mixin that every model class should use.  Used to add things you'd
    have in a real app, like IDs.

    TODO: Make this more of a mixin than a base class to avoid MRO issues
    with multiple inheritance
    """

    # Serializable attribtues
    serialize = {
        'id': fields.Integer
    }

    def __init__(self):
        """ Generate an ID and add it to myself """
        self.id = random.randint(1, 100000)


class Frame(object): # Not a RestableMixin
    """ A single frame for a single player. """

    class Shot(IntEnum):
        """ A shot represents a single shot in a frame.  A 'nil' shot would be
        the shot after a strike.  A 'notyet' shot represents a shot that
        hasn't been taken yet. """
        notyet = -4
        nil = -3
        spare = -2
        strike = -1
        zero = 0
        one = 1
        two = 2
        three = 3
        four = 4
        five = 5
        six = 6
        seven = 7
        eight = 8
        nine = 9

        @classmethod
        def convert(cls, marking):
            """ Convert a common marking on a scorecard to a Shot value.
            Specifically, 'X' and '/' map to 'strike' and 'spare', respectively.
            The allowable set of values for `marking` is:
                (0-9, 'X', '/', None)
            """
            theshot = {
                'X': cls.strike,
                '/': cls.spare,
                None: cls.nil
            }.get(marking)
            if not theshot:
                return cls(marking)

    # Serializable attribtues
    serialize = {
        'score': fields.Integer,
        'shots': fields.List(
            #fields.Nested(Shot.serialize)
            fields.Integer
        )
    }

    def __init__(self, player):
        """ Create a frame
            :param player: Person whose frame this is
        """
        super(Frame, self).__init__()
        self.player = player
        self.score = 0
        self.shots = [Frame.Shot.notyet, Frame.Shot.notyet]
        # Whether or not the score is complete on this frame (for example, this
        # would not be set on a frame that had a spare until the next frame was
        # complete).  Technically, only one shot out of the next frame has to
        # be complete in that example, but this API only allows posting full
        # frames.
        self.complete = False

    def is_open(self):
        """ Determine if a frame is open. """
        return self.shots[0] != Frame.Shot.strike and self.shots[1] != Frame.Shot.spare

    def strike(self):
        return self.shots[0] == Frame.Shot.strike

    def spare(self):
        return self.shots[1] == Frame.Shot.spare


class Player(RestableMixin):
    """ An object representing a player during a game """

    # Serializable attribtues
    serialize = dict({
        'name': fields.String,
    }, **RestableMixin.serialize)

    apples = {'id': fields.Integer}

    def __init__(self, name):
        super(Player, self).__init__()
        self.name = name


class Game(RestableMixin):
    """ A single game ob bowling - can consist of an arbitrary number of
    players.

    Games are stateful.  The states of a game mimic the steps of a real game.

    Each game consists of 10 frames.  Games are tightly coupled to frames in
    this implementation; frames are per player per round.  That is, to say, a
    frame represents one player's single frame.
    """

    class PlayerFrameMapItem(object):
        """ This class is a _terrible_ hack to get serilization working
        with flask_restful.  Forgive me, for I have sinned.

        Store a player ID + frames together in an object
        """

        serialize = {
            'pid': fields.Integer,
            'frames': fields.List(
                fields.Nested(Frame.serialize)
            )
        }

        def __init__(self, pid):
            self.pid = pid
            self.frames = []

    # Serializable attribtues
    serialize = dict({
        'players': fields.List(
            fields.Nested(Player.serialize)
        ),
        'current_frame': fields.Integer,
        'started': fields.Boolean,
        'complete': fields.Boolean,
        'current_player': fields.Nested(
            Player.serialize,
            allow_null=True
        ),
        'frames': fields.List(
            fields.Nested(PlayerFrameMapItem.serialize)
        ),
        'totals': fields.Raw
    }, **RestableMixin.serialize)

    def __init__(self, players):
        """ Create a new game
            :param players: iterable of Player(s) for the game - the iteration
            order of this will be the order of players turns'
        """
        super(Game, self).__init__()
        self.players = list(players) # make a predictable iteration order
        self._players = cycle(self.players) # TODO - Check for dupes
        self.current_frame = None
        self.started = False
        self.complete = False
        self.current_player = None
        # map of playerID -> running scores
        self.totals = OrderedDict()
        # List of PlayerFrameMapItems to hold frames per player
        self.frames = []
        for p in self.players:
            self.totals[p.id] = 0
            self.frames.append(Game.PlayerFrameMapItem(p.id))

    def get_frames(self, pid):
        """ A helper to get played frames for a given player ID """
        return [ f for f in self.frames if f.pid == pid ][0].frames

    def start(self):
        """ Start a game.  This will do any necesary initialization, and should
        only be called once """
        if self.started:
            raise ModelException('Unable to start already started game')
        self.current_frame = 1
        self.current_player = next(self._players)
        self.started = True

    def post_frame(self, player, shots):
        """ Post a frame for a player.  Player is the player, and shots is
        an iterable of 2 shots to post. """
        if self.complete:
            raise ModelException('Game is complete - cannot accpet new frames')
        if not self.started:
            self.start()
        if self.current_player.id != player.id:
            raise ModelException('Posting frame for incorrect player')
        # Create the frame
        frame = Frame(player)
        frame.shots = shots
        if frame.is_open():
            frame.score = sum(frame.shots)
            frame.complete = True
        #player_frames = self.frames[player.id]
        # Get the appropriate PlayerFrameMapItem
        player_frames = self.get_frames(player.id)
        player_frames.append(frame)
        # Deal with any non-open frames, which appear to NOT be called
        # closed frames, which apparently would make too much sense
        if any(filter(lambda f: not f.complete, player_frames)):
            # Deal with a strike 2 frames back
            if len(player_frames) >= 3 and not player_frames[-3].complete:
                if player_frames[-1].strike():
                    player_frames[-3].score = 30
                    player_frames[-3].complete = True
            # Deal with a strike/spare 1 frame back
            if len(player_frames) >= 2 and not player_frames[-2].complete:
                if player_frames[-2].strike():
                    if player_frames[-1].strike():
                        pass
                    elif player_frames[-1].spare():
                        player_frames[-2].score = 20
                        player_frames[-2].complete = True
                    else:
                        player_frames[-2].score = 10 + player_frames[-1].score
                        player_frames[-2].complete = True
                if player_frames[-2].spare():
                    if player_frames[-1].strike():
                        player_frames[-2].score = 20
                        player_frames[-2].complete = True
                    else:
                        player_frames[-2].score = 10 + player_frames[-1].shots[0]
                        player_frames[-2].complete = True

        # Update total running score for player
        total = sum(f.score for f in player_frames)
        self.totals[player.id] = total

        # All players have completed a frame in the round
        if len(set(map(len, [ f.frames for f in self.frames ]))) == 1:
            if self.current_frame == 10:
                self.complete = True
            self.current_frame += 1

        self.current_player = next(self._players)

        return self

