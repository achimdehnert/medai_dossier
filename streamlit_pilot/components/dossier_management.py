"""
Dossier Management page for Streamlit MVP.

Handles creation, editing, listing, and management of Value Dossiers.
"""

import streamlit as st
import uuid
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from utils.session_state import (
    get_session_data, 
    set_session_data, 
    show_success_message,
    clear_success_message
)


def render() -> None:
    """Render the dossier management page."""
    
    st.header("🗂️ Dossier Management")
    
    # Show success message if any
    if st.session_state.get("show_success_message"):
        st.success(st.session_state.get("success_message", ""))
        clear_success_message()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📋 All Dossiers", "➕ Create New", "📊 Analytics"])
    
    with tab1:
        render_dossier_list()
    
    with tab2:
        render_create_dossier()
    
    with tab3:
        render_dossier_analytics()


def render_dossier_list() -> None:
    """Render the list of all dossiers."""
    
    dossiers = get_session_data("dossiers", {})
    
    if not dossiers:
        st.info("📭 No dossiers created yet. Use the 'Create New' tab to get started!")
        return
    
    st.subheader(f"📋 All Dossiers ({len(dossiers)})")
    
    # Search and filter
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search dossiers", placeholder="Enter title or indication...")
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Draft", "In Review", "Approved", "Submitted"])
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Created Date", "Title", "Status", "Indication"])
    
    # Filter and sort dossiers
    filtered_dossiers = filter_and_sort_dossiers(dossiers, search_term, status_filter, sort_by)
    
    # Display dossiers
    for dossier_id, dossier in filtered_dossiers.items():
        render_dossier_card(dossier_id, dossier)


def render_dossier_card(dossier_id: str, dossier: Dict[str, Any]) -> None:
    """Render a single dossier card.
    
    Args:
        dossier_id: Unique dossier identifier
        dossier: Dossier data dictionary
    """
    
    with st.container():
        st.markdown("---")
        
        # Header row
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.subheader(f"📄 {dossier.get('title', 'Untitled')}")
            st.caption(f"ID: {dossier_id}")
        
        with col2:
            status = dossier.get('status', 'Draft')
            status_color = get_status_color(status)
            st.markdown(f"**Status:** :{status_color}[{status}]")
        
        with col3:
            indication = dossier.get('indication', 'Not specified')
            st.markdown(f"**Indication:** {indication}")
        
        with col4:
            created_date = dossier.get('created_date', 'Unknown')
            if isinstance(created_date, str):
                try:
                    created_date = datetime.fromisoformat(created_date).strftime('%Y-%m-%d')
                except:
                    pass
            st.markdown(f"**Created:** {created_date}")
        
        # Details row
        col1, col2 = st.columns([2, 1])
        
        with col1:
            description = dossier.get('description', 'No description provided')
            st.markdown(f"**Description:** {description}")
            
            # Progress indicators
            evidence_count = len(dossier.get('evidence_items', []))
            economics_data = dossier.get('economics_data', {})
            has_economics = bool(economics_data.get('budget_impact') or economics_data.get('cost_effectiveness'))
            
            progress_col1, progress_col2, progress_col3 = st.columns(3)
            with progress_col1:
                st.metric("Evidence Items", evidence_count)
            with progress_col2:
                st.metric("Economics", "✅" if has_economics else "❌")
            with progress_col3:
                completion = calculate_completion_percentage(dossier)
                st.metric("Completion", f"{completion}%")
        
        with col2:
            # Action buttons
            st.write("**Actions:**")
            
            if st.button(f"✏️ Edit", key=f"edit_{dossier_id}", use_container_width=True):
                st.session_state.editing_dossier = dossier_id
                st.session_state.current_page = "dossier_edit"
                st.rerun()
            
            if st.button(f"👀 View Details", key=f"view_{dossier_id}", use_container_width=True):
                show_dossier_details(dossier_id, dossier)
            
            if st.button(f"📊 Analytics", key=f"analytics_{dossier_id}", use_container_width=True):
                show_dossier_analytics(dossier_id, dossier)
            
            if st.button(f"🗑️ Delete", key=f"delete_{dossier_id}", use_container_width=True, type="secondary"):
                confirm_delete_dossier(dossier_id)


