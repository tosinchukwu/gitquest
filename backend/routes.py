from flask import Blueprint, request, jsonify
import subprocess

api_routes = Blueprint("api", __name__)

@api_routes.route("/execute_git", methods=["POST"])
def execute_git():
    data = request.json
    command = data.get("command")

    try:
        result = subprocess.run(command.split(), capture_output=True, text=True)
        return jsonify({"output": result.stdout, "error": result.stderr})
    except Exception as e:
        return jsonify({"error": str(e)})
