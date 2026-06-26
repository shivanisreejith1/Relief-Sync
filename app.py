import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from database.db import close_db, init_db

app = Flask(__name__)
app.secret_key = 'disaster_relief_secret_2024'

from routes.auth import auth_bp
from routes.main import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.teardown_appcontext(close_db)

with app.app_context():
    init_db(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
