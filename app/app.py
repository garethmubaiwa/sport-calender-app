import sys
import os

# Makes sure Python can find modules when running from app/
sys.path.insert(0, os.path.dirname(__file__))

from flask  import Flask
from config import get_env_variable
from routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DB_CONFIG"] = get_env_variable()
    app.register_blueprint(bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
    # debug=True: auto-reloads on save, shows errors in browser.
    # NEVER use debug=True in production.