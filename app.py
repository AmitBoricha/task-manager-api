from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

@app.route("/")
def home():
    return jsonify({"message": "Task Manager API is running"}), 200

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True)