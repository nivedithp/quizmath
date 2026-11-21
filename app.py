
import os
import re
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient, DESCENDING
from pymongo.errors import PyMongoError

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "number-nexus-development-key"
)

# MongoDB connection
MONGO_URI = os.getenv(
    "MONGO_URI", "mongodb://localhost:27017/"
)

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client["number_nexus"]

# MongoDB collections
players = db["players"]
levels = db["levels"]
sessions = db["game_sessions"]
achievements = db["achievements"]


def current_time():
    return datetime.now(timezone.utc)


def clean_username(username):
    username = re.sub(
        r"[^A-Za-z0-9_ -]",
        "",
        str(username or "")
    )
    return username.strip()[:20]


# --------------------------------------------------
# 1. LEVEL DATA
# --------------------------------------------------

LEVEL_DATA = [
    {
        "level_id": 1,
        "stage": "The Beginning",
        "title": "Missing Number",
        "difficulty": "Easy",
        "question": "2, 4, 6, __, 10",
        "answer": "8",
        "hint": "The numbers increase by 2.",
        "points": 100,
        "explanation": "Each number increases by 2."
    },
    {
        "level_id": 2,
        "stage": "The Beginning",
        "title": "Number Pair",
        "difficulty": "Easy",
        "question": "5 + 7 = __",
        "answer": "12",
        "hint": "Add 5 and 7.",
        "points": 100,
        "explanation": "5 plus 7 equals 12."
    },
    {
        "level_id": 3,
        "stage": "The Beginning",
        "title": "Double Trouble",
        "difficulty": "Easy",
        "question": "3, 6, 12, 24, __",
        "answer": "48",
        "hint": "Multiply each number by 2.",
        "points": 100,
        "explanation": "Every number is double the previous number."
    },
    {
        "level_id": 4,
        "stage": "Sequence Gate",
        "title": "Growing Steps",
        "difficulty": "Easy",
        "question": "1, 4, 7, 10, __",
        "answer": "13",
        "hint": "Add the same number each time.",
        "points": 100,
        "explanation": "Add 3 to each number."
    },
    {
        "level_id": 5,
        "stage": "Sequence Gate",
        "title": "Square Route",
        "difficulty": "Medium",
        "question": "1, 4, 9, 16, __",
        "answer": "25",
        "hint": "These are square numbers.",
        "points": 120,
        "explanation": "They are 1 squared, 2 squared, 3 squared, 4 squared and 5 squared."
    },
    {
        "level_id": 6,
        "stage": "Sequence Gate",
        "title": "Reverse Path",
        "difficulty": "Medium",
        "question": "30, 25, 20, 15, __",
        "answer": "10",
        "hint": "Subtract 5 each time.",
        "points": 120,
        "explanation": "The sequence decreases by 5."
    },
    {
        "level_id": 7,
        "stage": "Equation Chamber",
        "title": "Balance the Equation",
        "difficulty": "Medium",
        "question": "□ + 18 = 31",
        "answer": "13",
        "hint": "Subtract 18 from 31.",
        "points": 120,
        "explanation": "31 minus 18 equals 13."
    },
    {
        "level_id": 8,
        "stage": "Equation Chamber",
        "title": "Hidden Multiplier",
        "difficulty": "Medium",
        "question": "6 × □ = 54",
        "answer": "9",
        "hint": "Divide 54 by 6.",
        "points": 120,
        "explanation": "54 divided by 6 equals 9."
    },
    {
        "level_id": 9,
        "stage": "Equation Chamber",
        "title": "Three-Step Lock",
        "difficulty": "Medium",
        "question": "(8 × 3) - 5 = __",
        "answer": "19",
        "hint": "Multiply first, then subtract.",
        "points": 120,
        "explanation": "8 times 3 is 24. Subtract 5 to get 19."
    },
    {
        "level_id": 10,
        "stage": "Logic Labyrinth",
        "title": "Odd One Out",
        "difficulty": "Hard",
        "question": "Which number does not belong: 2, 3, 5, 8, 11?",
        "answer": "8",
        "hint": "Four of these numbers are prime.",
        "points": 150,
        "explanation": "8 is not prime. The other numbers are prime."
    },
    {
        "level_id": 11,
        "stage": "Logic Labyrinth",
        "title": "Hidden Number",
        "difficulty": "Hard",
        "question": "A number multiplied by 4 gives 64. Find the number.",
        "answer": "16",
        "hint": "Divide 64 by 4.",
        "points": 150,
        "explanation": "64 divided by 4 equals 16."
    },
    {
        "level_id": 12,
        "stage": "Logic Labyrinth",
        "title": "Halfway There",
        "difficulty": "Hard",
        "question": "What is half of 3/4? Enter as a/b.",
        "answer": "3/8",
        "hint": "Multiply 3/4 by 1/2.",
        "points": 150,
        "explanation": "Half of 3/4 is 3/8."
    },
    {
        "level_id": 13,
        "stage": "Final Nexus",
        "title": "Mixed Signal",
        "difficulty": "Hard",
        "question": "2, 6, 12, 20, 30, __",
        "answer": "42",
        "hint": "The differences are 4, 6, 8 and 10.",
        "points": 175,
        "explanation": "The next difference is 12, so the answer is 42."
    },
    {
        "level_id": 14,
        "stage": "Final Nexus",
        "title": "Final Equation",
        "difficulty": "Hard",
        "question": "If 3x + 7 = 28, what is x?",
        "answer": "7",
        "hint": "Subtract 7 and divide by 3.",
        "points": 175,
        "explanation": "3x equals 21, so x equals 7."
    },
    {
        "level_id": 15,
        "stage": "Final Nexus",
        "title": "The Last Key",
        "difficulty": "Hard",
        "question": "A two-digit number has digits that add to 9. Its tens digit is twice its units digit. What is the number?",
        "answer": "63",
        "hint": "Try 6 and 3 as the two digits.",
        "points": 200,
        "explanation": "6 plus 3 equals 9, and 6 is twice 3."
    }
]


