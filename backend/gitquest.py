import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Choose database based on environment
DATABASE_URL=postgresql://tosin:jgXBD3Yny6zMxdIymQnqfUMlUwV2cn0d@dpg-cveau2hc1ekc73edjlq0-a/blockchain_66q3  # Use PostgreSQL if available
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
app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/vnd.microsoft.icon")

@app.route("/")
def serve_frontend():
    return send_from_directory("frontend", "index.html")

# Execute Git Command Route
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
        storyline = {
            None: "Welcome to GitQuest! Your journey begins. Type 'git status' to start your adventure.",
            "Completed git status": "Great! You checked your repo status. Now, view your commit history using 'git log'.",
            "Completed git log": "Awesome! Now, list the branches using 'git branch'.",
            "Completed git branch": "Nice! Create a new branch with 'git checkout -b feature'.",
            "Completed git checkout": "You're doing well! Now, pull the latest changes with 'git pull'."
        }
        
        message = storyline.get(player.last_checkpoint, "You have completed all challenges!")
        return jsonify({"username": player.username, "checkpoint": player.last_checkpoint, "message": message})
    
    return jsonify({"error": "Player not found!"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
