"""
Navigation utilities for Streamlit application.
"""

import streamlit as st
from typing import Dict, List


def setup_navigation() -> None:
    """Setup sidebar navigation for the application."""
    
    st.sidebar.title("📋 Navigation")
    
    # Navigation options
    nav_options = {
        "🏠 Dashboard": "dashboard",
        "🗂️ Dossier Management": "dossier_management", 
        "📊 Value Dossier Structure": "value_dossier_structure",
        "🗂️ Template Management": "template_management",
        "🔬 Evidence Tracking": "evidence_tracking",
        "💰 Economics View": "economics_view"
    }
    
    # Current page selection
    current_page = st.session_state.get("current_page", "dossier_management")
    
    # Create navigation buttons
    for label, page_key in nav_options.items():
        if st.sidebar.button(
            label, 
            key=f"nav_{page_key}",
            use_container_width=True,
            type="primary" if current_page == page_key else "secondary"
        ):
            st.session_state.current_page = page_key
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Statistics section
    render_statistics()
    
    st.sidebar.markdown("---")
    
    # Quick actions
    render_quick_actions()


def render_statistics() -> None:
    """Render statistics in sidebar."""
    
    st.sidebar.subheader("📈 Statistics")
    
    # Get counts from session state
    dossier_count = len(st.session_state.get("dossiers", {}))
    evidence_count = len(st.session_state.get("evidence_entries", {}))
    economics_count = len(st.session_state.get("economics_data", {}))
    
    # Display stats
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        st.metric("Dossiers", dossier_count)
        st.metric("Evidence", evidence_count)
    
    with col2:
        st.metric("Economics", economics_count)
        st.metric("Total", dossier_count + evidence_count + economics_count)


def render_quick_actions() -> None:
    """Render quick action buttons in sidebar."""
    
    st.sidebar.subheader("⚡ Quick Actions")
    
    # Export all data
    if st.sidebar.button("📤 Export All Data", use_container_width=True):
        export_all_data()
    
    # Import data
    if st.sidebar.button("📥 Import Data", use_container_width=True):
        show_import_dialog()
    
    # Clear all data (with confirmation)
    if st.sidebar.button("🗑️ Clear All Data", use_container_width=True):
        show_clear_data_confirmation()


def export_all_data() -> None:
    """Export all data from session state."""
    
    import json
    from datetime import datetime
    
    # Collect all data
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "dossiers": st.session_state.get("dossiers", {}),
        "evidence_entries": st.session_state.get("evidence_entries", {}), 
        "economics_data": st.session_state.get("economics_data", {}),
        "metadata": {
            "version": "0.1",
            "source": "medai_dossier_streamlit_mvp"
        }
    }
    
    # Convert to JSON
    json_data = json.dumps(export_data, indent=2, default=str)
    
    # Create download
    st.sidebar.download_button(
        label="💾 Download JSON",
        data=json_data,
        file_name=f"medai_dossier_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )
    
    st.sidebar.success("✅ Export ready for download!")


def show_import_dialog() -> None:
    """Show import dialog."""
    st.sidebar.info("📥 Import functionality will be added in future version.")


def show_clear_data_confirmation() -> None:
    """Show confirmation dialog for clearing all data."""
    
    if "confirm_clear" not in st.session_state:
        st.session_state.confirm_clear = False
    
    if not st.session_state.confirm_clear:
        st.sidebar.warning("⚠️ This will delete all data!")
        if st.sidebar.button("⚠️ I understand, clear all data", use_container_width=True):
            st.session_state.confirm_clear = True
            st.rerun()
    else:
        st.sidebar.error("🚨 Final confirmation required!")
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("✅ Yes, Clear", use_container_width=True):
                clear_all_data()
                st.session_state.confirm_clear = False
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.confirm_clear = False
                st.rerun()


def clear_all_data() -> None:
    """Clear all data from session state."""
    
    st.session_state.dossiers = {}
    st.session_state.evidence_entries = {}
    st.session_state.economics_data = {}
    st.session_state.form_data = {}
    st.session_state.editing_dossier = None
    
    st.sidebar.success("✅ All data cleared!")


def navigate_to_page(page: str) -> None:
    """Navigate to a specific page.
    
    Args:
        page: Page identifier to navigate to
    """
    st.session_state.current_page = page
    st.rerun()