# --------------------------------------------------
# 2. DATABASE INITIALIZATION
# --------------------------------------------------

def initialize_database():

    if levels.count_documents({}) == 0:
        levels.insert_many(LEVEL_DATA)
        print("15 game levels inserted.")

    players.create_index(
        "username",
        unique=True
    )

    levels.create_index(
        "level_id",
        unique=True
    )

    sessions.create_index([
        ("username", 1),
        ("played_at", DESCENDING)
    ])

    achievements.create_index(
        [
            ("username", 1),
            ("achievement_name", 1)
        ],
        unique=True
    )

    print("MongoDB collections and indexes ready.")


# --------------------------------------------------
# 3. ACHIEVEMENT MANAGEMENT
# --------------------------------------------------

def award_achievement(username, name, description):

    achievements.update_one(
        {
            "username": username,
            "achievement_name": name
        },
        {
            "$setOnInsert": {
                "username": username,
                "achievement_name": name,
                "description": description,
                "unlocked_at": current_time()
            }
        },
        upsert=True
    )


# --------------------------------------------------
# 4. HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# 5. DATABASE CONNECTION TEST
# --------------------------------------------------

@app.route("/api/health")
def health():

    try:
        client.admin.command("ping")

        return jsonify({
            "status": "success",
            "database": "MongoDB connected"
        })

    except PyMongoError:

        return jsonify({
            "status": "error",
            "database": "MongoDB disconnected"
        }), 503


# --------------------------------------------------
# 6. PLAYER REGISTRATION
# --------------------------------------------------

@app.route("/api/start", methods=["POST"])
def start_game():

    data = request.get_json(silent=True) or {}

    username = clean_username(
        data.get("username")
    )

    if len(username) < 2:
        return jsonify({
            "error": "Username must contain at least 2 characters."
        }), 400

    try:

        player = players.find_one_and_update(
            {"username": username},

            {
                "$set": {
                    "last_played": current_time()
                },

                "$setOnInsert": {
                    "username": username,
                    "total_score": 0,
                    "unlocked_level": 1,
                    "completed_levels": [],
                    "created_at": current_time()
                }
            },

            upsert=True,
            return_document=True
        )

        return jsonify({
            "message": "Welcome to Number Nexus!",

            "player": {
                "username": player["username"],
                "total_score": player.get("total_score", 0),
                "unlocked_level": player.get("unlocked_level", 1),
                "completed_levels": player.get("completed_levels", [])
            }
        })

    except PyMongoError:

        return jsonify({
            "error": "Could not save player. Check MongoDB."
        }), 503


