import os
import sys
import time
import threading
import logging
import json
from typing import Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify, request

from core.database.connection import (
    connect_sqlite,
    create_tables,
    fetch_one,
    fetch_all,
    execute,
)
from core.database.schemas import create_default_user
from core.game.mechanics import (
    initialize_game_mechanics,
    start_cultivation,
    calculate_cultivation_progress,
)
from core.utils.database import generate_universal_uid
from core.utils.account_status import get_user_status

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "core.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("core.server")

core_app = Flask(__name__)
core_app.config["JSON_AS_ASCII"] = False

server_running = False
server_thread: Optional[threading.Thread] = None


def initialize_core_components() -> bool:
    try:
        logger.info("Initialising core components ...")
        connect_sqlite()
        create_tables()
        initialize_game_mechanics()
        logger.info("Core components initialised")
        return True
    except Exception as exc:  # pragma: no cover - simple startup helper
        logger.error(f"Failed to initialise core components: {exc}")
        return False


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------
@core_app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})


@core_app.route("/api/user/lookup", methods=["GET"])
def lookup_user():
    platform = request.args.get("platform")
    platform_id = request.args.get("platform_id")
    if not platform or not platform_id:
        return jsonify({"success": False, "message": "Missing parameters"}), 400
    column = f"{platform}_id"
    row = fetch_one(
        f"SELECT user_id, lang, in_game_username FROM users WHERE {column} = ?",
        (platform_id,),
    )
    if not row:
        return jsonify({"success": False, "message": "User not found"}), 404
    return jsonify({
        "success": True,
        "user_id": row["user_id"],
        "lang": row.get("lang", "CHS"),
        "username": row.get("in_game_username")
    })


@core_app.route("/api/register", methods=["POST"])
def register_user():
    data = request.get_json(force=True)
    platform = data.get("platform")
    platform_id = data.get("platform_id")
    username = data.get("username") or platform_id
    lang = data.get("lang", "CHS").upper()

    if not platform or not platform_id:
        return jsonify({"success": False, "message": "Missing parameters"}), 400

    column = f"{platform}_id"
    existing = fetch_one(f"SELECT user_id, lang FROM users WHERE {column} = ?", (platform_id,))
    if existing:
        return jsonify({"success": False, "message": "User already exists", "user_id": existing["user_id"], "lang": existing.get("lang", "CHS")}), 400

    try:
        uid = generate_universal_uid()
    except Exception as exc:
        logger.error(f"UID generation error: {exc}")
        return jsonify({"success": False, "message": "UID generation failed"}), 500

    user_data = create_default_user(uid, username)
    user_data["lang"] = lang
    user_data["third_party_ids"] = {"discord": "", "telegram": "", "matrix": ""}
    user_data["third_party_ids"][platform] = platform_id

    execute(
        """
        INSERT INTO users (
            user_id, in_game_username, lang, state, exp, rank, dy_times,
            copper, gold, asc_reduction, sign, element, discord_id, telegram_id, matrix_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_data["user_id"],
            user_data["in_game_username"],
            user_data["lang"],
            int(user_data["state"]),
            user_data["exp"],
            user_data["rank"],
            user_data["dy_times"],
            user_data["copper"],
            user_data["gold"],
            user_data["asc_reduction"],
            int(user_data["sign"]),
            user_data["element"],
            user_data["third_party_ids"].get("discord"),
            user_data["third_party_ids"].get("telegram"),
            user_data["third_party_ids"].get("matrix"),
        ),
    )
    logger.info(f"Created account {uid} for {platform}:{platform_id}")
    return jsonify({"success": True, "user_id": uid})


@core_app.route("/api/stat/<user_id>", methods=["GET"])
def user_status(user_id):
    status = get_user_status(user_id)
    if not status:
        return jsonify({"success": False, "message": "User not found"}), 404
    return jsonify({"success": True, "status": status})


@core_app.route("/api/cultivate/start", methods=["POST"])
def cultivate_start():
    data = request.get_json(force=True)
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Missing user_id"}), 400

    user = fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if user.get("state"):
        return jsonify({"success": False, "message": "In cultivation"}), 400

    timing = start_cultivation(user_id, user.get("element"))
    execute(
        "INSERT INTO timings (user_id, start_time, type, base_gain) VALUES (?, ?, ?, ?)",
        (user_id, timing["start_time"], timing["type"], timing["base_gain"]),
    )
    execute("UPDATE users SET state = 1 WHERE user_id = ?", (user_id,))

    return jsonify({"success": True, "start_time": timing["start_time"], "gain_per_hour": timing["base_gain"]})


@core_app.route("/api/cultivate/end", methods=["POST"])
def cultivate_end():
    data = request.get_json(force=True)
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Missing user_id"}), 400

    user = fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if not user or not user.get("state"):
        return jsonify({"success": False, "message": "Not cultivating"}), 400

    timing = fetch_one("SELECT * FROM timings WHERE user_id = ? AND type = 'cultivation'", (user_id,))
    if not timing:
        return jsonify({"success": False, "message": "Timing missing"}), 400

    gain = calculate_cultivation_progress(timing)
    execute("DELETE FROM timings WHERE id = ?", (timing["id"],))
    execute("UPDATE users SET state = 0, exp = exp + ? WHERE user_id = ?", (gain, user_id))
    return jsonify({"success": True, "gain": gain})


@core_app.route("/api/cultivate/status/<user_id>", methods=["GET"])
def cultivate_status(user_id):
    user = fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    if not user.get("state"):
        return jsonify({"success": True, "state": False})

    timing = fetch_one("SELECT * FROM timings WHERE user_id = ? AND type = 'cultivation'", (user_id,))
    if not timing:
        return jsonify({"success": False, "message": "Timing missing"}), 400
    gain = calculate_cultivation_progress(timing)
    return jsonify({
        "success": True,
        "state": True,
        "start_time": timing["start_time"],
        "current_gain": gain,
    })


def load_config():
    """Load configuration from config.json"""
    path = os.path.join(PROJECT_ROOT, "config.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error(f"Failed to load config: {exc}")
        return {}


def run_core_server():
    global server_running
    server_running = True
    try:
        config = load_config()
        port = config.get("core_server", {}).get("port", 11450)
        logger.info(f"Starting core server on http://127.0.0.1:{port}")
        core_app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)
    except Exception as exc: 
        logger.error(f"Core server error: {exc}")
    finally:
        server_running = False


def start_server() -> bool:
    global server_thread, server_running
    if server_running:
        logger.info("Core server already running")
        return True
    if not initialize_core_components():
        return False
    server_thread = threading.Thread(target=run_core_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    logger.info("Core server started")
    return True


def stop_server():
    global server_running
    server_running = False
    logger.info("Core server stopped")


if __name__ == "__main__":
    if start_server():
        try:
            while server_running:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_server()
