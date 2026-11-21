
const state = {
    username: "",
    currentLevel: null,
    attempts: 1,
    hintsUsed: 0,
    completedLevels: [],
    unlockedLevel: 1,
    totalScore: 0,
    alreadyCompleted: false
};


// --------------------------------------------------
// 1. HELPER FUNCTIONS
// --------------------------------------------------

const $ = (id) => document.getElementById(id);


async function api(url, options = {}) {

    const response = await fetch(url, {

        headers: {
            "Content-Type": "application/json"
        },

        ...options

    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.error || "Something went wrong."
        );
    }

    return data;
}


// --------------------------------------------------
// 2. NOTIFICATION
// --------------------------------------------------

function showToast(message) {

    const toast = $("toast");

    toast.textContent = message;

    toast.classList.remove("hidden");

    clearTimeout(showToast.timer);

    showToast.timer = setTimeout(() => {

        toast.classList.add("hidden");

    }, 2600);
}


// --------------------------------------------------
// 3. FEEDBACK
// --------------------------------------------------

function showFeedback(message, type = "info") {

    const box = $("feedback");

    box.textContent = message;

    box.className = `feedback ${type}`;
}


// --------------------------------------------------
// 4. UPDATE PLAYER INFORMATION
// --------------------------------------------------

function setPlayer(player) {

    state.totalScore = player.total_score || 0;

    state.unlockedLevel = player.unlocked_level || 1;

    state.completedLevels = player.completed_levels || [];

    $("totalScore").textContent = state.totalScore;

    $("levelsCleared").textContent =
        `${state.completedLevels.length} / 15`;

    $("nextLevel").textContent =
        String(Math.min(state.unlockedLevel, 15))
        .padStart(2, "0");

    $("levelCount").textContent =
        `${state.completedLevels.length} / 15`;
}


// --------------------------------------------------
// 5. START GAME
// --------------------------------------------------

async function startGame(username) {

    const data = await api("/api/start", {

        method: "POST",

        body: JSON.stringify({
            username: username
        })

    });

    state.username = data.player.username;

    setPlayer(data.player);

    $("playerChip").textContent = state.username;

    $("welcomeName").textContent = state.username;

    $("welcomeScreen").classList.add("hidden");

    $("gameScreen").classList.remove("hidden");

    await loadLevels();

    await loadProgress();
}


// --------------------------------------------------
// 6. LEVEL STAGES
// --------------------------------------------------

const stages = [

    "The Beginning",

    "Sequence Gate",

    "Equation Chamber",

    "Logic Labyrinth",

    "Final Nexus"

];


// --------------------------------------------------
// 7. LOAD ALL LEVELS
// --------------------------------------------------

async function loadLevels() {

    const data = await api(
        `/api/levels?username=${encodeURIComponent(state.username)}`
    );

    const container = $("levelsContainer");

    container.innerHTML = "";

    stages.forEach(stage => {

        const stageLevels = data.levels.filter(

            level => level.stage === stage

        );

        if (stageLevels.length === 0) {
            return;
        }

        const group = document.createElement("div");

        group.className = "stage-group";

        const heading = document.createElement("div");

        heading.className = "stage-title";

        heading.textContent = stage.toUpperCase();

        const grid = document.createElement("div");

        grid.className = "level-grid";


        stageLevels.forEach(level => {

            const button = document.createElement("button");

            button.className = "level-card";

            if (level.completed) {

                button.classList.add("completed");

            }

            if (!level.unlocked) {

                button.disabled = true;

            }

            let symbol = "🔒";

            if (level.completed) {

                symbol = "✓";

            } else if (level.unlocked) {

                symbol = "→";

            }

            const number = String(level.level_id)
                .padStart(2, "0");

            const strong = document.createElement("strong");

            strong.textContent = `${number} ${symbol}`;

            const small = document.createElement("small");

            small.textContent = level.title;

            button.append(strong, small);

            button.addEventListener("click", () => {

                openLevel(level.level_id);

            });

            grid.appendChild(button);

        });


        group.append(heading, grid);

        container.appendChild(group);

    });

}


