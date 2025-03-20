import os
import subprocess
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
Base = declarative_base()
engine = create_engine("sqlite:///gitquest.db")
Session = sessionmaker(bind=engine)

class PlayerProgress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    last_checkpoint = Column(String)

Base.metadata.create_all(engine)

# Flask app
app = Flask(__name__)
CORS(app)

# Allowed Git commands for security
ALLOWED_COMMANDS = ["git status", "git log", "git branch", "git checkout", "git pull"]

def get_session():
    if 'session' not in g:
        g.session = Session()
    return g.session

@app.teardown_appcontext
def remove_session(exception=None):
    session = g.pop('session', None)
    if session is not None:
        session.close()

@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    command = data.get("command")

    if command not in ALLOWED_COMMANDS:
        return jsonify({"error": "Command not allowed!"}), 403

    try:
        result = subprocess.run(command.split(), capture_output=True, text=True, check=True)
        return jsonify({"output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr}), 500

@app.route('/save_progress', methods=['POST'])
def save_progress():
    session = get_session()
    data = request.json
    username = data.get("username")
    checkpoint = data.get("checkpoint")

    player = session.query(PlayerProgress).filter_by(username=username).first()

    if player:
        player.last_checkpoint = checkpoint
    else:
        player = PlayerProgress(username=username, last_checkpoint=checkpoint)
        session.add(player)

    session.commit()
    return jsonify({"message": "Progress saved!"})

@app.route('/get_progress/<username>', methods=['GET'])
def get_progress(username):
    session = get_session()
    player = session.query(PlayerProgress).filter_by(username=username).first()

    if not player:
        return jsonify({"error": "Player not found!"}), 404
    return jsonify({"username": player.username, "checkpoint": player.last_checkpoint})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Default to 5000
    app.run(host="0.0.0.0", port=port)