def render_create_dossier() -> None:
    """Render the create new dossier form."""
    
    st.subheader("➕ Create New Dossier")
    
    with st.form("create_dossier_form"):
        # Basic information
        st.markdown("### 📝 Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Dossier Title *", placeholder="e.g., Alzheimer's Disease Treatment Dossier")
            indication = st.text_input("Medical Indication *", placeholder="e.g., Alzheimer's Disease")
            therapeutic_area = st.selectbox(
                "Therapeutic Area",
                ["Oncology", "Neurology", "Cardiology", "Infectious Disease", "Rare Disease", "Other"]
            )
        
        with col2:
            status = st.selectbox("Initial Status", ["Draft", "In Review", "Approved"])
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            target_submission_date = st.date_input("Target Submission Date", value=None)
        
        # Description
        description = st.text_area(
            "Description", 
            placeholder="Provide a detailed description of this dossier...",
            height=100
        )
        
        # Stakeholders
        st.markdown("### 👥 Stakeholders")
        
        col1, col2 = st.columns(2)
        
        with col1:
            primary_author = st.text_input("Primary Author", placeholder="Full Name")
            medical_writer = st.text_input("Medical Writer", placeholder="Full Name")
        
        with col2:
            regulatory_contact = st.text_input("Regulatory Contact", placeholder="Full Name")
            project_manager = st.text_input("Project Manager", placeholder="Full Name")
        
        # Form submission
        submitted = st.form_submit_button("🚀 Create Dossier", use_container_width=True)
        
        if submitted:
            if not title or not indication:
                st.error("❌ Please provide both title and indication.")
            else:
                create_new_dossier({
                    "title": title,
                    "indication": indication,
                    "therapeutic_area": therapeutic_area,
                    "status": status,
                    "priority": priority,
                    "target_submission_date": target_submission_date.isoformat() if target_submission_date else None,
                    "description": description,
                    "primary_author": primary_author,
                    "medical_writer": medical_writer,
                    "regulatory_contact": regulatory_contact,
                    "project_manager": project_manager
                })


def render_dossier_analytics() -> None:
    """Render dossier analytics and summary statistics."""
    
    dossiers = get_session_data("dossiers", {})
    
    if not dossiers:
        st.info("📊 No data to analyze yet. Create some dossiers first!")
        return
    
    st.subheader("📊 Dossier Analytics")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Dossiers", len(dossiers))
    
    with col2:
        draft_count = sum(1 for d in dossiers.values() if d.get('status') == 'Draft')
        st.metric("Draft", draft_count)
    
    with col3:
        approved_count = sum(1 for d in dossiers.values() if d.get('status') == 'Approved')
        st.metric("Approved", approved_count)
    
    with col4:
        avg_completion = sum(calculate_completion_percentage(d) for d in dossiers.values()) / len(dossiers)
        st.metric("Avg Completion", f"{avg_completion:.1f}%")
    
    # Charts and detailed analytics
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        status_data = {}
        for dossier in dossiers.values():
            status = dossier.get('status', 'Draft')
            status_data[status] = status_data.get(status, 0) + 1
        
        st.subheader("Status Distribution")
        st.bar_chart(status_data)
    
    with col2:
        # Therapeutic area distribution
        area_data = {}
        for dossier in dossiers.values():
            area = dossier.get('therapeutic_area', 'Other')
            area_data[area] = area_data.get(area, 0) + 1
        
        st.subheader("Therapeutic Areas")
        st.bar_chart(area_data)


def filter_and_sort_dossiers(
    dossiers: Dict[str, Any], 
    search_term: str, 
    status_filter: str, 
    sort_by: str
) -> Dict[str, Any]:
    """Filter and sort dossiers based on criteria.
    
    Args:
        dossiers: Dictionary of dossiers
        search_term: Search term to filter by
        status_filter: Status to filter by
        sort_by: Field to sort by
        
    Returns:
        Filtered and sorted dossiers dictionary
    """
    
    filtered = {}
    
    for dossier_id, dossier in dossiers.items():
        # Apply search filter
        if search_term:
            title = dossier.get('title', '').lower()
            indication = dossier.get('indication', '').lower()
            if search_term.lower() not in title and search_term.lower() not in indication:
                continue
        
        # Apply status filter
        if status_filter != "All":
            if dossier.get('status', 'Draft') != status_filter:
                continue
        
        filtered[dossier_id] = dossier
    
    # Sort (simple implementation for MVP)
    if sort_by == "Created Date":
        # Sort by created_date (most recent first)
        filtered = dict(sorted(
            filtered.items(), 
            key=lambda x: x[1].get('created_date', ''), 
            reverse=True
        ))
    elif sort_by == "Title":
        filtered = dict(sorted(
            filtered.items(), 
            key=lambda x: x[1].get('title', '').lower()
        ))
    
    return filtered


def create_new_dossier(dossier_data: Dict[str, Any]) -> None:
    """Create a new dossier.
    
    Args:
        dossier_data: Dossier information dictionary
    """
    
    # Generate unique ID
    dossier_id = str(uuid.uuid4())
    
    # Add metadata
    dossier_data.update({
        "created_date": datetime.now().isoformat(),
        "last_modified": datetime.now().isoformat(),
        "version": "1.0.0",
        "evidence_items": [],
        "economics_data": {},
        "timeline": [],
        "documents": []
    })
    
    # Save to session state
    dossiers = get_session_data("dossiers", {})
    dossiers[dossier_id] = dossier_data
    set_session_data("dossiers", dossiers)
    
    # Show success message
    show_success_message(f"✅ Dossier '{dossier_data['title']}' created successfully!")
    
    # Switch to list view
    st.rerun()


