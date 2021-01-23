# Libraries to create API
#import flask
"""
from flask import Flask
from resources.pgcb import pgcb

# Create Flask app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

app.register_blueprint(pgcb)

app.run()
"""

from flask import Flask
from flask_restful import Api
from resources.routes import initialize_routes
from resources.errors import errors

# Create Flask app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

api = Api(app, errors = errors)

initialize_routes(api)

app.run(host = "127.0.0.1", port = 5000)