// --------------------------------------------------
// 8. OPEN A LEVEL
// --------------------------------------------------

async function openLevel(levelId) {

    try {

        const data = await api(

            `/api/level/${levelId}?username=${encodeURIComponent(state.username)}`

        );

        state.currentLevel = levelId;

        state.attempts = 1;

        state.hintsUsed = 0;

        state.alreadyCompleted = data.already_completed;


        const level = data.level;


        $("puzzleEmpty").classList.add("hidden");

        $("puzzleContent").classList.remove("hidden");

        $("levelPill").textContent =
            `LEVEL ${String(level.level_id).padStart(2, "0")}`;

        $("difficulty").textContent =
            level.difficulty.toUpperCase();

        $("stageName").textContent =
            level.stage.toUpperCase();

        $("puzzleTitle").textContent =
            level.title;

        $("questionText").textContent =
            level.question;

        $("answerInput").value = "";

        $("answerInput").disabled = false;

        $("answerForm").querySelector("button").disabled = false;

        $("answerForm").querySelector("button").textContent =
            "Check Answer";

        $("attemptLabel").textContent = "Attempt 1";

        $("hintBtn").disabled = false;

        $("hintBtn").innerHTML =
            "☼ Get a hint <span>(−20 points)</span>";

        $("feedback").className = "feedback hidden";

        document.querySelectorAll(".level-card").forEach(button => {

            button.classList.remove("active");

        });

        // Highlight the selected level
        const buttons = [...document.querySelectorAll(".level-card")];

        const selected = buttons.find(button => {

            return button.querySelector("strong")
                ?.textContent.startsWith(
                    String(levelId).padStart(2, "0")
                );

        });

        if (selected) {

            selected.classList.add("active");

        }

        if (data.already_completed) {

            showFeedback(
                "You have already completed this level. Replay it for practice!",
                "info"
            );

        }

        $("answerInput").focus();

    } catch (error) {

        showToast(error.message);

    }

}


// --------------------------------------------------
// 9. SUBMIT ANSWER
// --------------------------------------------------

async function submitAnswer(event) {

    event.preventDefault();

    if (!state.currentLevel) {
        return;
    }

    const answer = $("answerInput").value.trim();

    if (!answer) {
        return;
    }

    try {

        const data = await api("/api/submit", {

            method: "POST",

            body: JSON.stringify({

                username: state.username,

                level_id: state.currentLevel,

                answer: answer,

                attempts: state.attempts,

                hints_used: state.hintsUsed

            })

        });


        // Incorrect answer
        if (!data.correct) {

            showFeedback(
                data.message,
                "error"
            );

            state.attempts += 1;

            $("attemptLabel").textContent =
                `Attempt ${state.attempts}`;

            $("answerInput").select();

            return;

        }


        // Correct answer
        setPlayer(data.player);

        let message = data.message;

        message += " " + data.explanation;

        if (data.already_completed) {

            message +=
                " This level was already completed. No extra points awarded.";

        } else {

            message +=
                ` You earned ${data.points_earned} points!`;

        }

        showFeedback(
            message,
            "success"
        );


        // Disable answer controls after success
        $("answerInput").disabled = true;

        $("answerForm").querySelector("button").disabled = true;

        $("hintBtn").disabled = true;


        await loadLevels();

        await loadProgress();


        // Next level button
        if (state.currentLevel < 15) {

            const nextLevel = state.currentLevel + 1;

            const nextButton = document.createElement("button");

            nextButton.className = "primary-btn";

            nextButton.style.marginTop = "14px";

            nextButton.textContent =
                `Continue to Level ${nextLevel} →`;

            nextButton.addEventListener("click", () => {

                openLevel(nextLevel);

            });

            $("feedback").appendChild(
                document.createElement("br")
            );

            $("feedback").appendChild(nextButton);

        } else {

            showToast(
                "Congratulations! You escaped Number Nexus!"
            );

        }

    } catch (error) {

        showFeedback(
            error.message,
            "error"
        );

    }

}