# --------------------------------------------------
# 7. DISPLAY ALL LEVELS
# --------------------------------------------------

@app.route("/api/levels")
def get_levels():

    username = clean_username(
        request.args.get("username")
    )

    player = players.find_one({
        "username": username
    })

    if not player:
        return jsonify({"error": "Player not found."}), 404

    unlocked = player.get("unlocked_level", 1)

    completed = player.get(
        "completed_levels", []
    )

    all_levels = levels.find(
        {},
        {
            "_id": 0,
            "level_id": 1,
            "stage": 1,
            "title": 1,
            "difficulty": 1
        }
    ).sort("level_id", 1)

    result = []

    for level in all_levels:

        level["unlocked"] = (
            level["level_id"] <= unlocked
        )

        level["completed"] = (
            level["level_id"] in completed
        )

        result.append(level)

    return jsonify({
        "levels": result
    })


# --------------------------------------------------
# 8. GET A SINGLE PUZZLE
# --------------------------------------------------

@app.route("/api/level/<int:level_id>")
def get_level(level_id):

    username = clean_username(
        request.args.get("username")
    )

    player = players.find_one({
        "username": username
    })

    if not player:
        return jsonify({"error": "Player not found."}), 404

    if level_id > player.get("unlocked_level", 1):
        return jsonify({
            "error": "Complete the previous level first."
        }), 403

    level = levels.find_one(
        {"level_id": level_id},
        {
            "_id": 0,
            "answer": 0,
            "explanation": 0
        }
    )

    if not level:
        return jsonify({
            "error": "Level not found."
        }), 404

    return jsonify({
        "level": level,
        "already_completed": (
            level_id in player.get("completed_levels", [])
        )
    })


# --------------------------------------------------
# 9. HINT SYSTEM
# --------------------------------------------------

@app.route("/api/hint", methods=["POST"])
def get_hint():

    data = request.get_json(silent=True) or {}

    username = clean_username(
        data.get("username")
    )

    try:
        level_id = int(data.get("level_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid level."}), 400

    player = players.find_one({
        "username": username
    })

    if not player:
        return jsonify({"error": "Player not found."}), 404

    if level_id > player.get("unlocked_level", 1):
        return jsonify({"error": "Level is locked."}), 403

    level = levels.find_one(
        {"level_id": level_id},
        {"_id": 0, "hint": 1}
    )

    if not level:
        return jsonify({"error": "Level not found."}), 404

    return jsonify({
        "hint": level["hint"],
        "penalty": 20
    })


# --------------------------------------------------
# 10. ANSWER VALIDATION AND SCORING
# --------------------------------------------------

