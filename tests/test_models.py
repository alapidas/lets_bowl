from models import Player, Game, Frame, ModelException

import pytest
from pprint import pprint


class TestPlayer(object):
    def test_create_player(self):
        p = Player('Mario Mario')
        assert p.name == 'Mario Mario'


class TestGame(object):
    def _make_game(self):
        p1 = Player('Mario Mario')
        p2 = Player('Luigi Mario')
        p3 = Player('King Koopa')
        g = Game([p1, p2, p3])
        return g, p1, p2, p3

    def test_create_game(self):
        g, p1, p2, p3 = self._make_game()
        for real, expected in zip(g.players, [p1, p2, p3]):
            assert real == expected

    def test_start_game(self):
        g, p1, p2, p3 = self._make_game()
        g.start()
        assert g.current_player == p1
        assert g.current_frame == 1
        assert g.started == True
        with pytest.raises(ModelException):
            g.start()

    def test_post_frames(self):
        """ Note the README.  I realize that games ended up not being very
        testable the way the model is created.  There are a number of different
        scenarios to test here.

        TODO: Make games more testable
        """
        g, p1, p2, p3 = self._make_game()
        with pytest.raises(ModelException):
            # wrong player
            g.post_frame(p2, [Frame.Shot.zero, Frame.Shot.one])

        # Frame #1

        g.post_frame(p1, [Frame.Shot.zero, Frame.Shot.one])
        assert len(g.get_frames(p1.id)) == 1
        assert len(g.get_frames(p2.id)) == 0
        assert len(g.get_frames(p3.id)) == 0
        assert g.totals[p1.id] == 1
        assert g.totals[p2.id] == 0
        assert g.totals[p3.id] == 0
        assert g.get_frames(p1.id)[0].score == 1
        assert g.get_frames(p1.id)[0].complete == True

        g.post_frame(p2, [Frame.Shot.three, Frame.Shot.spare])
        assert len(g.get_frames(p1.id)) == 1
        assert len(g.get_frames(p2.id)) == 1
        assert len(g.get_frames(p3.id)) == 0
        assert g.totals[p1.id] == 1
        assert g.totals[p2.id] == 0
        assert g.totals[p3.id] == 0
        assert g.get_frames(p2.id)[0].score == 0
        assert g.get_frames(p2.id)[0].complete == False

        g.post_frame(p3, [Frame.Shot.strike, Frame.Shot.nil])
        assert len(g.get_frames(p1.id)) == 1
        assert len(g.get_frames(p2.id)) == 1
        assert len(g.get_frames(p3.id)) == 1
        assert g.totals[p1.id] == 1
        assert g.totals[p2.id] == 0
        assert g.totals[p3.id] == 0
        assert g.get_frames(p3.id)[0].score == 0
        assert g.get_frames(p3.id)[0].complete == False

        assert g.current_frame == 2

        # Frame #2 - Fight!

        g.post_frame(p1, [Frame.Shot.three, Frame.Shot.six])
        assert len(g.get_frames(p1.id)) == 2
        assert len(g.get_frames(p2.id)) == 1
        assert len(g.get_frames(p3.id)) == 1
        assert g.totals[p1.id] == 10
        assert g.totals[p2.id] == 0
        assert g.totals[p3.id] == 0
        assert g.get_frames(p1.id)[1].score == 9
        assert g.get_frames(p1.id)[1].complete == True

        g.post_frame(p2, [Frame.Shot.three, Frame.Shot.four])
        assert len(g.get_frames(p1.id)) == 2
        assert len(g.get_frames(p2.id)) == 2
        assert len(g.get_frames(p3.id)) == 1
        assert g.totals[p1.id] == 10
        assert g.totals[p2.id] == 20
        assert g.totals[p3.id] == 0
        assert g.get_frames(p2.id)[0].score == 13
        assert g.get_frames(p2.id)[1].score == 7
        assert g.get_frames(p2.id)[0].complete == True
        assert g.get_frames(p2.id)[1].complete == True

        g.post_frame(p3, [Frame.Shot.four, Frame.Shot.spare])
        assert len(g.get_frames(p1.id)) == 2
        assert len(g.get_frames(p2.id)) == 2
        assert len(g.get_frames(p3.id)) == 2
        assert g.totals[p1.id] == 10
        assert g.totals[p2.id] == 20
        assert g.totals[p3.id] == 20
        assert g.get_frames(p3.id)[0].score == 20
        assert g.get_frames(p3.id)[1].score == 0
        assert g.get_frames(p3.id)[0].complete == True
        assert g.get_frames(p3.id)[1].complete == False

        assert g.current_frame == 3


class TestFrame(object):
    def test_create_frame(self):
        p1 = Player('Mario Mario')
        f1 = Frame(p1)
        assert f1.score == 0
        assert f1.player == p1
        assert f1.shots == [Frame.Shot.notyet, Frame.Shot.notyet]
