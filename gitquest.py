import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
Base = declarative_base()
engine = create_engine("sqlite:///gitquest.db")
Session = sessionmaker(bind=engine)
session = Session()

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

@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    command = data.get("command")

    if command not in ALLOWED_COMMANDS:
        return jsonify({"error": "Command not allowed!"}), 403

    output = os.popen(command).read()
    return jsonify({"output": output})

@app.route('/save_progress', methods=['POST'])
def save_progress():
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
    player = session.query(PlayerProgress).filter_by(username=username).first()
    
    if player:
        return jsonify({"username": player.username, "checkpoint": player.last_checkpoint})
    else:
        return jsonify({"error": "Player not found!"}), 404

if __name__ == "__main__":
    app.run(debug=True)
