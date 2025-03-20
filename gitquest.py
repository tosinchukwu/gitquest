import os

command = input("Enter a Git command: ")
os.system(command)  # Executes Git commands (security checks required)

def buggy_function():
    return 1 + "1"  # TypeError

try:
    buggy_function()
except TypeError:
    print("Fix the bug and commit your changes!")

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PlayerProgress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    last_checkpoint = Column(String)

engine = create_engine("sqlite:///gitquest.db")
Base.metadata.create_all(engine)

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    command = data.get("command")
    output = os.popen(command).read()
    return jsonify({"output": output})

if __name__ == "__main__":
    app.run(debug=True)
