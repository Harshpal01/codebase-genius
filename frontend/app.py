import streamlit as st
import requests
import json
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Codebase Genius",
    page_icon="📚",
    layout="wide",
)

# --- CSS STYLING ---
st.markdown("""
    <style>
        /* Main container */
        .main > div {
            max-width: 1400px;
            padding: 20px 40px;
        }
        
        /* Streamlit default styling improvements */
        .stApp {
            background-color: #f5f7fa;
        }
        
        .main {
            background-color: #ffffff;
            border-radius: 0px;
            margin: 0px;
            box-shadow: none;
        }
        
        /* Buttons */
        .stButton>button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        /* Input fields */
        .stTextInput>div>div>input {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            padding: 12px;
            font-size: 15px;
            transition: border 0.3s ease;
        }
        
        .stTextInput>div>div>input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Success box */
        .success-box {
            padding: 24px;
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-left: 5px solid #28a745;
            border-radius: 12px;
            margin: 20px 0;
            color: #155724;
            font-weight: 500;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.15);
        }
        
        .success-box h3 {
            color: #155724;
            margin-top: 0;
            font-size: 22px;
        }
        
        /* Error box */
        .error-box {
            padding: 24px;
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border-left: 5px solid #dc3545;
            border-radius: 12px;
            margin: 20px 0;
            color: #721c24;
            font-weight: 500;
            box-shadow: 0 4px 15px rgba(220, 53, 69, 0.15);
        }
        
        /* Info box */
        .info-box {
            padding: 24px;
            background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
            border-left: 5px solid #17a2b8;
            border-radius: 12px;
            margin: 20px 0;
            color: #0c5460;
            font-weight: 500;
            box-shadow: 0 4px 15px rgba(23, 162, 184, 0.15);
        }
        
        /* Repository card */
        .repo-card {
            padding: 20px;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border: 2px solid #e9ecef;
            border-radius: 12px;
            margin: 15px 0;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .repo-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            border-color: #667eea;
        }
        
        /* Status badges */
        .status-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        
        .status-completed {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
        }
        
        .status-processing {
            background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
            color: #000;
        }
        
        .status-error {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #ffffff;
            padding: 15px;
            border-radius: 12px;
            border: 2px solid #e2e8f0;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 14px 28px;
            font-weight: 600;
            font-size: 15px;
            transition: all 0.3s ease;
            background-color: #f7fafc;
            color: #4a5568;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #edf2f7;
            color: #2d3748;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        /* Headers */
        h1 {
            color: #1a202c;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        h2 {
            color: #2d3748;
            font-weight: 700;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 32px;
        }
        
        h3 {
            color: #4a5568;
            font-weight: 600;
        }
        
        /* Tab content headers */
        .main h2:first-of-type {
            color: #1a202c;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            color: white;
        }
        
        /* Download button */
        .stDownloadButton>button {
            background: linear-gradient(135deg, #20c997 0%, #17a2b8 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stDownloadButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(32, 201, 151, 0.4);
        }
        
        /* Markdown text */
        .stMarkdown {
            color: #2d3748;
            line-height: 1.7;
            font-size: 15px;
        }
        
        .stMarkdown p {
            color: #4a5568;
            font-weight: 400;
        }
        
        /* Code blocks */
        code {
            background-color: #f7fafc;
            padding: 2px 6px;
            border-radius: 4px;
            color: #667eea;
            font-weight: 500;
        }
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTS ---
BASE_URL = "http://localhost:8000"
CODE_GENIUS_ENDPOINT = f"{BASE_URL}/walker/generate_docs"
GET_DOCUMENTATION_ENDPOINT = f"{BASE_URL}/walker/get_documentation"
LIST_REPOSITORIES_ENDPOINT = f"{BASE_URL}/walker/list_repositories"

# --- SESSION STATE INIT ---
if 'generated_docs' not in st.session_state:
    st.session_state.generated_docs = []
if 'current_repo' not in st.session_state:
    st.session_state.current_repo = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='color: white; font-size: 28px; margin-bottom: 5px;'>📚 Codebase Genius</h1>
            <p style='color: rgba(255,255,255,0.8); font-size: 14px;'>Automated Documentation</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <h3 style='color: white; font-size: 16px; margin-bottom: 10px;'>✨ About</h3>
            <p style='color: rgba(255,255,255,0.9); font-size: 13px; line-height: 1.6;'>
                A powerful multi-agent system that automatically generates comprehensive 
                documentation for any software repository.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <h3 style='color: white; font-size: 16px; margin-bottom: 10px;'>🚀 Features</h3>
            <ul style='color: rgba(255,255,255,0.9); font-size: 13px; line-height: 1.8; list-style: none; padding-left: 0;'>
                <li>🔍 Repository analysis</li>
                <li>📊 Code context graphs</li>
                <li>📝 Auto-generated docs</li>
                <li>🎨 Architecture diagrams</li>
                <li>🐍 Python & Jac support</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
        <div style='text-align: center; padding: 10px; color: rgba(255,255,255,0.6); font-size: 12px;'>
            Made with ❤️ using JacLang
        </div>
    """, unsafe_allow_html=True)

