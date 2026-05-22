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
    Parses logs from multiple technologies (Laravel, PHP, Python, NodeJS, .NET, Java, Go, HTML)
    using regular expressions and returns a Polars DataFrame.
    """
    text_lower = log_text.lower()
    tech = "generic"
    if any(k in text_lower for k in ["laravel", "artisan", "eloquent"]):
        tech = "laravel"
    elif "traceback (most recent call last):" in text_lower or ".py\", line " in text_lower or ".py:" in text_lower:
        tech = "python"
    elif "node_modules" in text_lower or (re.search(r'\b(TypeError|ReferenceError|SyntaxError|RangeError)\b', log_text) and "at " in text_lower) or ".js:" in text_lower or ".ts:" in text_lower:
        tech = "nodejs"
    elif "system.nullreferenceexception" in text_lower or "system.argumentnullexception" in text_lower or re.search(r'in [\w\:\\]+\.cs:line \d+', log_text):
        tech = "dotnet"
    elif "nullpointerexception" in text_lower or "noclassdeffounderror" in text_lower or ".java:" in text_lower:
        tech = "java"
    elif "panic: runtime error" in text_lower or "goroutine " in text_lower:
        tech = "go"
    elif "php fatal error" in text_lower or "php warning" in text_lower or "php notice" in text_lower or ".php on line" in text_lower:
        tech = "php"
    elif "doctype html" in text_lower or "<html>" in text_lower or "cors policy" in text_lower or "domexception" in text_lower:
        tech = "html"
        
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

    if tech == "laravel":
        pattern = re.compile(
            r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+([a-zA-Z0-9_-]+\.[A-Z]+):\s+(.*?)(?=\n^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]|\Z)',
            re.MULTILINE | re.DOTALL
        )
        for match in pattern.finditer(log_text):
            ts = match.group(1)
            env_lvl = match.group(2)
            body = match.group(3).strip()
            
            dt_str = ts.split(" ")[0]
            if "." in env_lvl:
                env, lvl = env_lvl.split(".", 1)
            else:
                env, lvl = "local", env_lvl
                
            lines = body.split("\n", 1)
            msg = lines[0]
            
            err_type = "Generic Exception"
            type_match = re.match(r'^\\?([a-zA-Z0-9_\\]+(?:Exception|Error|FatalError))\b', msg)
            if type_match:
                err_type = type_match.group(1).split('\\')[-1]
                
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

    elif tech == "python":
        pattern = re.compile(
            r'((?:Traceback \(most recent call last\):|File ".*?").*?(?=\n(?:Traceback \(most recent call last\):|File ".*?")|\Z))',
            re.MULTILINE | re.DOTALL
        )
        blocks = pattern.findall(log_text)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            lines = block.splitlines()
            msg = lines[-1]
            err_type = "Python Error"
            type_match = re.match(r'^([a-zA-Z0-9_]+Error|Exception):\s*(.*)', msg)
            if type_match:
                err_type = type_match.group(1)
            
            file_matches = list(re.finditer(r'File "([^"]+)", line (\d+), in (\w+)', block))
            if file_matches:
                last_match = file_matches[-1]
                f_path = last_match.group(1)
                line_no = int(last_match.group(2))
                f_name = os.path.basename(f_path)
            else:
                f_path = "Unknown File"
                f_name = "Unknown File"
                line_no = 0
                
            ts_match = re.search(r'\[?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\]?', block)
            ts = ts_match.group(1) if ts_match else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dt_str = ts.split(" ")[0] if " " in ts else ts.split("T")[0]
            
            timestamps.append(ts)
            dates.append(dt_str)
            environments.append("local")
            levels.append("ERROR")
            error_types.append(err_type)
            file_names.append(f_name)
            file_paths.append(f_path)
            line_numbers.append(line_no)
            messages.append(msg)
            full_texts.append(block)

    elif tech == "nodejs":
        pattern = re.compile(
            r'((?:\b[a-zA-Z0-9_]+Error|Error|Exception\b):\s+.*?(?=\n(?:\b[a-zA-Z0-9_]+Error|Error|Exception\b):\s+|\Z))',
            re.MULTILINE | re.DOTALL
        )
        blocks = pattern.findall(log_text)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            lines = block.splitlines()
            msg = lines[0]
            err_type = "NodeJS Error"
            type_match = re.match(r'^([a-zA-Z0-9_]+Error|Error):\s*(.*)', msg)
            if type_match:
                err_type = type_match.group(1)
                
            file_match = re.search(r'at\s+.*?\((.*?):(\d+):(\d+)\)|at\s+(.*?):(\d+):(\d+)', block)
            if file_match:
                f_path = file_match.group(1) or file_match.group(4)
                line_no = int(file_match.group(2) or file_match.group(5))
                f_name = os.path.basename(f_path)
            else:
                f_path = "Unknown File"
                f_name = "Unknown File"
                line_no = 0
                
            ts_match = re.search(r'\[?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\]?', block)
            ts = ts_match.group(1) if ts_match else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dt_str = ts.split(" ")[0] if " " in ts else ts.split("T")[0]
            
            timestamps.append(ts)
            dates.append(dt_str)
            environments.append("local")
            levels.append("ERROR")
            error_types.append(err_type)
            file_names.append(f_name)
            file_paths.append(f_path)
            line_numbers.append(line_no)
            messages.append(msg)
            full_texts.append(block)

    elif tech == "dotnet":
        pattern = re.compile(
            r'((?:System\.[a-zA-Z0-9_\.]+Exception|Exception):\s+.*?(?=\n(?:System\.[a-zA-Z0-9_\.]+Exception|Exception):\s+|\Z))',
            re.MULTILINE | re.DOTALL
        )
        blocks = pattern.findall(log_text)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            lines = block.splitlines()
            msg = lines[0]
            err_type = "DotNet Exception"
            type_match = re.match(r'^([a-zA-Z0-9_\.]+Exception):\s*(.*)', msg)
            if type_match:
                err_type = type_match.group(1).split('.')[-1]
                
            file_match = re.search(r'in\s+([\w\.\-\/\\:]+\.cs):line\s+(\d+)', block)
            if file_match:
                f_path = file_match.group(1)
                line_no = int(file_match.group(2))
                f_name = os.path.basename(f_path)
            else:
                f_path = "Unknown File"
                f_name = "Unknown File"
                line_no = 0
                
            ts_match = re.search(r'\[?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\]?', block)
            ts = ts_match.group(1) if ts_match else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dt_str = ts.split(" ")[0] if " " in ts else ts.split("T")[0]
            
            timestamps.append(ts)
            dates.append(dt_str)
            environments.append("local")
            levels.append("ERROR")
            error_types.append(err_type)
            file_names.append(f_name)
            file_paths.append(f_path)
            line_numbers.append(line_no)
            messages.append(msg)
            full_texts.append(block)

    elif tech == "java":
        pattern = re.compile(
            r'((?:\b[a-zA-Z0-9_\.]+Exception|Exception\b):\s+.*?(?=\n(?:\b[a-zA-Z0-9_\.]+Exception|Exception\b):\s+|\Z))',
            re.MULTILINE | re.DOTALL
        )
        blocks = pattern.findall(log_text)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            lines = block.splitlines()
            msg = lines[0]
            err_type = "Java Exception"
            type_match = re.match(r'^([a-zA-Z0-9_\.]+Exception):\s*(.*)', msg)
            if type_match:
                err_type = type_match.group(1).split('.')[-1]
                
            file_match = re.search(r'at\s+[\w\.]+\.([\w]+)\(([\w\.\-]+\.java):(\d+)\)', block)
            if file_match:
                f_name = file_match.group(2)
                f_path = file_match.group(2)
                line_no = int(file_match.group(3))
            else:
                f_path = "Unknown File"
                f_name = "Unknown File"
                line_no = 0
                
            ts_match = re.search(r'\[?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\]?', block)
            ts = ts_match.group(1) if ts_match else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dt_str = ts.split(" ")[0] if " " in ts else ts.split("T")[0]
            
            timestamps.append(ts)
            dates.append(dt_str)
            environments.append("local")
            levels.append("ERROR")
            error_types.append(err_type)
            file_names.append(f_name)
            file_paths.append(f_path)
            line_numbers.append(line_no)
            messages.append(msg)
            full_texts.append(block)

    elif tech == "go":
        pattern = re.compile(
            r'(panic:\s+.*?(?=\npanic:\s+|\Z))',
            re.MULTILINE | re.DOTALL
        )
        blocks = pattern.findall(log_text)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            lines = block.splitlines()
            msg = lines[0]
            err_type = "Go Panic"
            
            file_match = re.search(r'([\w\.\-\/\\:]+\.go):(\d+)', block)
            if file_match:
                f_path = file_match.group(1)
                line_no = int(file_match.group(2))
                f_name = os.path.basename(f_path)
            else:
                f_path = "Unknown File"
                f_name = "Unknown File"
                line_no = 0
                
            ts_match = re.search(r'\[?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\]?', block)
            ts = ts_match.group(1) if ts_match else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dt_str = ts.split(" ")[0] if " " in ts else ts.split("T")[0]
            
            timestamps.append(ts)
            dates.append(dt_str)
            environments.append("local")
            levels.append("PANIC")
            error_types.append(err_type)
            file_names.append(f_name)
            file_paths.append(f_path)
            line_numbers.append(line_no)
            messages.append(msg)
            full_texts.append(block)

    elif tech == "php":
        pattern = re.compile(
            r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+PHP\s+([A-Za-z\s]+):\s+(.*?)\s+in\s+([\w\.\-\/\\:]+)\s+on\s+line\s+(\d+)',
            re.MULTILINE
        )
        for match in pattern.finditer(log_text):
            ts = match.group(1)
            lvl = match.group(2).strip().upper()
            msg = match.group(3).strip()
            f_path = match.group(4)
            line_no = int(match.group(5))
            f_name = os.path.basename(f_path)
            
            dt_str = ts.split(" ")[0]
            err_type = "PHP Error"
            
            timestamps.append(ts)
            dates.append(dt_str)
            environments.append("local")
            levels.append(lvl)
            error_types.append(err_type)
            file_names.append(f_name)
            file_paths.append(f_path)
            line_numbers.append(line_no)
            messages.append(msg)
            full_texts.append(match.group(0))

    elif tech == "html":
        lines = [line.strip() for line in log_text.splitlines() if line.strip()]
        for line in lines:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dt_str = ts.split(" ")[0]
            err_type = "HTML/CSS Error"
            if "cors" in line.lower() or "access-control-allow-origin" in line.lower():
                err_type = "CORS Access Blocked"
            elif "404" in line.lower() or "not found" in line.lower():
                err_type = "Asset Load Failure"
            elif "dom" in line.lower() or "queryselector" in line.lower() or "addeventlistener" in line.lower():
                err_type = "DOMException"
                
            file_match = re.search(r'([\w\.\-\/\\]+\.(?:html|htm|css|js|png|jpg|gif|svg|ico))', line)
            if file_match:
                f_path = file_match.group(1)
                f_name = os.path.basename(f_path)
            else:
                f_path = "Unknown File"
                f_name = "Unknown File"
                
            line_match = re.search(r'(?::|\bline\b\s*)(\d+)', line)
            line_no = int(line_match.group(1)) if line_match else 0
            
            timestamps.append(ts)
            dates.append(dt_str)
            environments.append("local")
            levels.append("ERROR")
            error_types.append(err_type)
            file_names.append(f_name)
            file_paths.append(f_path)
            line_numbers.append(line_no)
            messages.append(line)
            full_texts.append(line)

    if not timestamps:
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

    if not timestamps:
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

def analyze_exception(message: str, error_type: str = "", file_name: str = "", full_text: str = "") -> dict:
    """Matches the message against known paradigms based on stack and technology."""
    text_to_scan = f"{message} {error_type} {file_name} {full_text}".lower()
    
    # 1. Tech detection
    tech = "generic"
    file_lower = file_name.lower()
    
    if file_lower.endswith(".py") or ".py:" in text_to_scan or "traceback (most recent call last):" in text_to_scan or "pip install" in text_to_scan:
        tech = "python"
    elif file_lower.endswith(".cs") or file_lower.endswith(".csproj") or file_lower.endswith(".sln") or ".cs:line" in text_to_scan or "system.nullreferenceexception" in text_to_scan or "dotnet build" in text_to_scan or "microsoft.aspnetcore" in text_to_scan:
        tech = "dotnet"
    elif file_lower.endswith(".java") or file_lower.endswith(".jar") or file_lower.endswith(".class") or "nullpointerexception" in text_to_scan or "noclassdeffounderror" in text_to_scan or "classpath" in text_to_scan:
        tech = "java"
    elif file_lower.endswith(".go") or "go.mod" in text_to_scan or "panic: runtime error" in text_to_scan or "goroutine " in text_to_scan:
        tech = "go"
    elif file_lower.endswith(".html") or file_lower.endswith(".htm") or "<html>" in text_to_scan or "doctype html" in text_to_scan or "domexception" in text_to_scan or "cors policy" in text_to_scan:
        tech = "html"
    elif file_lower.endswith(".js") or file_lower.endswith(".ts") or file_lower.endswith(".jsx") or file_lower.endswith(".tsx") or "node_modules" in text_to_scan or "package.json" in text_to_scan or "npm " in text_to_scan or "at object." in text_to_scan:
        tech = "nodejs"
    elif any(k in text_to_scan for k in ["laravel", "artisan", "eloquent"]):
        tech = "laravel"
    elif file_lower.endswith(".php") or "php fatal error" in text_to_scan or "php warning" in text_to_scan or "composer.json" in text_to_scan:
        tech = "php"
    else:
        if "python" in text_to_scan or "django" in text_to_scan or "flask" in text_to_scan:
            tech = "python"
        elif "dotnet" in text_to_scan or "csharp" in text_to_scan:
            tech = "dotnet"
        elif "nodejs" in text_to_scan or "javascript" in text_to_scan or "typescript" in text_to_scan:
            tech = "nodejs"
        elif "java" in text_to_scan or "springboot" in text_to_scan or "spring boot" in text_to_scan:
            tech = "java"
        elif "golang" in text_to_scan or "go build" in text_to_scan:
            tech = "go"
        elif "composer" in text_to_scan or "symfony" in text_to_scan:
            tech = "php"
        elif "html" in text_to_scan or "css" in text_to_scan or "stylesheet" in text_to_scan:
            tech = "html"

    # 2. Technology-specific diagnostic matching
    if tech == "python":
        if "modulenotfounderror" in text_to_scan or "importerror" in text_to_scan or "no module named" in text_to_scan:
            mod_match = re.search(r"no module named ['\"]?([a-zA-Z0-9_\-]+)['\"]?", text_to_scan)
            mod_name = mod_match.group(1) if mod_match else "<package_name>"
            return {
                "name": f"Python Dependency Missing: '{mod_name}'",
                "explanation": f"The Python interpreter could not locate the module '{mod_name}' in the current environment.",
                "remediation": f"""# Install missing package via pip
