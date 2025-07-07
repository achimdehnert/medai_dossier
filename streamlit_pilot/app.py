"""
Streamlit MVP Application for Medical AI Dossier Management System.

This is the main entry point for the Streamlit pilot implementation.
Provides a simple, intuitive interface for managing Value Dossiers.
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from components import dossier_management, evidence_tracking, economics_view
from utils.session_state import initialize_session_state
from utils.navigation import setup_navigation


def main() -> None:
    """Main Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title="Medical AI Dossier Manager",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/achimdehnert/medai_dossier',
            'Report a bug': 'https://github.com/achimdehnert/medai_dossier/issues',
            'About': "Medical AI Dossier Management System - Streamlit MVP v0.1"
        }
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Setup navigation
    setup_navigation()
    
    # Main content area
    st.title("🏥 Medical AI Dossier Manager")
    st.markdown("---")
    
    # Navigation based on selected page
    page = st.session_state.get("current_page", "dossier_management")
    
    if page == "dossier_management":
        dossier_management.render()
    elif page == "evidence_tracking":
        evidence_tracking.render()
    elif page == "economics_view":
        economics_view.render()
    else:
        st.error(f"Unknown page: {page}")


if __name__ == "__main__":
    main()
