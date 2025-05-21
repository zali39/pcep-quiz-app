# PCEP-1 Adaptive Quiz App

This is an AI-powered, adaptive quiz application designed to help users prepare for the PCEP-1 Python Certification Exam. Built with Streamlit and powered by a local SQLite database, it features:

- Adaptive difficulty based on user performance
- Secure login with username and password
- Topic-based accuracy tracking
- Leaderboard for top performers
- Fully deployable to Streamlit Cloud or local hosting

## 🧠 Topics Covered
- Data types and operations
- Control flow (conditionals, loops)
- Functions and input/output
- Exception handling

## 🚀 Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🧩 Deployment on Streamlit Cloud
1. Fork or upload this repo to GitHub
2. Go to https://streamlit.io/cloud
3. Create a new app from your repo and select `app.py`

## 📁 Files
- `app.py` — main app logic
- `questions.json` — quiz questions
- `quiz.db` — SQLite database (auto-created)
- `requirements.txt` — required Python packages
- `.streamlit/config.toml` — custom visual theme
- `logo.png` — placeholder logo image

---

© 2025 Your Organization. Licensed under the MIT License.