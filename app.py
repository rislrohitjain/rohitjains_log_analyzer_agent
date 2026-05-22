import streamlit as st
import polars as pl
import re
import requests
import os
import time
import base64
import psutil
from datetime import datetime
from pathlib import Path

# ==========================================
# 1. IMMEDIATE PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Rohit Jain's Portal - Log Analyzer Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hard Injection to override head element titles during low-level DOM construction
st.markdown("""
    <head>
        <title>Rohit Jain's Portal - Log Analyzer Agent</title>
    </head>
""", unsafe_allow_html=True)

# FORCE FIXED DARK THEME CONFIGURATION VIA CSS OVERRIDES
st.markdown("""
    <style>
        /* 1. Force absolute dark background onto all main structural containers */
        html, body, [data-testid="stAppViewContainer"], .stApp { 
            background-color: #0b0f19 !important; 
            color: #e2e8f0 !important; 
        }
        
        /* 2. Force Sidebar to lock into dark mode layout independently */
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div {
            background-color: #0f172a !important;
            color: #e2e8f0 !important;
            border-right: 1px solid #1e293b !important;
        }

        /* 3. Enforce light-colored typography over all standard labels and texts globally */
        h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, [data-testid="stWidgetLabel"] p { 
            color: #ffffff !important; 
        }
        
        /* 4. Smooth scrolling physics configuration */
        html { scroll-behavior: smooth; }
        
        /* Maximize vertical screen real estate - remove extra top space */
        .block-container { padding-top: 1rem !important; padding-bottom: 3rem !important; max-width: 100%; }
        div[data-testid="stHeader"] { height: 0px !important; background: transparent !important; }
        footer { visibility: hidden; }
        
        /* Responsive Header Layout */
        .responsive-header-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
            width: 100%;
        }
        .header-title-wrapper { flex: 1; min-width: 280px; }
        .header-title-main {
            font-size: clamp(1.2rem, 2.5vw, 2.2rem); 
            font-weight: bold;
            color: #ffffff !important;
            margin: 0;
            line-height: 1.2;
            background: linear-gradient(135deg, #06b6d4, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Scientific telemetry metrics cards */
        .stMetric { background: #111827 !important; padding: 12px; border-radius: 8px; border: 1px solid #1f2937 !important; }
        div[data-testid="stMetricValue"] > div { color: #ffffff !important; }
        div[data-testid="stMetricLabel"] > div { color: #94a3b8 !important; }
        
        /* Custom styled marquee container */
        .custom-marquee {
            background-color: #111827 !important;
            color: #06b6d4 !important;
            padding: 6px;
            font-weight: bold;
            font-size: 0.9rem;
            border-radius: 6px;
            border: 1px solid #1f2937 !important;
            margin-bottom: 15px;
        }
        
        /* Enforce internal scrollable zones */
        .scrollbox {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #1e293b !important;
            padding: 15px;
            border-radius: 6px;
            background-color: #030712 !important;
        }
        .branding-text { font-size: 0.85rem; line-height: 1.4; color: #cbd5e1 !important; }
        .section-watermark { font-size: 0.85rem; color: #06b6d4 !important; font-weight: bold; margin-bottom: 5px; }
        .section-watermark a { color: #06b6d4 !important; text-decoration: none; }
        
        /* Button layout details */
        div.stDownloadButton button { width: 100% !important; white-space: nowrap !important; }
        
        /* Native Pure-CSS Sidebar Jump Controllers */
        .nav-link-btn {
            display: block;
            text-align: center;
            background-color: #1e293b !important;
            color: #06b6d4 !important;
            padding: 8px;
            margin: 5px 0;
            border-radius: 6px;
            border: 1px solid #334155 !important;
            font-weight: bold;
            text-decoration: none !important;
            font-size: 0.85rem;
            transition: background 0.3s ease;
        }
        .nav-link-btn:hover { background-color: #334155 !important; color: #ffffff !important; }

        /* Scientific Custom Loader Animations */
        .loader-box {
            background: #0f172a !important;
            border-left: 4px solid #06b6d4 !important;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }
        .loader-spin {
            width: 24px;
            height: 24px;
            border: 3px solid #334155 !important;
            border-top: 3px solid #06b6d4 !important;
            border-radius: 50%;
            display: inline-block;
            animation: spin 0.8s linear infinite;
            vertical-align: middle;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .sidebar-inspect-box {
            background-color: #030712 !important;
            border: 1px dashed #334155 !important;
            border-radius: 6px;
            padding: 10px;
            margin-top: 10px;
        }

        /* 3D Scientific Profile Image Matrix Box */
        .profile-card-3d {
            perspective: 1000px;
            max-width: 140px;
            margin: 0 auto 15px auto;
        }
        .profile-img-3d {
            width: 100%;
            max-width: 140px;
            height: auto;
            border-radius: 12px;
            border: 2px solid #06b6d4;
            box-shadow: 0px 10px 20px rgba(6, 182, 212, 0.15), 
                        0px 4px 6px rgba(0, 0, 0, 0.3);
            transform: rotateX(10deg) rotateY(-10deg);
            transition: transform 0.5s ease, box-shadow 0.5s ease;
        }
        .profile-img-3d:hover {
            transform: rotateX(0deg) rotateY(0deg) scale(1.04);
            box-shadow: 0px 15px 25px rgba(6, 182, 212, 0.3), 
                        0px 6px 10px rgba(6, 182, 212, 0.2);
        }

        /* Raw log box container */
        .raw-logs-box {
            font-family: 'Fira Code', 'Courier New', Courier, monospace;
            font-size: 13px;
            background-color: #030712;
            color: #e2e8f0;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 12px;
            height: 480px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- PATH CONFIGURATIONS -----------------
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR / "uploads"
PHOTO_PATH = STATIC_DIR / "images" / "RohitPhoto.jpg"
RESUME_PATH = STATIC_DIR / "Resume_Original_Rohit_Jain.pdf"
SAMPLE_LOG_PATH = STATIC_DIR / "sample_laravel.log"

# Guarantee local folders are present
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Initialize Session State Variables
if "raw_logs" not in st.session_state:
    st.session_state.raw_logs = ""
if "last_fetched_url" not in st.session_state:
    st.session_state.last_fetched_url = ""
if "use_sample_logs" not in st.session_state:
    st.session_state.use_sample_logs = False

# Clock engine processing baseline
t_start = time.perf_counter()

# ==========================================
# 2. MODAL POPUP GATEWAYS (DIALOGS)
# ==========================================
def safe_dialog(title, width="large"):
    """Dynamically applies the available Streamlit dialog wrapper node to handle versioning traps."""
    if hasattr(st, "dialog"):
        return st.dialog(title, width=width)
    elif hasattr(st, "experimental_dialog"):
        return st.experimental_dialog(title, width=width)
    else:
        def legacy_decorator(func):
            def wrapper(*args, **kwargs):
                with st.container(border=True):
                    st.warning("⚠️ Dialog UI components are not natively supported in this environment version.")
                    return func(*args, **kwargs)
            return wrapper
        return legacy_decorator

@safe_dialog("📬 Direct Communications Matrix — Rohit Jain", width="large")
def show_contact_modal():
    st.markdown("""
    Feel free to reach out directly via any of the technical gateway routes below:
    
    * **Direct Contact Hotkey:** `+91 89469 19241`
    * **Production Email Inquiries:** `engrohitjain5@gmail.com`
    * **Digital Resourcing Node:** [Explore Digital Portfolio](https://rohitjain-resume.vercel.app/)
    * **Core Specialty Focus:** AI Solutions Architectures, RAG Orchestration, and Enterprise Full-Stack Microservices.
    
    ---
    *Click outside or use the top right 'X' to close this view.*
    """)

@safe_dialog("🖥️ Platform Architecture Deployment Profile", width="large")
def show_profile_modal():
    col1, col2 = st.columns([1.5, 3.5])
    with col1:
        if PHOTO_PATH.exists():
            try:
                with open(PHOTO_PATH, "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read()).decode()
                st.markdown(f"""
                <div class="profile-card-3d">
                    <img src="data:image/png;base64,{b64_string}" class="profile-img-3d" alt="Rohit Jain"/>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                st.image(str(PHOTO_PATH), use_container_width=True)
        else:
            st.warning("⚠️ Profile Image missing.")
    with col2:
        st.markdown("""
        ### **Rohit Jain**
        *AI Solutions Architect & Full Stack Architect | AI & Data Solutions*
        
        This workspace represents a production-grade optimization tier leveraging local compute, low-latency parsing engines, and fluid rendering.
        
        * 🎯 **AI Architecture & Advanced Workflows** — LLMs, Agentic Pipelines, & Enterprise Automation.
        * 💻 **Enterprise Full-Stack Engineering** — Highly optimized data microservices and real-time computing dashboards.
        * 📞 **+91 89469 19241** | ✉️ **engrohitjain5@gmail.com**
        * 🌐 [**Explore Digital Portfolio Resume**](https://rohitjain-resume.vercel.app/) — Technical project repositories and engineering background.
        """)

# ==========================================
# 3. SIDEBAR BRANDING & ASSET INFRASTRUCTURE
# ==========================================
with st.sidebar:
    st.markdown("### 🛠️ Platform Architect", help="System Architect profile details and rapid communication management console.")
    
    st.markdown("""
    <div class="branding-text">
        <strong>Rohit Jain</strong><br>
        <span style="color: #06b6d4; font-size:0.85rem;">AI Solutions Architect & Full Stack Architect</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🖥️ View Deployment Profile", use_container_width=True, help="Launches a secure popup detailing architectural specifications."):
        show_profile_modal()

    if st.button("📞 Quick Contact Portal", use_container_width=True, help="Launches a secure popup displaying communication paths."):
        show_contact_modal()
        
    st.markdown("---")
    
    # Ingestion Select Mode
    st.markdown("### 📡 Log Ingestion Matrix")
    ingestion_mode = st.radio(
        "Choose log ingestion mode:",
        options=["🌐 Live Stream URL", "📤 Upload Log File / Sample"],
        help="Connect to a live development log URL stream or load a file for local analysis."
    )
    
    st.markdown("---")
    
    # Mode-dependent sidebar items
    if ingestion_mode == "🌐 Live Stream URL":
        st.markdown("### ⚙️ Network Settings")
        network_timeout = st.slider(
            "Read Timeout (seconds)",
            min_value=2,
            max_value=60,
            value=10,
            help="Adjust log fetching timeout limit to prevent slow connection drops."
        )
        use_mock = st.checkbox(
            "Force Test Server Fallback", 
            value=False, 
            help="Connect to the local mock logs service running at http://127.0.0.1:8000/laravel.log"
        )
        uploaded_file = None
    else:
        uploaded_file = st.file_uploader(
            "Upload working laravel.log file", 
            type=["log", "txt"],
            help="Drop local Laravel log files here to parse and analyze."
        )
        
        if SAMPLE_LOG_PATH.exists():
            if st.button("🚀 Work with Sample Logs Instantly", use_container_width=True, help="Triggers instant log injection using system-backup datasets."):
                with st.spinner("Injecting Sample Log Environment..."):
                    st.session_state.use_sample_logs = True
                    try:
                        st.session_state.raw_logs = SAMPLE_LOG_PATH.read_text(encoding="utf-8")
                        st.toast("🎯 Sample logs loaded successfully!", icon="✅")
                    except Exception as e:
                        st.error(f"Failed to load sample log: {e}")
                    time.sleep(0.2)
                    st.rerun()
        else:
            st.caption("⚠️ Sample logs missing in static folder.")
            
    # Active File Inspector Node in Sidebar
    if (ingestion_mode == "📤 Upload Log File / Sample" and 
        (uploaded_file is not None or st.session_state.get("use_sample_logs", False))):
        st.markdown("#### 📂 Active File Inspector Node", help="Quick access tab validating file integrity schemas.")
        with st.container():
            st.markdown('<div class="sidebar-inspect-box">', unsafe_allow_html=True)
            if uploaded_file is not None:
                st.caption(f"📁 **Filename:** `{uploaded_file.name}`")
                st.caption(f"⚖️ **Allocated Stream Size:** {uploaded_file.size / 1024:.2f} KB")
            else:
                st.caption("📁 **Filename:** `sample_laravel.log (System Cache)`")
            st.markdown('<a class="nav-link-btn" href="#table-section" style="padding:4px; font-size:0.75rem;">🔍 Jump Directly To Filtered Data</a>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Webhook Integration In Sidebar
    st.markdown("### 💬 Google Chat Integration")
    webhook_url = st.text_input(
        "Webhook Endpoint Channel",
        value="",
        type="password",
        placeholder="https://chat.googleapis.com/v1/spaces/...",
        help="Paste the Google Chat webhook URL here."
    )
    
    st.markdown("---")
    
    # Pure-CSS jump navigation links
    st.markdown("### 🗺️ Quick Workspace Navigation", help="Use these anchors to fluidly shift your viewport focus.")
    st.markdown('<a class="nav-link-btn" href="#top-anchor">⬆️ Scroll To Top Banner</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#filter-section">🔍 Jump To Query Matrix</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#analytics-section">📊 Jump To Metrics Charts</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#lhs-raw-section">📋 Jump To Raw Stream</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link-btn" href="#diagnostics-section">🛠️ Jump To Hardware Footer</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📥 Developer Assets & Utilities", help="Download official distribution copies of engineering blueprints.")
    
    # Binary download handler for CV
    if RESUME_PATH.exists():
        with open(RESUME_PATH, "rb") as pdf_file:
            st.download_button(
                label="📄 Download Professional Resume",
                data=pdf_file.read(),
                file_name="Resume_Original_Rohit_Jain.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="sidebar_resume_btn"
            )
            
    # Download sample laravel.log
    if SAMPLE_LOG_PATH.exists():
        try:
            sample_data = SAMPLE_LOG_PATH.read_text(encoding="utf-8")
            st.download_button(
                label="📋 Download Sample laravel.log",
                data=sample_data,
                file_name="laravel.log",
                mime="text/plain",
                use_container_width=True,
                key="sidebar_sample_log_btn"
            )
        except Exception:
            st.caption("⚠️ Unable to load sample logs for download.")

# --- STRUCTURAL SCROLL ANCHOR ---
st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# ==========================================
# 4. MAIN INTERFACE HEADER DISPLAY
# ==========================================
st.markdown("""
<div class="responsive-header-container">
    <div class="header-title-wrapper">
        <h1 class="header-title-main">⚡ Rohit Jain's Portal - Log Analyzer Agent</h1>
        <div class='section-watermark'>Designed & Engineered by <a href='https://rohitjain-resume.vercel.app/' target='_blank' style='color:#06b6d4; text-decoration:none;'>Rohit Jain</a></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="custom-marquee">
        <marquee behavior="scroll" direction="left" scrollamount="6">
            📢 Laravel Log Analyzer Engine Online. Ingest a remote log stream URL or upload a laravel.log file to trigger advanced diagnostics. 
            | 📢 लारवेल लॉग विश्लेषक इंजन ऑनलाइन है। उन्नत डायग्नोस्टिक्स शुरू करने के लिए रिमोट लॉग स्ट्रीम URL दर्ज करें या laravel.log फ़ाइल अपलोड करें।
        </marquee>
    </div>
""", unsafe_allow_html=True)

# ----------------- PARSING ENGINE (POLARS ONLY) -----------------
def parse_laravel_logs(log_text: str) -> pl.DataFrame:
    """
    Parses Laravel logs using regular expressions and returns a Polars DataFrame.
    Laravel pattern: [YYYY-MM-DD HH:MM:SS] environment.level: message [stacktrace]
    """
    # Regex to capture: [timestamp] environment.level: message
    # And lazily capture all content up to the next timestamp or end of file.
    pattern = re.compile(
        r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+([a-zA-Z0-9_-]+\.[A-Z]+):\s+(.*?)(?=\n^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]|\Z)',
        re.MULTILINE | re.DOTALL
    )
    
    timestamps = []
    dates = []
    environments = []
    levels = []
    error_types = []
    file_names = []
    file_paths = []
    line_numbers = []
    messages = []
    full_texts = []
    
    for match in pattern.finditer(log_text):
        ts = match.group(1)
        env_lvl = match.group(2)
        body = match.group(3).strip()
        
        # Date extraction
        dt_str = ts.split(" ")[0]
        
        # Split environment & level
        if "." in env_lvl:
            env, lvl = env_lvl.split(".", 1)
        else:
            env, lvl = "local", env_lvl
            
        # Message is first line
        lines = body.split("\n", 1)
        msg = lines[0]
        
        # Exception type extraction
        err_type = "Generic Exception"
        type_match = re.match(r'^\\?([a-zA-Z0-9_\\]+(?:Exception|Error|FatalError))\b', msg)
        if type_match:
            err_type = type_match.group(1).split('\\')[-1]
            
        # File & line number extraction
        file_match = re.search(r'([\w\.\-\/\\]+\.php)(?::|\s+line\s+|\()(\d+)', body)
        if file_match:
            f_path = file_match.group(1)
            line_no = int(file_match.group(2))
            f_name = os.path.basename(f_path)
        else:
            f_path = "Unknown File"
            f_name = "Unknown File"
            line_no = 0
            
        timestamps.append(ts)
        dates.append(dt_str)
        environments.append(env)
        levels.append(lvl)
        error_types.append(err_type)
        file_names.append(f_name)
        file_paths.append(f_path)
        line_numbers.append(line_no)
        messages.append(msg)
        full_texts.append(f"[{ts}] {env_lvl}: {body}")
        
    if not timestamps:
        # Fallback if logs don't match the regex perfectly
        lines = [line.strip() for line in log_text.splitlines() if line.strip()]
        if lines:
            for line in lines:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                dt_str = ts.split(" ")[0]
                timestamps.append(ts)
                dates.append(dt_str)
                environments.append("local")
                levels.append("ERROR")
                error_types.append("Generic Error")
                file_names.append("Unknown File")
                file_paths.append("Unknown File")
                line_numbers.append(0)
                messages.append(line)
                full_texts.append(line)
        else:
            return pl.DataFrame({
                "timestamp": pl.Series([], dtype=pl.Utf8),
                "date": pl.Series([], dtype=pl.Utf8),
                "environment": pl.Series([], dtype=pl.Utf8),
                "level": pl.Series([], dtype=pl.Utf8),
                "error_type": pl.Series([], dtype=pl.Utf8),
                "file_name": pl.Series([], dtype=pl.Utf8),
                "file_path": pl.Series([], dtype=pl.Utf8),
                "line_number": pl.Series([], dtype=pl.Int64),
                "exception_message": pl.Series([], dtype=pl.Utf8),
                "full_text": pl.Series([], dtype=pl.Utf8)
            })

    # Build Polars DataFrame
    df = pl.DataFrame({
        "timestamp": timestamps,
        "date": dates,
        "environment": environments,
        "level": levels,
        "error_type": error_types,
        "file_name": file_names,
        "file_path": file_paths,
        "line_number": line_numbers,
        "exception_message": messages,
        "full_text": full_texts
    })
    
    # Sort LIFO - newest first
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
        
    webhook_url = webhook_url.strip()
    
    if not (webhook_url.startswith("https://chat.googleapis.com/v1/spaces/") or 
            webhook_url.startswith("https://chat.googleapis.com/v1/spaces%2F") or 
            "chat.googleapis.com" in webhook_url):
        st.error("❌ Invalid Webhook URL format.")
        st.info("💡 **Make sure you copied the Webhook API URL, not the browser address bar space room URL.**\n\n"
                "To get the correct API URL:\n"
                "1. Open Google Chat space.\n"
                "2. Click the Space Name dropdown -> **Apps & Integrations** -> **Webhooks**.\n"
                "3. Click **Add Webhook**, name it, and copy the generated URL starting with `https://chat.googleapis.com/`.")
        return False
        
    if "key=" not in webhook_url or "token=" not in webhook_url:
        st.error("❌ Invalid Webhook URL. The Webhook URL must contain authentication parameters (`key` and `token`).")
        st.info("💡 Ensure you have copied the entire URL from the Webhook configuration panel without truncating it.")
        return False

    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    text_content = (
        f"🚨 **Laravel Exception Alert**\n"
        f"📅 **Timestamp:** `{timestamp}`\n"
        f"🏷️ **Env/Level:** `{env_level}`\n"
        f"📝 **Exception Summary:** `{message}`\n\n"
        f"🔍 **Diagnosis:** {diagnosis['name']}\n"
        f"ℹ️ *{diagnosis['explanation']}*\n\n"
        f"🛠️ **Remediation Command:**\n```bash\n{diagnosis['remediation']}\n```"
    )
    
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
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10, allow_redirects=False)
        
        if response.status_code == 200:
            return True
        elif response.status_code in (301, 302, 307, 308):
            st.error(f"❌ Webhook URL redirected (HTTP {response.status_code}).")
            st.info("💡 You may have pasted the browser chat space room URL instead of the Webhook API URL. Google Chat's web client redirects unauthorized API requests to Google Account login pages.")
            return False
        elif response.status_code == 401:
            st.error("❌ Webhook Dispatch Failed: 401 Unauthorized.")
            st.info("💡 **Your Webhook API Key or Token is invalid or expired.** Please verify the URL or create a new Webhook in your Google Chat Space settings.")
            return False
        else:
            st.error(f"Failed to deliver payload. Server responded with {response.status_code}: {response.text}")
            return False
    except Exception as e:
        st.error(f"Network error during dispatch: {str(e)}")
        return False

# ==========================================
# 5. LOG STREAM FETCHING & INGESTION BLOCK
# ==========================================
raw_logs_content = ""
fetch_error = ""
is_fallback_active = False

if ingestion_mode == "🌐 Live Stream URL":
    col_url, col_btn = st.columns([5, 1], gap="medium")
    with col_url:
        log_url = st.text_input(
            "Log Stream URL",
            value="/static/sample_laravel.log",
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
            if target_url.startswith("static/") or target_url.startswith("/static/"):
                stripped_path = target_url.lstrip("/")
                local_file_path = BASE_DIR / stripped_path
                with st.spinner(f"Loading local static file: {local_file_path}..."):
                    if local_file_path.exists():
                        raw_logs_content = local_file_path.read_text(encoding="utf-8")
                    else:
                        fetch_error = f"Local File Not Found: {local_file_path}"
            else:
                with st.spinner(f"Scraping logs from: {target_url}..."):
                    response = requests.get(target_url, timeout=network_timeout)
                    if response.status_code == 200:
                        raw_logs_content = response.text
                    else:
                        fetch_error = f"HTTP Error {response.status_code}: Unable to read target stream."
        except Exception as e:
            fetch_error = f"Ingestion Failed: {str(e)}"
            
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
                - Switch the Ingestion Mode to **Upload Log File / Sample** in the sidebar.
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
                if SAMPLE_LOG_PATH.exists():
                    try:
                        raw_logs_content = SAMPLE_LOG_PATH.read_text(encoding="utf-8")
                        st.info("ℹ️ Successfully loaded mock log fallback (Offline Static).")
                    except Exception:
                        raw_logs_content = ""
                if not raw_logs_content:
                    # Final hard fallback static text
                    sample_fallback = """[2026-05-22 14:40:43] local.ERROR: PDOException: SQLSTATE[HY000] [2002] Connection refused {"exception":"[object] (PDOException(code: 2002): SQLSTATE[HY000] [2002] Connection refused at /var/www/html/vendor/laravel/framework/src/Illuminate/Database/Connectors/Connector.php:70)"}
[2026-05-22 14:45:43] production.ERROR: ErrorException: file_put_contents(/var/www/html/storage/framework/views/w7f82h39): Failed to open stream: Permission denied {"exception":"[object] (ErrorException(code: 0): file_put_contents...)"}"""
                    raw_logs_content = sample_fallback
                    st.info("ℹ️ Successfully loaded static mock logs.")
        
        # Cache in session state
        st.session_state.raw_logs = raw_logs_content
        st.session_state.last_fetched_url = target_url
    else:
        # Use cached logs
        raw_logs_content = st.session_state.raw_logs

else:  # Upload Log File / Sample
    if uploaded_file is not None:
        raw_logs_content = uploaded_file.getvalue().decode("utf-8")
        st.session_state.last_fetched_url = "uploaded_file"
        st.session_state.raw_logs = raw_logs_content
        st.session_state.use_sample_logs = False
    else:
        if st.session_state.get("use_sample_logs", False):
            raw_logs_content = st.session_state.raw_logs
        else:
            raw_logs_content = ""

# Visual banner for fallback
if is_fallback_active:
    st.warning("⚠️ Offline Mode: Displaying mock/cached logs due to connection failure to live stream.")

# ==========================================
# 6. ANALYTICS & ADVANCED DRILL-DOWN FILTERS
# ==========================================
if raw_logs_content:
    # 1. Parse into Polars dataframe
    df_raw = parse_laravel_logs(raw_logs_content)
    
    if not df_raw.is_empty():
        # --- SECTION: TELEMETRY METRIC CARDS ---
        st.markdown("<br>", unsafe_allow_html=True)
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        total_exceptions = len(df_raw)
        unique_types = len(df_raw["error_type"].unique())
        
        # Calculate level breakdown ratio
        level_counts = df_raw.group_by("level").agg(pl.len().alias("count")).sort("count", descending=True)
        most_common_level = level_counts[0, "level"] if len(level_counts) > 0 else "N/A"
        most_common_level_count = level_counts[0, "count"] if len(level_counts) > 0 else 0
        ratio_str = f"{most_common_level} ({most_common_level_count}/{total_exceptions})"
        
        # Most common error type
        type_counts = df_raw.group_by("error_type").agg(pl.len().alias("count")).sort("count", descending=True)
        most_common_type = type_counts[0, "error_type"] if len(type_counts) > 0 else "N/A"
        
        with m_col1:
            st.metric(label="📋 Total Exceptions", value=str(total_exceptions), delta="LIFO Order Active")
        with m_col2:
            st.metric(label="🔍 Unique Exception Types", value=str(unique_types), delta="Distinct Signatures")
        with m_col3:
            st.metric(label="🏷️ Dominant Level", value=ratio_str, delta="Error Distribution")
        with m_col4:
            st.metric(label="🚨 Main Culprit Class", value=most_common_type[:20], delta="Highest Frequency")
            
        # --- SECTION: DRILL-DOWN FILTER MATRIX ---
        st.markdown('<div id="filter-section"></div>', unsafe_allow_html=True)
        with st.expander("🔍 1. Filter Data Your Way (Advanced Query Matrix)", expanded=True):
            st.markdown("<div class='section-watermark'>Pipeline Layer: Smart Query Filter Engine by <a href='https://rohitjain-resume.vercel.app/' target='_blank' style='color:#06b6d4;'>Rohit Jain</a></div>", unsafe_allow_html=True)
            
            # Sub-filters grid
            df_filtered = df_raw
            
            # 1. Date Range
            unique_dates = df_raw["date"].unique().sort().to_list()
            if unique_dates:
                min_date_val = datetime.strptime(unique_dates[0], "%Y-%m-%d").date()
                max_date_val = datetime.strptime(unique_dates[-1], "%Y-%m-%d").date()
                
                if min_date_val == max_date_val:
                    st.info(f"📅 Logs are locked to date: `{min_date_val}`")
                    df_filtered = df_filtered.filter(pl.col("date") == min_date_val.strftime("%Y-%m-%d"))
                else:
                    date_range = st.date_input(
                        "Filter by Date Range:",
                        value=(min_date_val, max_date_val),
                        min_value=min_date_val,
                        max_value=max_date_val
                    )
                    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                        start_d, end_d = date_range
                        df_filtered = df_filtered.filter(
                            (pl.col("date") >= start_d.strftime("%Y-%m-%d")) &
                            (pl.col("date") <= end_d.strftime("%Y-%m-%d"))
                        )
            
            # 2. Level, Env, Exception Types
            levels_list = df_raw["level"].unique().to_list()
            envs_list = df_raw["environment"].unique().to_list()
            types_list = df_raw["error_type"].unique().to_list()
            
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                selected_levels = st.multiselect("Filter by Level:", options=levels_list, default=levels_list)
            with col_f2:
                selected_envs = st.multiselect("Filter by Env:", options=envs_list, default=envs_list)
            with col_f3:
                selected_types = st.multiselect("Filter by Exception:", options=types_list, default=types_list)
                
            # 3. File Basenames, File Search & Message Search
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                search_code = st.text_input(
                    "Search Code Reference / File Name:", 
                    placeholder="e.g. Connector.php, /vendor/laravel/..., or line number :70"
                )
            with col_s2:
                search_msg = st.text_input(
                    "Search Exception Message:", 
                    placeholder="e.g. Connection refused, Permission denied"
                )
                
            # Execute Polars dynamic filter pipelines
            if selected_levels:
                df_filtered = df_filtered.filter(pl.col("level").is_in(selected_levels))
            if selected_envs:
                df_filtered = df_filtered.filter(pl.col("environment").is_in(selected_envs))
            if selected_types:
                df_filtered = df_filtered.filter(pl.col("error_type").is_in(selected_types))
                
            if search_code:
                df_filtered = df_filtered.filter(
                    pl.col("file_path").str.contains(f"(?i){re.escape(search_code)}") |
                    pl.col("file_name").str.contains(f"(?i){re.escape(search_code)}") |
                    pl.col("line_number").cast(pl.String).str.contains(search_code)
                )
                
            if search_msg:
                df_filtered = df_filtered.filter(
                    pl.col("exception_message").str.contains(f"(?i){re.escape(search_msg)}") |
                    pl.col("full_text").str.contains(f"(?i){re.escape(search_msg)}")
                )

        # --- SECTION: TWO COLUMN DASHBOARD LAYOUT ---
        col_lhs, col_rhs = st.columns([1, 1], gap="large")
        
        # --- LHS PANEL: Parsed Grid & Visualization Studio ---
        with col_lhs:
            st.markdown('<div id="table-section"></div>', unsafe_allow_html=True)
            st.markdown(f"### 📊 2. Parsed Exception Records ({len(df_filtered)} items)")
            
            st.markdown('<div class="scrollbox">', unsafe_allow_html=True)
            # Filtered columns overview
            columns_display = ["timestamp", "environment", "level", "error_type", "file_name", "line_number", "exception_message"]
            if not df_filtered.is_empty():
                st.dataframe(
                    df_filtered.select(columns_display).to_pandas(),
                    use_container_width=True,
                    height=280
                )
            else:
                st.warning("No records match the current filter selection.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # --- GRAPHICAL CANVAS ---
            st.markdown('<div id="analytics-section"></div>', unsafe_allow_html=True)
            st.markdown("### 📈 3. Interactive Visualization Studio")
            
            if not df_filtered.is_empty():
                import plotly.express as px
                
                viz_col1, viz_col2 = st.columns(2)
                
                with viz_col1:
                    # Level allocation breakdown ratio (Pie)
                    level_counts_filtered = df_filtered.group_by("level").agg(pl.len().alias("count")).sort("count", descending=True)
                    fig_pie = px.pie(
                        level_counts_filtered.to_pandas(),
                        names="level",
                        values="count",
                        title="Error Levels Distribution",
                        template="plotly_dark",
                        color_discrete_sequence=px.colors.sequential.Electric
                    )
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10))
                    st.plotly_chart(fig_pie, use_container_width=True, theme=None)
                    
                with viz_col2:
                    # Exception Class Frequency (Bar)
                    type_counts_filtered = df_filtered.group_by("error_type").agg(pl.len().alias("count")).sort("count", descending=True).head(5)
                    fig_bar = px.bar(
                        type_counts_filtered.to_pandas(),
                        x="error_type",
                        y="count",
                        title="Top Exception Classes",
                        template="plotly_dark",
                        color_discrete_sequence=["#06b6d4"]
                    )
                    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10))
                    st.plotly_chart(fig_bar, use_container_width=True, theme=None)
                    
                # Time Trend Line
                date_counts_filtered = df_filtered.group_by("date").agg(pl.len().alias("count")).sort("date")
                fig_trend = px.line(
                    date_counts_filtered.to_pandas(),
                    x="date",
                    y="count",
                    title="Exceptions Logged Over Time",
                    template="plotly_dark",
                    markers=True
                )
                fig_trend.update_traces(line=dict(color="#10b981", width=2.5))
                fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=220, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_trend, use_container_width=True, theme=None)
            else:
                st.info("Ingest data and refine criteria filter to display visualization studio.")
                
        # --- RHS PANEL: Raw Stream & Diagnostic Suite ---
        with col_rhs:
            st.markdown('<div id="lhs-raw-section"></div>', unsafe_allow_html=True)
            st.markdown("### 📋 4. Raw Exception Stream Viewer")
            st.markdown(
                f"""
                <div class="raw-logs-box">
                    <pre style="margin: 0; padding: 0; color: inherit; background-color: transparent; border: none; font-family: inherit;">{raw_logs_content}</pre>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # --- Selected Exception Diagnostic Pinned Suite ---
            st.markdown("### 🛠️ 5. Pinned Exception Diagnostic Suite")
            
            if not df_filtered.is_empty():
                options_list = [
                    f"[{row['timestamp']}] [{row['level']}] {row['exception_message'][:70]}..."
                    for row in df_filtered.iter_rows(named=True)
                ]
                
                selected_idx = st.selectbox(
                    "Pinpoint Exception Trace:",
                    options=range(len(options_list)),
                    format_func=lambda idx: options_list[idx],
                    key="pinned_exception_trace_selector"
                )
                
                selected_row = df_filtered.row(selected_idx, named=True)
                
                st.markdown("#### Selected Exception Trace Detail")
                st.code(selected_row["full_text"], language="text")
                
                # Analyze Paradigm
                diagnosis = analyze_exception(selected_row["exception_message"])
                
                st.markdown(f"#### 🔍 Diagnosis: **{diagnosis['name']}**")
                st.info(diagnosis["explanation"])
                
                st.markdown("#### 🛠️ Suggested Remediation Command")
                st.code(diagnosis["remediation"], language="bash")
                
                # Webhook Dispatch
                st.markdown("---")
                if st.button("🚀 Dispatch Google Chat Notification", use_container_width=True, key="dispatch_chat_webhook_btn"):
                    with st.spinner("Pushing payload to Google Chat..."):
                        success = dispatch_webhook(
                            webhook_url=webhook_url,
                            timestamp=selected_row["timestamp"],
                            env_level=f"{selected_row['environment']}.{selected_row['level']}",
                            message=selected_row["exception_message"],
                            diagnosis=diagnosis
                        )
                        if success:
                            st.success("Google Chat Alert dispatched successfully!")
            else:
                st.warning("Empty records scope. Refine filters to display and diagnostic selected trace details.")
    else:
        st.warning("No Laravel error exceptions parsed from the log content.")
else:
    st.info("""
    📡 Log Ingestion Matrix Idle. Ingest a live stream URL or upload a log file in the left sidebar console to trigger advanced telemetry analysis.
    """)

# ==========================================
# 7. PERFORMANCE & DIAGNOSTICS TELEMETRY FOOTER
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div id="diagnostics-section"></div>', unsafe_allow_html=True)
with st.expander("🛠️ Compute & Engine Execution Profile Diagnostics", expanded=True):
    st.markdown("<div class='section-watermark'>Diagnostics Layer: Low-Level Profiling Core by <a href='https://rohitjain-resume.vercel.app/' target='_blank' style='color:#06b6d4;'>Rohit Jain</a></div>", unsafe_allow_html=True)
    st.markdown('<div class="scrollbox" style="max-height: 180px; background-color: #020617 !important;">', unsafe_allow_html=True)
    
    process = psutil.Process(os.getpid())
    execution_delta = time.perf_counter() - t_start
    rss_memory_mb = process.memory_info().rss / (1024 * 1024)
    system_cpu = psutil.cpu_percent()
    system_ram = psutil.virtual_memory().percent
    
    foot_1, foot_2, foot_3, foot_4 = st.columns(4)
    with foot_1:
        st.metric(label="⏱️ Engine Computational Time", value=f"{execution_delta:.4f}s", delta="Polars Ultra-Fast Execution")
    with foot_2:
        st.metric(label="💾 Application Dedicated RAM", value=f"{rss_memory_mb:.1f} MB", delta="Minimized Memory Allocation")
    with foot_3:
        st.metric(label="🎛️ Active Server Core Load", value=f"{system_cpu}%", delta="Dynamic Scaling Enabled")
    with foot_4:
        st.metric(label="🧠 Global System Memory Load", value=f"{system_ram}%", delta="Optimal Platform Performance")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer Layout
st.markdown(
    "<div style='text-align: center; color: #cbd5e1 !important; padding-top: 15px; font-size: 0.85rem; font-weight: bold;'>"
    "Designed & Developed by <a href='https://rohitjain-resume.vercel.app/' target='_blank' style='color:#06b6d4 !important; text-decoration:none;'>Rohit Jain</a> • Optimized for Mobile Phones, Tablets, and 4K Office Projectors"
    "</div>",
    unsafe_allow_html=True
)
