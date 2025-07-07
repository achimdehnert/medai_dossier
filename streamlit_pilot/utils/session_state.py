"""
Session state management for Streamlit application.
"""

import streamlit as st
from typing import Dict, Any
from datetime import datetime


def initialize_session_state() -> None:
    """Initialize Streamlit session state with default values."""
    
    # Navigation state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dossier_management"
    
    # Data storage (using session state as simple persistence for MVP)
    if "dossiers" not in st.session_state:
        st.session_state.dossiers = {}
    
    if "evidence_entries" not in st.session_state:
        st.session_state.evidence_entries = {}
    
    if "economics_data" not in st.session_state:
        st.session_state.economics_data = {}
    
    # Form states
    if "editing_dossier" not in st.session_state:
        st.session_state.editing_dossier = None
    
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}
    
    # UI states
    if "show_success_message" not in st.session_state:
        st.session_state.show_success_message = False
    
    if "success_message" not in st.session_state:
        st.session_state.success_message = ""


def get_session_data(key: str, default: Any = None) -> Any:
    """Get data from session state.
    
    Args:
        key: Session state key
        default: Default value if key not found
        
    Returns:
        Session state value or default
    """
    return st.session_state.get(key, default)


def set_session_data(key: str, value: Any) -> None:
    """Set data in session state.
    
    Args:
        key: Session state key
        value: Value to set
    """
    st.session_state[key] = value


def clear_form_data() -> None:
    """Clear form data from session state."""
    st.session_state.form_data = {}


def show_success_message(message: str) -> None:
    """Show success message in next render.
    
    Args:
        message: Success message to display
    """
    st.session_state.show_success_message = True
    st.session_state.success_message = message


def clear_success_message() -> None:
    """Clear success message."""
    st.session_state.show_success_message = False
    st.session_state.success_message = ""