pip install {mod_name}
# Or if using poetry / uv
poetry add {mod_name} # Poetry
uv add {mod_name}     # uv"""
            }
        elif "filenotfounderror" in text_to_scan or "ioerror" in text_to_scan or "no such file or directory" in text_to_scan:
            return {
                "name": "Python File Access / FileNotFoundError",
                "explanation": "The script attempted to open or manipulate a file that does not exist at the specified target path.",
                "remediation": f"""# Verify path existence in Python CLI
python -c "import os; print(os.path.exists('path/to/file'))"
# Check file read permissions
ls -la {file_name if file_name != "Unknown File" else ""}"""
            }
        elif any(k in text_to_scan for k in ["connectionrefusederror", "operationalerror", "postgresql", "mysql", "sqlite3"]):
            return {
                "name": "Python Database Connection Refused",
                "explanation": "Python failed to establish a network connection to your database server. DB port is offline or credentials mismatch.",
                "remediation": """# Check local database service status
sudo systemctl status postgresql # PostgreSQL
# Validate environment configurations (e.g. settings.py or .env)
# For Django, perform outstanding migrations:
python manage.py migrate"""
            }
        elif "syntaxerror" in text_to_scan or "indentationerror" in text_to_scan:
            return {
                "name": "Python Syntax / Indentation Compilation Error",
                "explanation": "The Python interpreter failed to parse the module due to improper indentation, syntax typos, or mismatched brackets.",
                "remediation": f"""# Check module syntax structure
python -m py_compile {file_name if file_name != "Unknown File" else "script.py"}"""
            }
        else:
            return {
                "name": f"Python {error_type if error_type else 'Runtime'} Exception",
                "explanation": "A Python runtime error occurred. Review the exception trace details below.",
                "remediation": f"""# Debug using Python Interactive PDB
python -m pdb {file_name if file_name != "Unknown File" else "script.py"}
# Check style lint rules
ruff check ."""
            }

    elif tech == "nodejs":
        if "cannot find module" in text_to_scan or "module_not_found" in text_to_scan:
            mod_match = re.search(r"cannot find module ['\"]?([a-zA-Z0-9_\-/]+)['\"]?", text_to_scan)
            mod_name = mod_match.group(1) if mod_match else "<package_name>"
            return {
                "name": f"Node.js Package Missing: '{mod_name}'",
                "explanation": f"Node.js could not resolve the required module '{mod_name}'. The package is missing in node_modules.",
                "remediation": f"""# Install package via npm/yarn/pnpm
npm install {mod_name}
# Or clean install dependencies from package-lock.json
npm ci"""
            }
        elif "econnrefused" in text_to_scan or "mongodb" in text_to_scan or "mongoose" in text_to_scan or "redis" in text_to_scan:
            return {
                "name": "Node.js Network Socket / Connection Refused",
                "explanation": "The Node.js runtime failed to connect to the SQL, MongoDB, Redis, or external HTTP server API.",
                "remediation": """# Check if DB or target service is running locally
sudo systemctl status mongod  # MongoDB
sudo systemctl status redis   # Redis
# Check environment variables in your active directory
cat .env"""
            }
        elif "typeerror" in text_to_scan or "referenceerror" in text_to_scan or "cannot read properties" in text_to_scan:
            return {
                "name": "Node.js TypeError / Reference Variable Exception",
                "explanation": "Accessing properties on an undefined or null variable, or calling an undefined object method.",
                "remediation": """# Run TypeScript or ESLint compiler static checks
npx eslint . --ext .js,.ts
# Or run with Node debug inspector enabled:
node --inspect-brk index.js"""
            }
        else:
            return {
                "name": f"NodeJS {error_type if error_type else 'Runtime'} Error",
                "explanation": "An unhandled JavaScript runtime error occurred.",
                "remediation": """# Run clean build check
npm run build
# Check dependencies health
npm audit"""
            }

    elif tech == "dotnet":
        if "nullreferenceexception" in text_to_scan:
            return {
                "name": ".NET C# NullReferenceException",
                "explanation": "A reference variable in C# was dereferenced while pointing to null.",
                "remediation": f"""# Build in Debug mode to locate local symbols
dotnet build --configuration Debug
# Use C# null-coalescing or null-conditional checks:
# var name = obj?.Name ?? "Default";"""
            }
        elif "sqlexception" in text_to_scan or "dbupdateexception" in text_to_scan:
            return {
                "name": ".NET Entity Framework Database Exception",
                "explanation": "A database query or schema modification transaction failed due to connection drops or constraints.",
                "remediation": """# Update DB to latest migration schema
dotnet ef database update
# Validate connection strings in appsettings.json
cat appsettings.json | grep -i ConnectionStrings"""
            }
        elif "filenotfoundexception" in text_to_scan or "directorynotfoundexception" in text_to_scan:
            return {
                "name": ".NET File System Resolution Failure",
                "explanation": "The target assembly file or directory could not be located at runtime.",
                "remediation": """# Restore NuGet dependencies packages
dotnet restore
# Clean compilation folder and build
dotnet clean && dotnet build"""
            }
        else:
            return {
                "name": f".NET C# {error_type if error_type else 'Runtime'} Exception",
                "explanation": "A .NET CLI or Web Host runtime exception was thrown.",
                "remediation": """# Rebuild project
dotnet build
# Run unit tests to verify system state
dotnet test"""
            }

    elif tech == "java":
        if "nullpointerexception" in text_to_scan:
            return {
                "name": "Java NullPointerException (NPE)",
                "explanation": "Code attempted to access variables or run methods on a null object instance.",
                "remediation": """# Ensure you compile with full debug symbols:
javac -g YourClass.java
# Implement Defensive Guard checks or use java.util.Optional wrapper."""
            }
        elif "classnotfoundexception" in text_to_scan or "noclassdeffounderror" in text_to_scan:
            return {
                "name": "Java JVM Classpath Definition Failure",
                "explanation": "The JVM classloader could not locate the compiled class binary on the system classpath.",
                "remediation": """# Rebuild project dependencies and refresh cache
mvn clean install   # Maven
./gradlew build --refresh-dependencies # Gradle"""
            }
        elif "sqlexception" in text_to_scan:
            return {
                "name": "Java JDBC Database Exception",
                "explanation": "A SQL database execution transaction or connection failed via JDBC driver.",
                "remediation": """# Check JDBC driver jar is on classpath
# Verify DB URL port bindings and firewall rules"""
            }
        else:
            return {
                "name": f"Java {error_type if error_type else 'JVM'} Exception",
                "explanation": "A JVM compiler or thread execution runtime exception occurred.",
                "remediation": """# Package project package structure
mvn package
# Run Java application debugger profile"""
            }

    elif tech == "go":
        if "nil pointer dereference" in text_to_scan or "invalid memory address" in text_to_scan:
            return {
                "name": "Go (Golang) Nil Pointer Dereference",
                "explanation": "The program panicked because it attempted to access a field or method on a nil pointer reference.",
                "remediation": """# Build application binary with debug symbols enabled
go build -gcflags="all=-N -l" -o app
# Run with Go Delve debugger tool:
dlv debug"""
            }
        elif "database is closed" in text_to_scan or "bad connection" in text_to_scan:
            return {
                "name": "Go Database Driver Connection Drop",
                "explanation": "An operation was attempted on a closed database connection or connection pool.",
                "remediation": """# Check db.Ping() errors in your connection initiator
# Verify import of SQL driver driver:
# import _ "github.com/go-sql-driver/mysql\""""
            }
        else:
            return {
                "name": f"Go {error_type if error_type else 'Runtime'} Panic",
                "explanation": "Go runtime panic thrown. Review stdout traceback details.",
                "remediation": """# Check project imports and tidy modules dependencies
go mod tidy
# Run tests to pinpoint panic code segment
go test ./..."""
            }

    elif tech == "php":
        if "parse error" in text_to_scan or "syntax error" in text_to_scan:
            return {
                "name": "PHP Parser Syntax Error",
                "explanation": "The PHP compiler failed to parse the file due to syntax issues (missing semicolons, mismatched brackets).",
                "remediation": f"""# Check PHP script syntax errors via linter
php -l {file_name if file_name != "Unknown File" else "your_file.php"}"""
            }
        elif "call to undefined function" in text_to_scan or "call to undefined method" in text_to_scan:
            return {
                "name": "PHP Undefined Reference Call",
                "explanation": "Calling a method or function that has not been defined in scope or resolved by Composer.",
                "remediation": """# Refresh Composer classmaps autoloader
composer dump-autoload
# Verify that the class is imported with 'use Namespace\\Class;'"""
            }
        elif "permission denied" in text_to_scan or "failed to open stream" in text_to_scan:
            return {
                "name": "PHP File Permissions Denied",
                "explanation": "The PHP process (apache or php-fpm) doesn't have sufficient read/write rights for the directory.",
                "remediation": """# Grant write access to web-server group
sudo chmod -R 775 storage
sudo chown -R www-data:www-data storage"""
            }
        else:
            return {
                "name": f"PHP {error_type if error_type else 'Runtime'} Error",
                "explanation": "A PHP runtime exception occurred.",
                "remediation": """# Check composer package packages versions
composer install
# Check apache / php-fpm system error log file
tail -n 50 /var/log/apache2/error.log"""
            }

    elif tech == "html":
        if "cors" in text_to_scan or "access-control-allow-origin" in text_to_scan:
            return {
                "name": "Frontend CORS Policy Blocked Access",
                "explanation": "The web browser blocked a cross-origin HTTP request because the target server failed to return the correct 'Access-Control-Allow-Origin' header.",
                "remediation": """# If configuring nginx proxy server, add header:
# add_header 'Access-Control-Allow-Origin' '*';
# Or verify your local backend server's CORS middleware configuration."""
            }
        elif "404" in text_to_scan or "not found" in text_to_scan or "failed to load resource" in text_to_scan:
            return {
                "name": "Frontend Asset Loading Failure (404)",
                "explanation": "The browser failed to retrieve a referenced asset (e.g. stylesheet, script, image, or font) because the file path is incorrect.",
                "remediation": f"""# Verify the asset file path exists in your public build folder:
# Check reference in: {file_name if file_name != "Unknown File" else "index.html"}
# Ensure absolute paths or build pipelines (Vite/Webpack) match the deployed directory."""
            }
        elif "domexception" in text_to_scan or "queryselector" in text_to_scan or "addeventlistener" in text_to_scan:
            return {
                "name": "HTML DOM Reference Reference Error",
                "explanation": "A client-side script attempted to query or attach listener rules to an element that is missing or not yet loaded in the DOM tree.",
                "remediation": """# Wrap script invocation inside DOMContentLoaded:
# document.addEventListener('DOMContentLoaded', () => { ... });
# Or ensure element checks are guarded: if (elem) { elem.addEventListener(...) }"""
            }
        else:
            return {
                "name": "HTML/CSS/JS Frontend Diagnostics Error",
                "explanation": "A general frontend layout, rendering, or client-side script execution exception occurred.",
                "remediation": """# Audit HTML markup validation rules
npx html-validator-cli --file=index.html
# Check script syntax errors via ESLint linter
npx eslint src/"""
            }

    else:  # laravel / fallback
        for p in PARADIGMS:
            if any(kw in text_to_scan for kw in p["keywords"]):
                return p
                
        return {
            "name": "Generic Exception / Runtime Error",
            "explanation": "An unclassified exception was thrown. Review the raw traceback context in the LHS panel.",
            "remediation": """# Check local ports and server socket processes
netstat -tulpn
# Verify execution logs of system services
tail -n 50 /var/log/syslog
# Check permissions on current workspace
ls -la"""
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
            is_static_file = False
            static_rel_path = ""
            if "static/" in target_url:
                idx = target_url.find("static/")
                static_rel_path = target_url[idx:]
                is_static_file = True
            elif target_url.startswith("/static/"):
                static_rel_path = target_url.lstrip("/")
                is_static_file = True
                
            local_file_path = BASE_DIR / static_rel_path if is_static_file else None
            
            if local_file_path and local_file_path.exists():
                with st.spinner(f"Loading local static file: {local_file_path.name}..."):
                    raw_logs_content = local_file_path.read_text(encoding="utf-8")
            else:
                if not (target_url.startswith("http://") or target_url.startswith("https://") or "://" in target_url):
                    fetch_error = f"Local static log file not found at: {local_file_path if local_file_path else target_url}"
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
                diagnosis = analyze_exception(
                    message=selected_row["exception_message"],
                    error_type=selected_row["error_type"],
                    file_name=selected_row["file_name"],
                    full_text=selected_row["full_text"]
                )
                
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
