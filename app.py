import streamlit as st
import sqlite3
import random
import json
import os

# Initialize database
DB_FILE = "quiz.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    score INTEGER,
    total INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER,
    topic TEXT,
    correct INTEGER,
    FOREIGN KEY (result_id) REFERENCES results(id)
)
""")
conn.commit()

# Load questions
with open("questions.json", "r") as f:
    questions = json.load(f)

# Sidebar login/signup
st.sidebar.title("🔐 Login / Sign Up")
mode = st.sidebar.radio("Select Mode", ["Login", "Sign Up"])
input_user = st.sidebar.text_input("Username")
input_pass = st.sidebar.text_input("Password", type="password")

if st.sidebar.button(mode):
    if mode == "Sign Up":
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (input_user, input_pass))
            conn.commit()
            st.sidebar.success("User registered. Please log in.")
        except:
            st.sidebar.error("Username already exists.")
    else:
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (input_user, input_pass))
        user = cursor.fetchone()
        if user:
            st.session_state.user_id = user[0]
            st.session_state.username = input_user
            st.sidebar.success(f"Logged in as: {input_user}")
        else:
            st.sidebar.error("Invalid credentials.")

# Proceed if logged in
if "user_id" in st.session_state:
    user_id = st.session_state.user_id
    username = st.session_state.username

    st.title(f"🎯 PCEP-1 Adaptive Quiz for {username}")

    if "current_q" not in st.session_state:
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.history = []
        st.session_state.quiz_done = False

    def get_next_question():
        prev_q = st.session_state.history
        available = [q for q in questions if q["id"] not in [pq["id"] for pq in prev_q]]

        if prev_q:
            last = prev_q[-1]
            if last["user_answer"] == last["answer"]:
                next_difficulty = min(3, last["difficulty"] + 1)
            else:
                next_difficulty = max(1, last["difficulty"] - 1)
            available = [q for q in available if q["difficulty"] == next_difficulty]

        if not available:
            return None
        return random.choice(available)

    if not st.session_state.quiz_done:
        question = get_next_question()
        if question:
            st.write(f"**Q: {question['question']}**")
            user_answer = st.radio("Choose your answer:", question["options"], key=question["id"])
            if st.button("Submit", key=f"submit_{question['id']}"):
                correct = user_answer == question["answer"]
                st.session_state.history.append({
                    "id": question["id"],
                    "question": question["question"],
                    "answer": question["answer"],
                    "user_answer": user_answer,
                    "correct": correct,
                    "topic": question["topic"],
                    "difficulty": question["difficulty"]
                })
                if correct:
                    st.success("✅ Correct!")
                    st.session_state.score += 1
                else:
                    st.error(f"❌ Incorrect. The correct answer was: {question['answer']}")
                st.experimental_rerun()
        else:
            st.session_state.quiz_done = True
            total = len(st.session_state.history)
            st.success(f"🎉 Quiz complete! Score: {st.session_state.score}/{total}")

            cursor.execute("INSERT INTO results (user_id, score, total) VALUES (?, ?, ?)",
                           (user_id, st.session_state.score, total))
            result_id = cursor.lastrowid
            for h in st.session_state.history:
                cursor.execute("INSERT INTO answers (result_id, topic, correct) VALUES (?, ?, ?)",
                               (result_id, h["topic"], int(h["correct"])))
            conn.commit()

            if st.button("Restart Quiz"):
                st.session_state.current_q = 0
                st.session_state.score = 0
                st.session_state.history = []
                st.session_state.quiz_done = False
                st.experimental_rerun()
    else:
        st.info("You've completed the quiz. Restart or view leaderboard.")

    # Leaderboard
    st.sidebar.title("🏆 Leaderboard")
    if st.sidebar.button("Show Leaderboard"):
        st.subheader("Top Scores")
        leaderboard = cursor.execute(
            "SELECT username, MAX(score) AS max_score FROM results JOIN users ON users.id = results.user_id GROUP BY user_id ORDER BY max_score DESC LIMIT 10"
        ).fetchall()
        for rank, (user, score) in enumerate(leaderboard, 1):
            st.write(f"{rank}. {user} – {score} points")

    # Topic Accuracy
    st.sidebar.title("📊 Your Stats")
    if st.sidebar.button("View Stats"):
        st.subheader("📈 Topic Accuracy")
        stats = cursor.execute(
            "SELECT topic, SUM(correct), COUNT(*) FROM answers JOIN results ON results.id = answers.result_id WHERE results.user_id = ? GROUP BY topic",
            (user_id,)
        ).fetchall()
        for topic, correct, total in stats:
            acc = correct / total * 100
            st.write(f"{topic.title()}: {acc:.1f}% ({correct}/{total})")
