import os
from flask import Flask, request, jsonify
from flask import Flask, send_from_directory
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Choose database based on environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///gitquest.db")  # Use PostgreSQL if available
engine = create_engine(DATABASE_URL, echo=True)

# Database setup
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class PlayerProgress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    last_checkpoint = Column(String)

Base.metadata.create_all(engine)

# Flask app setup
app = Flask(__name__, static_folder="frontend")
CORS(app)

@app.route("/")
def serve_frontend():
    return send_from_directory("frontend", "index.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory("public", "favicon.ico", mimetype="image/vnd.microsoft.icon") 
    
@app.route("/")
def home():
    return "GitQuest API is running!"

@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    command = data.get("command")

    ALLOWED_COMMANDS = ["git status", "git log", "git branch", "git checkout", "git pull"]
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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
