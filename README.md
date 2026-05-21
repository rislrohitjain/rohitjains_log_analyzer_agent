# Antigravity 2.0 - Laravel Log Analyzer Agent

A privacy-first high-performance enterprise automation dashboard designed to scrape, parse, and analyze remote or local Laravel logs in real-time. Built with Polars for ultra-fast multi-threaded log filtering, and Streamlit for a premium developer UI.

## Features
- **High-Performance Ingest & Parse:** Leverages Polars to parse exceptions and tracebacks with multi-threaded efficiency.
- **LIFO Log Evaluation:** Automatically displays log streams in reverse-chronological order (newest first) to surface infrastructure failures instantly.
- **Protocol-Aligned Data Schema:** Strictly parses tokens into structural schemas mapping: `[timestamp] [environment.level] [exception_message]`.
- **Laravel Paradigm Matcher:** Automatically identifies major Laravel-specific failure categories (Database socket connection drops, File permissions, Memory/timeout limit exhaustion) and displays a copy-pasteable bash/artisan remediation command.
- **Google Chat Webhook Dispatcher:** Instantly formats and relays the selected active log exception (with timestamp, trace, and repair guide) as a markdown card to your Google Chat workspace channels.
- **Dual-Panel Grid Layout:** LHS features a scrollable, height-bounded code container for raw logs. RHS provides the diagnostic suite.

---

## Installation & Setup

1. **Python version:** Requires Python 3.11+.
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Application:**
   ```bash
   streamlit run app.py
   ```

---

## Testing / Mock Server

To run offline or test without a live server:
1. **Start the Mock Server:**
   ```bash
   python mock_server.py
   ```
   This will start a local HTTP server at `http://localhost:8000/laravel.log` serving mock Laravel exceptions with fresh timestamps.
2. **Streamlit Connection:** Check the **Force Test Server Fallback** option in the Streamlit sidebar, or enter `http://localhost:8000/laravel.log` as the log stream URL.

---

## GitHub Setup & Integration

### 1. Linking Local Repository to GitHub
The project is initialized with a local Git repository. To host this repository on GitHub:
1. Create a new, blank repository on GitHub.
2. Run the following commands in your local project folder:
   ```bash
   git remote add origin <your-github-repo-url>
   git branch -M main
   git push -u origin main
   ```

### 2. CI/CD Workflows
A GitHub Actions workflow is pre-configured at `.github/workflows/ci.yml`. 
- **Trigger:** Runs automatically on every `push` and `pull_request` to `main` or `master` branches.
- **Functions:** Set up Python 3.11, install dependencies, run code quality analysis using `ruff`, and perform python syntax verification on `app.py` and `mock_server.py`.