# --- MAIN TITLE ---
st.markdown("""
    <div style='text-align: center; padding: 40px 0 30px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                margin: -20px -40px 30px -40px; border-radius: 0 0 20px 20px;'>
        <h1 style='font-size: 48px; font-weight: 700; color: white; margin-bottom: 10px;'>
            📚 Codebase Genius
        </h1>
        <p style='font-size: 18px; color: rgba(255,255,255,0.9); font-weight: 500;'>
            Automated Documentation Generation for Software Repositories
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🚀 Generate Documentation", "📖 View Documentation", "📂 Repository History"])

# ========================
#   GENERATE DOCUMENTATION
# ========================
with tab1:
    st.markdown("<h2 style='color: #1a202c; font-weight: 700; font-size: 32px; margin-bottom: 10px;'>Generate Documentation</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #4a5568; font-size: 16px; margin-bottom: 20px;'>Enter a GitHub repository URL to generate comprehensive documentation.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        github_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/username/repository",
            help="Enter the full GitHub repository URL"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_button = st.button("🎯 Generate Docs", type="primary")
    
    if generate_button:
        if not github_url:
            st.error("⚠️ Please enter a GitHub repository URL")
        elif not github_url.startswith("https://github.com/"):
            st.error("⚠️ Please enter a valid GitHub URL (must start with https://github.com/)")
        else:
            with st.spinner("🔄 Processing repository... This may take a few minutes."):
                try:
                    # Call the code_genius walker
                    payload = {"github_url": github_url}
                    response = requests.post(CODE_GENIUS_ENDPOINT, json=payload, timeout=600)
                    
                    if response.status_code == 200:
                        data = response.json()
                        reports = data.get("reports", [])
                        
                        if reports and reports[0].get("status") == "completed":
                            result = reports[0]
                            st.session_state.current_repo = result.get("repository")
                            
                            st.markdown(f"""
                            <div class="success-box">
                                <h3>✅ Documentation Generated Successfully!</h3>
                                <p><strong>Repository:</strong> {result.get('repository')}</p>
                                <p><strong>Documentation Path:</strong> {result.get('documentation_path')}</p>
                                <p><strong>Message:</strong> {result.get('message')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.balloons()
                            
                            # Add to history
                            st.session_state.generated_docs.append({
                                "repo": result.get("repository"),
                                "url": github_url,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "status": "completed"
                            })
                        else:
                            error_msg = reports[0].get("message", "Unknown error") if reports else "No response"
                            st.markdown(f"""
                            <div class="error-box">
                                <h3>❌ Error</h3>
                                <p>{error_msg}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Server error: {response.status_code}")
                        st.code(response.text)
                        
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. The repository might be too large or the server is busy.")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Cannot connect to the backend server. Please ensure it's running on http://localhost:8000")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
    
    # Example repositories
    st.markdown("---")
    st.markdown("### 💡 Try These Example Repositories")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📦 Flask (Small)"):
            st.session_state.example_url = "https://github.com/pallets/flask"
            st.rerun()
    
    with col2:
        if st.button("🔧 Requests (Medium)"):
            st.session_state.example_url = "https://github.com/psf/requests"
            st.rerun()
    
    with col3:
        if st.button("🎯 FastAPI (Medium)"):
            st.session_state.example_url = "https://github.com/tiangolo/fastapi"
            st.rerun()
    
    if 'example_url' in st.session_state:
        st.info(f"📋 Example URL copied: {st.session_state.example_url}")
        del st.session_state.example_url

# ========================
#   VIEW DOCUMENTATION
# ========================
with tab2:
    st.markdown("<h2 style='color: #1a202c; font-weight: 700; font-size: 32px; margin-bottom: 20px;'>View Generated Documentation</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        repo_name = st.text_input(
            "Repository Name",
            value=st.session_state.current_repo or "",
            placeholder="Enter repository name",
            help="Enter the name of the repository to view its documentation"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        view_button = st.button("👁️ View Docs")
    
    if view_button and repo_name:
        with st.spinner("📖 Loading documentation..."):
            try:
                payload = {"repo_name": repo_name}
                response = requests.post(GET_DOCUMENTATION_ENDPOINT, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    reports = data.get("reports", [])
                    
                    if reports and reports[0].get("status") == "success":
                        content = reports[0].get("content", "")
                        
                        st.markdown("---")
                        st.markdown(content, unsafe_allow_html=True)
                        
                        # Download button
                        st.download_button(
                            label="⬇️ Download Documentation",
                            data=content,
                            file_name=f"{repo_name}_docs.md",
                            mime="text/markdown"
                        )
                    else:
                        st.warning(f"📭 No documentation found for '{repo_name}'")
                else:
                    st.error(f"❌ Server error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to the backend server. Please ensure it's running.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

# ========================
#   REPOSITORY HISTORY
# ========================
with tab3:
    st.markdown("<h2 style='color: #1a202c; font-weight: 700; font-size: 32px; margin-bottom: 20px;'>Repository History</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        refresh = st.button("🔄 Refresh List")
    
    if refresh or st.session_state.get("_load_repos_once", True):
        with st.spinner("Loading repositories..."):
            try:
                response = requests.post(LIST_REPOSITORIES_ENDPOINT)
                
                if response.status_code == 200:
                    data = response.json()
                    reports = data.get("reports", [])
                    
                    if reports and isinstance(reports[0], list):
                        repos = reports[0]
                        
                        if repos:
                            st.success(f"Found {len(repos)} repositories")
                            
                            for repo in repos:
                                status_class = f"status-{repo.get('status', 'processing')}"
                                
                                st.markdown(f"""
                                <div class="repo-card">
                                    <h4>{repo.get('name', 'Unknown')}</h4>
                                    <p><strong>URL:</strong> {repo.get('url', 'N/A')}</p>
                                    <p><span class="status-badge {status_class}">{repo.get('status', 'Unknown').upper()}</span></p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("📭 No repositories found. Generate documentation to get started!")
                    else:
                        st.info("📭 No repositories found.")
                else:
                    st.error(f"❌ Server error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to the backend server. Please ensure it's running.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
        
        st.session_state._load_repos_once = False

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>Built with ❤️ using JacLang, byLLM, and Streamlit</p>
    <p>Codebase Genius - Automated Documentation Generation System</p>
</div>
""", unsafe_allow_html=True)
