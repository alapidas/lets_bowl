import app

import pytest
import json
from pprint import pprint


class Struct:
    """ Stolen from
    http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
    """
    def __init__(self, **entries):
        self.__dict__.update(entries)

@pytest.fixture(scope='module')
def client():
    return app.app.test_client()

def test_add_players(client):
    resp = client.post('/player',
                      data=json.dumps(dict(name='andy')),
                      content_type='application/json')
    jresp = json.loads(resp.data)
    assert jresp['name'] == 'andy'
    resp = client.get('/player/%s' % jresp['id'])
    jresp = json.loads(resp.data)
    assert jresp['name'] == 'andy'

def test_game(client):
    # Make players
    resp = client.post('/player',
                      data=json.dumps(dict(name='mario')),
                      content_type='application/json')
    mario = json.loads(resp.data)
    resp = client.post('/player',
                      data=json.dumps(dict(name='luigi')),
                      content_type='application/json')
    luigi = json.loads(resp.data)
    resp = client.post('/game',
                      data=json.dumps(dict(players=[mario['id'], luigi['id']])),
                      content_type='application/json')
    game = json.loads(resp.data)
    # TODO: Some assertions
    # post a frame
    resp = client.post('/game/%s/player/%s/frame' % (game['id'], mario['id']),
                       data=json.dumps(dict(shots=[4,5])),
                       content_type='application/json')
    game = Struct(**json.loads(resp.data))
    assert len(game.frames) == 2
    assert game.complete == False
    assert game.started == True
    assert game.current_player['id'] == luigi['id']

    # And so on and so forth