@app.route("/api/submit", methods=["POST"])
def submit_answer():

    data = request.get_json(silent=True) or {}

    username = clean_username(
        data.get("username")
    )

    try:

        level_id = int(data.get("level_id"))

        attempts = max(
            1,
            min(int(data.get("attempts", 1)), 50)
        )

        hints_used = max(
            0,
            min(int(data.get("hints_used", 0)), 5)
        )

    except (TypeError, ValueError):

        return jsonify({
            "error": "Invalid game information."
        }), 400

    submitted = str(
        data.get("answer", "")
    ).strip().lower().replace(" ", "")

    if not submitted:
        return jsonify({
            "error": "Please enter your answer."
        }), 400

    player = players.find_one({
        "username": username
    })

    if not player:
        return jsonify({
            "error": "Player not found."
        }), 404

    if level_id > player.get("unlocked_level", 1):
        return jsonify({
            "error": "This level is locked."
        }), 403

    level = levels.find_one({
        "level_id": level_id
    })

    if not level:
        return jsonify({
            "error": "Level not found."
        }), 404

    correct_answer = str(
        level["answer"]
    ).strip().lower().replace(" ", "")

    correct = submitted == correct_answer

    already_completed = (
        level_id in player.get("completed_levels", [])
    )

    points = 0

    if correct and not already_completed:

        first_attempt_bonus = (
            25 if attempts == 1 else 0
        )

        points = max(
            0,
            level["points"]
            + first_attempt_bonus
            - (20 * hints_used)
            - (10 * (attempts - 1))
        )

        # Stage completion bonus
        if level_id in [3, 6, 9, 12, 15]:
            points += 50

    # Save game attempt
    sessions.insert_one({

        "username": username,

        "level_id": level_id,

        "submitted_answer": submitted,

        "is_correct": correct,

        "attempts": attempts,

        "hints_used": hints_used,

        "points_earned": points,

        "played_at": current_time()
    })

    if not correct:

        return jsonify({
            "correct": False,
            "message": "Incorrect answer! Try again.",
            "points_earned": 0
        })

    # Update player progress only on first completion
    if not already_completed:

        completed = sorted(
            set(
                player.get("completed_levels", [])
                + [level_id]
            )
        )

        unlocked = max(
            player.get("unlocked_level", 1),
            min(15, level_id + 1)
        )

        players.update_one(
            {"username": username},

            {
                "$set": {
                    "completed_levels": completed,
                    "unlocked_level": unlocked,
                    "last_played": current_time()
                },

                "$inc": {
                    "total_score": points
                }
            }
        )

        if level_id == 1:

            award_achievement(
                username,
                "First Victory",
                "Completed the first level."
            )

        if level_id in [3, 6, 9, 12, 15]:

            award_achievement(
                username,
                "Stage Explorer",
                "Completed a complete stage."
            )

        if level_id == 15:

            award_achievement(
                username,
                "Nexus Escaped",
                "Successfully completed all 15 levels."
            )

    updated_player = players.find_one({
        "username": username
    })

    return jsonify({

        "correct": True,

        "message": "Correct! Level completed.",

        "explanation": level["explanation"],

        "points_earned": points,

        "already_completed": already_completed,

        "player": {
            "total_score": updated_player["total_score"],
            "unlocked_level": updated_player["unlocked_level"],
            "completed_levels": updated_player["completed_levels"]
        }
    })


# --------------------------------------------------
# 11. PLAYER PROGRESS
# --------------------------------------------------

@app.route("/api/progress/<username>")
def get_progress(username):

    username = clean_username(username)

    player = players.find_one({
        "username": username
    })

    if not player:
        return jsonify({
            "error": "Player not found."
        }), 404

    history = list(
        sessions.find(
            {"username": username},
            {"_id": 0}
        ).sort(
            "played_at", DESCENDING
        ).limit(10)
    )

    badges = list(
        achievements.find(
            {"username": username},
            {"_id": 0}
        )
    )

    total_attempts = sessions.count_documents({
        "username": username
    })

    correct_attempts = sessions.count_documents({
        "username": username,
        "is_correct": True
    })

    accuracy = 0

    if total_attempts > 0:
        accuracy = round(
            correct_attempts / total_attempts * 100,
            1
        )

    return jsonify({

        "player": {
            "username": player["username"],
            "total_score": player.get("total_score", 0),
            "unlocked_level": player.get("unlocked_level", 1),
            "completed_levels": player.get("completed_levels", [])
        },

        "total_attempts": total_attempts,

        "correct_attempts": correct_attempts,

        "accuracy": accuracy,

        "history": history,

        "achievements": badges
    })


# --------------------------------------------------
# 12. LEADERBOARD USING AGGREGATION
# --------------------------------------------------

@app.route("/api/leaderboard")
def leaderboard():

    pipeline = [

        {
            "$sort": {
                "total_score": -1,
                "username": 1
            }
        },

        {
            "$limit": 10
        },

        {
            "$project": {
                "_id": 0,
                "username": 1,
                "total_score": 1,
                "unlocked_level": 1
            }
        }

    ]

    result = list(
        players.aggregate(pipeline)
    )

    return jsonify({
        "leaderboard": result
    })


# --------------------------------------------------
# 13. START APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    try:

        client.admin.command("ping")

        print("MongoDB connected successfully!")

        initialize_database()

    except PyMongoError as error:

        print("MongoDB connection error:", error)

        raise SystemExit(
            "Please start MongoDB and check your connection."
        )

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