// --------------------------------------------------
// 10. HINT SYSTEM
// --------------------------------------------------

async function useHint() {

    if (!state.currentLevel) {
        return;
    }

    try {

        const data = await api("/api/hint", {

            method: "POST",

            body: JSON.stringify({

                username: state.username,

                level_id: state.currentLevel

            })

        });

        state.hintsUsed += 1;

        $("hintBtn").disabled = true;

        $("hintBtn").textContent = "Hint used";

        showFeedback(

            `Hint: ${data.hint}. 20 points will be deducted from the level reward.`,

            "info"

        );

    } catch (error) {

        showToast(error.message);

    }

}


// --------------------------------------------------
// 11. PLAYER PROGRESS
// --------------------------------------------------

async function loadProgress() {

    try {

        const data = await api(

            `/api/progress/${encodeURIComponent(state.username)}`

        );

        setPlayer(data.player);

        const container = $("achievements");

        container.innerHTML = "";

        if (data.achievements.length === 0) {

            container.innerHTML =

                '<span class="muted">Complete a level to earn your first achievement.</span>';

        } else {

            data.achievements.forEach(item => {

                const badge = document.createElement("div");

                badge.className = "achievement-item";

                const title = document.createElement("strong");

                title.textContent =
                    `✦ ${item.achievement_name}`;

                const description = document.createElement("span");

                description.textContent =
                    item.description;

                badge.append(title, description);

                container.appendChild(badge);

            });

        }

    } catch (error) {

        console.error(error);

    }

}


// --------------------------------------------------
// 12. LEADERBOARD
// --------------------------------------------------

async function showLeaderboard() {

    try {

        const data = await api("/api/leaderboard");

        const list = $("leaderboardList");

        list.innerHTML = "";

        if (data.leaderboard.length === 0) {

            list.textContent =
                "No scores yet. Be the first to play!";

        }

        data.leaderboard.forEach((player, index) => {

            const row = document.createElement("div");

            row.className = "leader-row";

            const name = document.createElement("span");

            name.textContent =
                `${index + 1}. ${player.username}`;

            const score = document.createElement("b");

            score.textContent =
                `${player.total_score} pts`;

            row.append(name, score);

            list.appendChild(row);

        });

        $("leaderboardModal").classList.remove("hidden");

    } catch (error) {

        showToast(error.message);

    }

}


// --------------------------------------------------
// 13. EVENT LISTENERS
// --------------------------------------------------

// Player registration

$("startForm").addEventListener("submit", async (event) => {

    event.preventDefault();

    const username = $("username").value.trim();

    try {

        await startGame(username);

    } catch (error) {

        showToast(error.message);

    }

});


// Answer submission

$("answerForm").addEventListener(
    "submit",
    submitAnswer
);


// Hint button

$("hintBtn").addEventListener(
    "click",
    useHint
);


// Leaderboard

$("leaderboardBtn").addEventListener(
    "click",
    showLeaderboard
);


// Close leaderboard

$("closeModal").addEventListener("click", () => {

    $("leaderboardModal").classList.add("hidden");

});


// Close leaderboard by clicking outside

$("leaderboardModal").addEventListener("click", event => {

    if (event.target === $("leaderboardModal")) {

        $("leaderboardModal").classList.add("hidden");

    }

});


// Refresh progress

$("refreshProgress").addEventListener(
    "click",
    loadProgress
);


// Home button

$("homeBtn").addEventListener("click", () => {

    $("gameScreen").classList.add("hidden");

    $("welcomeScreen").classList.remove("hidden");

    $("answerInput").disabled = false;

    $("answerForm").querySelector("button").disabled = false;

    state.currentLevel = null;

});
