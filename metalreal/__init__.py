from flask import Flask
app = Flask(__name__)

from metalreal.redis_session import RedisSessionInterface
app.session_interface = RedisSessionInterface()

import metalreal.main
