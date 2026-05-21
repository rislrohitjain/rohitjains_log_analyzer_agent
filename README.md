# Antigravity 2.0 - Laravel Log Analyzer Agent

A high-performance enterprise automation dashboard designed to scrape, parse, and analyze remote or local Laravel logs in real-time. Built with Polars for ultra-fast, multi-threaded log filtering and Streamlit for a slick developer UI.

## Features
- **High-Performance Parsing Engine:** Leverages Polars to parse exceptions and tracebacks with multi-threaded efficiency.
- **LIFO Log Evaluation:** Automatically displays log streams in reverse-chronological order (newest first).
- **Laravel Paradigm Matcher:** Automatically identifies major Laravel-specific failure categories (Database drops, Permission issues, Memory exhaustion) and generates immediate CLI/Bash repair snippets.
- **Google Chat Webhook Dispatcher:** Instantly formats and relays the selected active log exception (with timestamp, trace, and repair guide) to your Google Chat spaces via a webhook connector.
- **Dual-Panel Grid Layout:** LHS for raw logs, RHS for live diagnostic parsing.

## Installation & Setup

1. **Python version:** Requires Python 3.11+.
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run application:**
   ```bash
   streamlit run app.py
   ```

## Repository Management
Initialize git inside this directory and link it to your remote GitHub:
```bash
git init
git add .
git commit -m "Initial commit: Antigravity 2.0 Log Analyzer Agent"
```
To link to a remote repository:
```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```
