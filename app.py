from flask import Flask
from flask_restful import Api

app = Flask(__name__)
app.config.from_object(__name__)

from routes import RestPlayer, RestGame, RestFrameRecorder

api = Api(app)
api.add_resource(RestPlayer, '/player', '/player/<int:id>')
api.add_resource(RestGame, '/game', '/game/<int:id>')
api.add_resource(RestFrameRecorder, '/game/<int:gid>/player/<int:pid>/frame')
