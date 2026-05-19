"""
Streamlit entry point — run from project root:

    streamlit run streamlit_app.py
"""

from site_path import ensure_project_root

ensure_project_root()

from app.streamlit_ui import main

main()