def calculate_completion_percentage(dossier: Dict[str, Any]) -> int:
    """Calculate completion percentage for a dossier.
    
    Args:
        dossier: Dossier data dictionary
        
    Returns:
        Completion percentage (0-100)
    """
    
    total_fields = 10
    completed_fields = 0
    
    # Check required fields
    if dossier.get('title'): completed_fields += 1
    if dossier.get('indication'): completed_fields += 1
    if dossier.get('description'): completed_fields += 1
    if dossier.get('therapeutic_area'): completed_fields += 1
    if dossier.get('primary_author'): completed_fields += 1
    if dossier.get('status') != 'Draft': completed_fields += 1
    if dossier.get('evidence_items'): completed_fields += 1
    if dossier.get('economics_data'): completed_fields += 1
    if dossier.get('target_submission_date'): completed_fields += 1
    if len(dossier.get('timeline', [])) > 0: completed_fields += 1
    
    return int((completed_fields / total_fields) * 100)


def get_status_color(status: str) -> str:
    """Get color for status display.
    
    Args:
        status: Status string
        
    Returns:
        Color name for Streamlit
    """
    
    color_map = {
        "Draft": "gray",
        "In Review": "orange", 
        "Approved": "green",
        "Submitted": "blue"
    }
    
    return color_map.get(status, "gray")


def show_dossier_details(dossier_id: str, dossier: Dict[str, Any]) -> None:
    """Show detailed view of a dossier in modal/expander.
    
    Args:
        dossier_id: Dossier ID
        dossier: Dossier data
    """
    
    with st.expander(f"📄 Details: {dossier.get('title', 'Untitled')}", expanded=True):
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information:**")
            st.write(f"• **Title:** {dossier.get('title', 'N/A')}")
            st.write(f"• **Indication:** {dossier.get('indication', 'N/A')}")
            st.write(f"• **Therapeutic Area:** {dossier.get('therapeutic_area', 'N/A')}")
            st.write(f"• **Status:** {dossier.get('status', 'N/A')}")
            st.write(f"• **Priority:** {dossier.get('priority', 'N/A')}")
        
        with col2:
            st.markdown("**Team & Dates:**")
            st.write(f"• **Primary Author:** {dossier.get('primary_author', 'N/A')}")
            st.write(f"• **Medical Writer:** {dossier.get('medical_writer', 'N/A')}")
            st.write(f"• **Project Manager:** {dossier.get('project_manager', 'N/A')}")
            st.write(f"• **Target Date:** {dossier.get('target_submission_date', 'N/A')}")
        
        st.markdown("**Description:**")
        st.write(dossier.get('description', 'No description provided.'))
        
        st.markdown("**Progress:**")
        completion = calculate_completion_percentage(dossier)
        st.progress(completion / 100)
        st.write(f"Completion: {completion}%")


def show_dossier_analytics(dossier_id: str, dossier: Dict[str, Any]) -> None:
    """Show analytics for a specific dossier.
    
    Args:
        dossier_id: Dossier ID
        dossier: Dossier data
    """
    
    with st.expander(f"📊 Analytics: {dossier.get('title', 'Untitled')}", expanded=True):
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            evidence_count = len(dossier.get('evidence_items', []))
            st.metric("Evidence Items", evidence_count)
        
        with col2:
            timeline_count = len(dossier.get('timeline', []))
            st.metric("Timeline Events", timeline_count)
        
        with col3:
            completion = calculate_completion_percentage(dossier)
            st.metric("Completion", f"{completion}%")
        
        # Timeline visualization (simple)
        timeline = dossier.get('timeline', [])
        if timeline:
            st.markdown("**Recent Activity:**")
            for event in timeline[-5:]:  # Show last 5 events
                st.write(f"• {event.get('date', 'Unknown')}: {event.get('description', 'No description')}")
        else:
            st.info("No timeline events recorded yet.")


def confirm_delete_dossier(dossier_id: str) -> None:
    """Confirm deletion of a dossier.
    
    Args:
        dossier_id: ID of dossier to delete
    """
    
    # Simple confirmation using session state
    confirm_key = f"confirm_delete_{dossier_id}"
    
    if not st.session_state.get(confirm_key, False):
        st.session_state[confirm_key] = True
        st.warning("⚠️ Confirm deletion by clicking the delete button again.")
        st.rerun()
    else:
        # Actually delete
        dossiers = get_session_data("dossiers", {})
        if dossier_id in dossiers:
            title = dossiers[dossier_id].get('title', 'Unknown')
            del dossiers[dossier_id]
            set_session_data("dossiers", dossiers)
            show_success_message(f"🗑️ Dossier '{title}' deleted successfully.")
        
        # Reset confirmation state
        if confirm_key in st.session_state:
            del st.session_state[confirm_key]
        
        st.rerun()
