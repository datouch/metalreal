from flask import Flask
from werkzeug.datastructures import ImmutableDict

app = Flask(__name__)

from metalreal.redis_session import RedisSessionInterface
app.session_interface = RedisSessionInterface()

#app.jinja_options = ImmutableDict(extensions=['jinja2.ext.with_'])

import metalreal.main
