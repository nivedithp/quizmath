🔢 Number Nexus — Mathematical Escape Game

A web-based mathematical puzzle game where players solve number challenges across 15 progressive levels, earn points, unlock achievements, and compete on a leaderboard.

Built with Python (Flask) and MongoDB (NoSQL).

🎮 Features
🧠 15 Levels across 5 stages — Easy to Hard
🏆 Achievements — unlock badges as you progress
💡 Hint System — get hints with a small point penalty
📊 Leaderboard — top 10 players by score
📈 Player Progress Tracking — accuracy, history, completed levels
🗄️ MongoDB — NoSQL database for all game data
🗺️ Game Stages
Stage	Levels	Difficulty
The Beginning	1 – 3	Easy
Sequence Gate	4 – 6	Easy / Medium
Equation Chamber	7 – 9	Medium
Logic Labyrinth	10 – 12	Hard
Final Nexus	13 – 15	Hard
🛠️ Tech Stack
Layer	Technology
Frontend	HTML, CSS, JavaScript
Backend	Python 3, Flask
Database	MongoDB
ODM	PyMongo
Config	Python dotenv
📁 Project Structure
Number_Nexus/
│
├── app.py               # Main Flask application
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
│
├── templates/
│   └── index.html       # Main game UI
│
└── static/
    ├── css/
    │   └── style.css    # Styling
    └── js/
        └── game.js      # Game logic (frontend)
🗄️ MongoDB Collections
Collection	Purpose
players	User profiles, scores, progress
levels	All 15 puzzle levels
game_sessions	Every answer attempt
achievements	Unlocked badges per player
🚀 Getting Started
1. Clone the repository
bash
git clone https://github.com/nivedithp/quizmath.git
cd quizmath
2. Create and activate virtual environment
bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac / Linux
source venv/bin/activate
3. Install dependencies
bash
pip install -r requirements.txt
4. Set up environment variables

Create a .env file in the root folder:

MONGO_URI=mongodb://localhost:27017/
SECRET_KEY=your-secret-key
5. Start MongoDB

Make sure MongoDB is running locally on port 27017.

6. Run the app
bash
python app.py

Open your browser at: http://127.0.0.1:5000

📡 API Endpoints
Method	Endpoint	Description
GET	/	Home page
GET	/api/health	Check DB connection
POST	/api/start	Register / login player
GET	/api/levels?username=	Get all levels for a player
GET	/api/level/<id>?username=	Get a single level
POST	/api/hint	Get a hint (−20 pts penalty)
POST	/api/submit	Submit an answer
GET	/api/progress/<username>	Get player progress & achievements
GET	/api/leaderboard	Top 10 players
🏅 Achievements
Badge	How to Unlock
First Victory	Complete Level 1
Stage Explorer	Complete any full stage (Level 3, 6, 9, 12, or 15)
Nexus Escaped	Complete all 15 levels
📦 Requirements
Flask
pymongo
python-dotenv
📄 License

This project is for educational purposes.
