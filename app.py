import streamlit as st
import polars as pl
import re
import requests
from datetime import datetime

# Configure Streamlit wide mode, page title, and premium look
st.set_page_config(
    page_title="Antigravity 2.0 - Log Analyzer Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern visual design (dark mode styling, glassmorphism, nice fonts)
st.markdown("""
<style>
    /* Styling headers and panels */
    .header-title {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, #FF4B4B, #FF8F8F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .panel-container {
        background-color: #1E2022;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2D3035;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .raw-logs-box {
        font-family: 'Fira Code', 'Courier New', Courier, monospace;
        font-size: 13px;
        background-color: #0E1117;
        color: #E2E8F0;
        border: 1px solid #1F2937;
        border-radius: 8px;
        padding: 12px;
        height: 600px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
    
    .code-snippet {
        font-family: 'Fira Code', monospace;
        background-color: #0E1117;
        border: 1px solid #FF4B4B;
        border-radius: 6px;
        padding: 10px;
        color: #58A6FF;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- PARSING ENGINE (POLARS ONLY) -----------------

def parse_laravel_logs(log_text: str) -> pl.DataFrame:
    """
    Parses Laravel logs using regular expressions and returns a Polars DataFrame sorted LIFO.
    Laravel pattern: [YYYY-MM-DD HH:MM:SS] environment.level: message [stacktrace]
    """
    # Regex to capture: [timestamp] environment.level: message
    # And lazily capture all content up to the next timestamp or end of file.
    pattern = re.compile(
        r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+([a-zA-Z0-9_-]+\.[A-Z]+):\s+(.*?)(?=\n^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]|\Z)',
        re.MULTILINE | re.DOTALL
    )
    
    timestamps = []
    env_levels = []
    messages = []
    full_texts = []
    
    for match in pattern.finditer(log_text):
        ts = match.group(1)
        env_lvl = match.group(2)
        body = match.group(3).strip()
        
        # Get the first line as message, remainder is traceback
        lines = body.split("\n", 1)
        msg = lines[0]
        
        timestamps.append(ts)
        env_levels.append(env_lvl)
        messages.append(msg)
        full_texts.append(f"[{ts}] {env_lvl}: {body}")
        
    if not timestamps:
        # Fallback if logs don't match the regex perfectly
        # Treat every non-empty line as an entry
        lines = [line.strip() for line in log_text.splitlines() if line.strip()]
        if lines:
            timestamps = [datetime.now().strftime("%Y-%m-%d %H:%M:%S") for _ in lines]
            env_levels = ["local.ERROR" for _ in lines]
            messages = lines
            full_texts = lines
        else:
            return pl.DataFrame({
                "timestamp": pl.Series([], dtype=pl.Utf8),
                "environment.level": pl.Series([], dtype=pl.Utf8),
                "exception_message": pl.Series([], dtype=pl.Utf8),
                "full_text": pl.Series([], dtype=pl.Utf8)
            })

    # Build Polars DataFrame
    df = pl.DataFrame({
        "timestamp": timestamps,
        "environment.level": env_levels,
        "exception_message": messages,
        "full_text": full_texts
    })
    
    # Sort descending (LIFO - newest first)
    df = df.sort("timestamp", descending=True)
    return df

# ----------------- PARADIGM MATCHING ENGINE -----------------

PARADIGMS = [
    {
        "name": "File Permissions / Storage Write Issue",
        "keywords": ["permission denied", "failed to open stream: permission denied", "storage/framework/views", "bootstrap/cache"],
        "explanation": "Laravel cache, logs, or views directories are not writable by the web server process (e.g. www-data or nginx).",
        "remediation": """# Grant write access to web-server group
sudo chmod -R 775 storage bootstrap/cache
sudo chown -R www-data:www-data storage bootstrap/cache
# Clear Laravel system/view caches
php artisan cache:clear
php artisan view:clear
php artisan optimize:clear"""
    },
    {
        "name": "Database Connection Drop / Socket Refused",
        "keywords": ["pdoexception", "connection refused", "sqlstate[hy000] [2002]", "access denied for user"],
        "explanation": "The Laravel service cannot reach the SQL database. The database server may be down, or credentials in .env are incorrect.",
        "remediation": """# Check if DB service (MySQL/PostgreSQL) is running
sudo systemctl status mysql
# Verify environment variables in Laravel directory
cat .env | grep -E "DB_HOST|DB_PORT|DB_DATABASE|DB_USERNAME"
# Flush config cache to apply .env changes
php artisan config:clear
php artisan config:cache"""
    },
    {
        "name": "Memory Limit / Timeout Exhausted",
        "keywords": ["allowed memory size of", "maximum execution time of", "exhausted"],
        "explanation": "Laravel process hit PHP's execution limits. Typically happens during large queries, exports, or queue processing.",
        "remediation": """# Check current PHP memory limits
php -r "echo ini_get('memory_limit');"
# Increase memory limits temporarily in CLI commands
php -d memory_limit=512M artisan queue:work --once
# Optimize Composer autoloader
composer install --optimize-autoloader --no-dev
# Clear configurations
php artisan config:clear"""
    },
    {
        "name": "Missing Application Encryption Key",
        "keywords": ["no application encryption key has been specified", "runtimeexception... encryptionserviceprovider"],
        "explanation": "The APP_KEY environment variable is not defined. Encrypted cookies, sessions, and data will fail.",
        "remediation": """# Generate a new app encryption key
php artisan key:generate
# Clear application config cache
php artisan config:clear
php artisan config:cache"""
    }
]

def analyze_exception(message: str) -> dict:
    """Matches the message against known Laravel paradigms."""
    msg_lower = message.lower()
    for p in PARADIGMS:
        if any(kw in msg_lower for kw in p["keywords"]):
            return p
            
    # Default fallback
    return {
        "name": "Generic Laravel Exception / Runtime Error",
        "explanation": "An unclassified exception was thrown. Review the raw traceback context in the LHS panel.",
        "remediation": """# Clear general caches
php artisan optimize:clear
# Query system state
php artisan about
# Restart the Laravel queue worker (if running asynchronous jobs)
php artisan queue:restart"""
    }

# ----------------- WEBHOOK DISPATCHER -----------------

def dispatch_webhook(webhook_url: str, timestamp: str, env_level: str, message: str, diagnosis: dict) -> bool:
    """Dispatches a structured Google Chat webhook notification."""
    if not webhook_url:
        st.error("Please enter a valid Google Chat webhook URL.")
        return False
        
    # Build a clean markdown and card representation
    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    # 1. Text payload with markdown structure
    text_content = (
        f"🚨 **Laravel Exception Alert**\n"
        f"📅 **Timestamp:** `{timestamp}`\n"
        f"🏷️ **Env/Level:** `{env_level}`\n"
        f"📝 **Exception Summary:** `{message}`\n\n"
        f"🔍 **Diagnosis:** {diagnosis['name']}\n"
        f"ℹ️ *{diagnosis['explanation']}*\n\n"
        f"🛠️ **Remediation Command:**\n```bash\n{diagnosis['remediation']}\n```"
    )
    
    # 2. Complete Google Chat Card structure
    payload = {
        "text": text_content,
        "cardsV2": [
            {
                "cardId": f"laravel_exception_{int(datetime.now().timestamp())}",
                "card": {
                    "header": {
                        "title": f"Laravel Exception: {env_level}",
                        "subtitle": f"Occurred at {timestamp}",
                        "imageUrl": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/warning/default/48px.svg"
                    },
                    "sections": [
                        {
                            "header": "Summary",
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": f"<b>Message:</b><br>{message}"
                                    }
                                }
                            ]
                        },
                        {
                            "header": f"Diagnosis: {diagnosis['name']}",
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": f"<i>{diagnosis['explanation']}</i>"
                                    }
                                }
                            ]
                        },
                        {
                            "header": "Remediation Script",
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": f"<font color=\"#58A6FF\"><b>Commands:</b></font><br><pre>{diagnosis['remediation']}</pre>"
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to deliver payload. Server responded with {response.status_code}: {response.text}")
            return False
    except Exception as e:
        st.error(f"Network error during dispatch: {str(e)}")
        return False

# ----------------- STREAMLIT APP LAYOUT -----------------

st.markdown("<h1 class='header-title'>⚡ Antigravity 2.0 Log Analyzer Agent</h1>", unsafe_allow_html=True)

# Initialize session state cache for logs
if "raw_logs" not in st.session_state:
    st.session_state.raw_logs = """[2026-05-22 14:40:43] local.ERROR: PDOException: SQLSTATE[HY000] [2002] Connection refused {"exception":"[object] (PDOException(code: 2002): SQLSTATE[HY000] [2002] Connection refused at /var/www/html/vendor/laravel/framework/src/Illuminate/Database/Connectors/Connector.php:70)"}
[2026-05-22 14:45:43] production.ERROR: ErrorException: file_put_contents(/var/www/html/storage/framework/views/w7f82h39): Failed to open stream: Permission denied {"exception":"[object] (ErrorException(code: 0): file_put_contents...)"}"""
if "last_fetched_url" not in st.session_state:
    st.session_state.last_fetched_url = "http://172.18.177.165/rsos/storage/laravel.log"

# Application controls in sidebar
with st.sidebar:
    st.markdown("### Google Chat Integration")
    webhook_url = st.text_input(
        "Webhook Endpoint Channel",
        value="",
        type="password",
        placeholder="https://chat.googleapis.com/v1/spaces/...",
        help="Paste the Google Chat webhook URL key here."
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Network Settings")
    network_timeout = st.slider(
        "Read Timeout (seconds)",
        min_value=2,
        max_value=60,
        value=10,
        help="Adjust log fetching timeout limit to prevent slow connection drops."
    )
    
    st.markdown("---")
    st.markdown("#### Test Environment Fallback")
    use_mock = st.checkbox("Force Test Server Fallback", value=False, help="Connect to the local mock logs service running at http://127.0.0.1:8000/laravel.log")

# Ingestion Selection on main panel
st.markdown("### 🔌 Log Ingestion Mode")
ingestion_mode = st.radio(
    "Choose how to load your logs:",
    options=["🌐 Live Stream URL", "📤 Upload Log File"],
    horizontal=True,
    label_visibility="collapsed"
)

raw_logs_content = ""
fetch_error = ""
is_fallback_active = False

if ingestion_mode == "🌐 Live Stream URL":
    col_url, col_btn = st.columns([5, 1], gap="medium")
    with col_url:
        log_url = st.text_input(
            "Log Stream URL",
            value="http://172.18.177.165/rsos/storage/laravel.log",
            help="Input target laravel.log endpoint. Defaults to standard development node.",
            label_visibility="collapsed"
        )
    with col_btn:
        refresh_btn = st.button("🔄 Refresh Stream", use_container_width=True, help="Force reload the Laravel log stream.")
        
    # Determine target URL
    target_url = "http://127.0.0.1:8000/laravel.log" if use_mock else log_url
    
    # Trigger fetch only if no logs exist, URL changed, or refresh was pressed
    should_fetch = (
        st.session_state.raw_logs == "" or 
        st.session_state.last_fetched_url != target_url or 
        refresh_btn
    )
    
    if should_fetch:
        try:
            with st.spinner(f"Scraping logs from: {target_url}..."):
                response = requests.get(target_url, timeout=network_timeout)
                if response.status_code == 200:
                    raw_logs_content = response.text
                else:
                    fetch_error = f"HTTP Error {response.status_code}: Unable to read target stream."
        except Exception as e:
            fetch_error = f"Network Connection Failed: {str(e)}"
            
        if fetch_error:
            st.error(f"⚠️ Failed to fetch remote log: {fetch_error}")
            
            # Show a troubleshooting helper
            with st.expander("🔍 Connection Troubleshooting Guide", expanded=True):
                st.markdown(f"""
                **Why did the connection to `{target_url}` fail?**
                1. **Read Timeout:** The server took longer than `{network_timeout}` seconds to respond. You can increase the **Read Timeout** in the sidebar.
                2. **VPN Disconnected:** If the target host is on a corporate/private network, check if you need to connect to your VPN.
                3. **Host Unreachable:** Verify if the IP/Domain is correct and accessible from your browser.
                
                **Alternatives:**
                - Switch the Ingestion Mode to **Upload Log File** to analyze a local log.
                - Check the **Force Test Server Fallback** box in the sidebar to run with mock logs.
                """)
            
            # Load fallback mock logs to keep app alive
            is_fallback_active = True
            try:
                fallback_resp = requests.get("http://127.0.0.1:8000/laravel.log", timeout=2)
                if fallback_resp.status_code == 200:
                    raw_logs_content = fallback_resp.text
                    st.info("ℹ️ Successfully loaded mock log fallback (Local Server).")
            except Exception:
                sample_fallback = """[2026-05-21 16:32:00] local.ERROR: PDOException: SQLSTATE[HY000] [2002] Connection refused {"exception":"[object] (PDOException(code: 2002): SQLSTATE[HY000] [2002] Connection refused at /var/www/html/vendor/laravel/framework/src/Illuminate/Database/Connectors/Connector.php:70)"}
[2026-05-21 16:35:12] production.ERROR: ErrorException: file_put_contents(/var/www/html/storage/framework/views/temp_views): Failed to open stream: Permission denied {"exception":"[object] (ErrorException(code: 0): file_put_contents...)"}
[2026-05-21 16:40:45] staging.ERROR: RuntimeException: No application encryption key has been specified. {"exception":"[object] (RuntimeException(code: 0): No application encryption key has been specified.)"}"""
                raw_logs_content = sample_fallback
                st.info("ℹ️ Successfully loaded mock log fallback (Offline Static).")
        
        # Cache in session state
        st.session_state.raw_logs = raw_logs_content
        st.session_state.last_fetched_url = target_url
    else:
        # Use cached logs
        raw_logs_content = st.session_state.raw_logs

else:  # Upload Log File
    uploaded_file = st.file_uploader(
        "Upload a laravel.log file:",
        type=["log", "txt"],
        help="Analyze Laravel logs offline by uploading a log file."
    )
    if uploaded_file is not None:
        raw_logs_content = uploaded_file.getvalue().decode("utf-8")
        # Clear last fetched URL cache when working with uploaded files
        st.session_state.last_fetched_url = "uploaded_file"
        st.session_state.raw_logs = raw_logs_content
    else:
        st.info("Please upload a laravel.log file to begin analysis.")
        raw_logs_content = ""

# Visual banner for fallback
if is_fallback_active:
    st.warning("⚠️ Offline Mode: Displaying mock/cached logs due to connection failure to live stream.")

# Grid layout definition
col_lhs, col_rhs = st.columns([1, 1], gap="large")

# --- LHS: Raw Stream Viewer ---
with col_lhs:
    st.markdown("### 📋 Continuous Raw Log Stream")
    
    # Styled scrollable raw log container
    st.markdown(
        f"""
        <div class="raw-logs-box">
            <pre style="margin: 0; padding: 0; color: inherit; background-color: transparent; border: none; font-family: inherit;">{raw_logs_content}</pre>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- RHS: High-Performance Diagnostic Suite ---
with col_rhs:
    st.markdown("### 🛠️ High-Performance Diagnostic Suite")
    
    if raw_logs_content:
        # Parse exceptions into Polars DataFrame
        df = parse_laravel_logs(raw_logs_content)
        
        if not df.is_empty():
            # Display stats
            st.markdown(f"**Total Parsed Exception Blocks (LIFO Order):** `{len(df)}`")
            
            # Select exception dropdown
            options_list = [
                f"[{row['timestamp']}] [{row['environment.level']}] {row['exception_message'][:100]}..."
                for row in df.iter_rows(named=True)
            ]
            
            selected_idx = st.selectbox(
                "Pinpoint Exception Trace:",
                options=range(len(options_list)),
                format_func=lambda idx: options_list[idx]
            )
            
            selected_row = df.row(selected_idx, named=True)
            
            # Show exception detail
            st.markdown("#### Selected Exception Detail")
            st.code(selected_row["full_text"], language="text")
            
            # Analyze paradigm
            diagnosis = analyze_exception(selected_row["exception_message"])
            
            st.markdown(f"#### 🔍 Diagnosis: **{diagnosis['name']}**")
            st.info(diagnosis["explanation"])
            
            st.markdown("#### 🛠️ Suggested Remediation Snippet")
            st.code(diagnosis["remediation"], language="bash")
            
            # Webhook dispatch trigger
            st.markdown("---")
            if st.button("🚀 Dispatch Google Chat Notification", use_container_width=True):
                with st.spinner("Pushing payload to Google Chat..."):
                    success = dispatch_webhook(
                        webhook_url=webhook_url,
                        timestamp=selected_row["timestamp"],
                        env_level=selected_row["environment.level"],
                        message=selected_row["exception_message"],
                        diagnosis=diagnosis
                    )
                    if success:
                        st.success("Google Chat Alert dispatched successfully!")
        else:
            st.warning("No Laravel error exceptions parsed from the stream.")
    else:
        st.error("No raw log stream could be accessed. Please start local mock server or configure URL.")
