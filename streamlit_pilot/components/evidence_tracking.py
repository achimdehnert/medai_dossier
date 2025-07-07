"""
Evidence Tracking page for Streamlit MVP.

Handles management of evidence items, studies, and supporting documentation.
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
    """Render the evidence tracking page."""
    
    st.header("📊 Evidence Tracking")
    
    # Show success message if any
    if st.session_state.get("show_success_message"):
        st.success(st.session_state.get("success_message", ""))
        clear_success_message()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Evidence", "➕ Add Evidence", "🔍 Search & Filter", "📈 Analytics"])
    
    with tab1:
        render_evidence_list()
    
    with tab2:
        render_add_evidence()
    
    with tab3:
        render_evidence_search()
    
    with tab4:
        render_evidence_analytics()


def render_evidence_list() -> None:
    """Render the list of all evidence items."""
    
    evidence_entries = get_session_data("evidence_entries", {})
    dossiers = get_session_data("dossiers", {})
    
    if not evidence_entries:
        st.info("📭 No evidence items added yet. Use the 'Add Evidence' tab to get started!")
        return
    
    st.subheader(f"📋 All Evidence Items ({len(evidence_entries)})")
    
    # Quick filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        evidence_type_filter = st.selectbox(
            "Filter by Type", 
            ["All", "Clinical Trial", "Real World Evidence", "Literature Review", "Meta-Analysis", "Registry Study", "Other"]
        )
    
    with col2:
        quality_filter = st.selectbox("Filter by Quality", ["All", "High", "Medium", "Low"])
    
    with col3:
        dossier_filter_options = ["All"] + [f"{did}: {d.get('title', 'Untitled')}" for did, d in dossiers.items()]
        dossier_filter = st.selectbox("Filter by Dossier", dossier_filter_options)
    
    # Filter evidence
    filtered_evidence = filter_evidence(evidence_entries, evidence_type_filter, quality_filter, dossier_filter)
    
    # Display evidence items
    for evidence_id, evidence in filtered_evidence.items():
        render_evidence_card(evidence_id, evidence)


def render_evidence_card(evidence_id: str, evidence: Dict[str, Any]) -> None:
    """Render a single evidence item card.
    
    Args:
        evidence_id: Unique evidence identifier
        evidence: Evidence data dictionary
    """
    
    with st.container():
        st.markdown("---")
        
        # Header row
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(f"📄 {evidence.get('title', 'Untitled Evidence')}")
            st.caption(f"ID: {evidence_id}")
        
        with col2:
            evidence_type = evidence.get('evidence_type', 'Other')
            st.markdown(f"**Type:** {evidence_type}")
            
            quality = evidence.get('quality_rating', 'Medium')
            quality_color = get_quality_color(quality)
            st.markdown(f"**Quality:** :{quality_color}[{quality}]")
        
        with col3:
            study_date = evidence.get('study_date', 'Unknown')
            if isinstance(study_date, str) and study_date != 'Unknown':
                try:
                    study_date = datetime.fromisoformat(study_date).strftime('%Y-%m-%d')
                except:
                    pass
            st.markdown(f"**Study Date:** {study_date}")
        
        # Details row
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Study details
            st.markdown(f"**Study Population:** {evidence.get('study_population', 'Not specified')}")
            st.markdown(f"**Primary Endpoint:** {evidence.get('primary_endpoint', 'Not specified')}")
            
            # Key findings
            key_findings = evidence.get('key_findings', 'No findings recorded')
            st.markdown(f"**Key Findings:** {key_findings}")
            
            # Associated dossier
            dossier_id = evidence.get('associated_dossier')
            if dossier_id:
                dossiers = get_session_data("dossiers", {})
                dossier_title = dossiers.get(dossier_id, {}).get('title', 'Unknown Dossier')
                st.markdown(f"**Associated Dossier:** {dossier_title}")
        
        with col2:
            # Action buttons
            st.write("**Actions:**")
            
            if st.button(f"✏️ Edit", key=f"edit_evidence_{evidence_id}", use_container_width=True):
                edit_evidence_item(evidence_id)
            
            if st.button(f"👀 View Details", key=f"view_evidence_{evidence_id}", use_container_width=True):
                show_evidence_details(evidence_id, evidence)
            
            if st.button(f"📊 Analytics", key=f"analytics_evidence_{evidence_id}", use_container_width=True):
                show_evidence_analytics(evidence_id, evidence)
            
            if st.button(f"🗑️ Delete", key=f"delete_evidence_{evidence_id}", use_container_width=True, type="secondary"):
                confirm_delete_evidence(evidence_id)


def render_add_evidence() -> None:
    """Render the add new evidence form."""
    
    st.subheader("➕ Add New Evidence")
    
    # Get available dossiers for association
    dossiers = get_session_data("dossiers", {})
    dossier_options = ["None"] + [f"{did}: {d.get('title', 'Untitled')}" for did, d in dossiers.items()]
    
    with st.form("add_evidence_form"):
        # Basic information
        st.markdown("### 📝 Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Evidence Title *", placeholder="e.g., Phase III RCT for Drug X")
            evidence_type = st.selectbox(
                "Evidence Type *",
                ["Clinical Trial", "Real World Evidence", "Literature Review", "Meta-Analysis", "Registry Study", "Other"]
            )
            study_phase = st.selectbox(
                "Study Phase",
                ["Not Applicable", "Preclinical", "Phase I", "Phase II", "Phase III", "Phase IV", "Post-Market"]
            )
        
        with col2:
            study_date = st.date_input("Study Date", value=None)
            quality_rating = st.selectbox("Quality Rating", ["High", "Medium", "Low"])
            associated_dossier = st.selectbox("Associated Dossier", dossier_options)
        
        # Study details
        st.markdown("### 🔬 Study Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            study_population = st.text_input(
                "Study Population", 
                placeholder="e.g., Adults with moderate Alzheimer's disease (n=500)"
            )
            primary_endpoint = st.text_input(
                "Primary Endpoint", 
                placeholder="e.g., Change in ADAS-Cog score at 24 weeks"
            )
        
        with col2:
            study_duration = st.text_input(
                "Study Duration", 
                placeholder="e.g., 24 weeks"
            )
            comparator = st.text_input(
                "Comparator", 
                placeholder="e.g., Placebo, Standard of Care"
            )
        
        # Findings and outcomes
        st.markdown("### 📈 Findings & Outcomes")
        
        key_findings = st.text_area(
            "Key Findings", 
            placeholder="Summarize the main results and statistical significance...",
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            primary_result = st.text_input(
                "Primary Result", 
                placeholder="e.g., 3.2 point improvement (p<0.001)"
            )
            statistical_significance = st.selectbox(
                "Statistical Significance",
                ["Yes (p<0.05)", "No (p≥0.05)", "Not Reported", "Not Applicable"]
            )
        
        with col2:
            safety_profile = st.text_area(
                "Safety Profile", 
                placeholder="Summary of adverse events and safety findings...",
                height=80
            )
        
        # Additional metadata
        st.markdown("### 📚 Additional Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            publication_status = st.selectbox(
                "Publication Status",
                ["Published", "Submitted", "In Preparation", "Unpublished"]
            )
            journal = st.text_input("Journal/Source", placeholder="e.g., New England Journal of Medicine")
        
        with col2:
            doi = st.text_input("DOI/Reference", placeholder="e.g., 10.1056/NEJMoa...")
            tags = st.text_input("Tags", placeholder="Comma-separated tags for categorization")
        
        # Form submission
        submitted = st.form_submit_button("🚀 Add Evidence", use_container_width=True)
        
        if submitted:
            if not title or not evidence_type:
                st.error("❌ Please provide both title and evidence type.")
            else:
                # Process associated dossier
                dossier_id = None
                if associated_dossier != "None":
                    dossier_id = associated_dossier.split(":")[0]
                
                create_new_evidence({
                    "title": title,
                    "evidence_type": evidence_type,
                    "study_phase": study_phase,
                    "study_date": study_date.isoformat() if study_date else None,
                    "quality_rating": quality_rating,
                    "associated_dossier": dossier_id,
                    "study_population": study_population,
                    "primary_endpoint": primary_endpoint,
                    "study_duration": study_duration,
                    "comparator": comparator,
                    "key_findings": key_findings,
                    "primary_result": primary_result,
                    "statistical_significance": statistical_significance,
                    "safety_profile": safety_profile,
                    "publication_status": publication_status,
                    "journal": journal,
                    "doi": doi,
                    "tags": [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
                })


def render_evidence_search() -> None:
    """Render advanced search and filtering interface."""
    
    st.subheader("🔍 Advanced Search & Filter")
    
    evidence_entries = get_session_data("evidence_entries", {})
    
    if not evidence_entries:
        st.info("📭 No evidence items to search. Add some evidence first!")
        return
    
    # Search interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search Evidence", 
            placeholder="Search in title, findings, population..."
        )
    
    with col2:
        search_button = st.button("🔍 Search", use_container_width=True)
    
    # Advanced filters
    with st.expander("🎛️ Advanced Filters", expanded=False):
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_range = st.date_input("Study Date Range", value=[], max_value=date.today())
            quality_multi = st.multiselect("Quality Ratings", ["High", "Medium", "Low"])
        
        with col2:
            evidence_types = st.multiselect(
                "Evidence Types", 
                ["Clinical Trial", "Real World Evidence", "Literature Review", "Meta-Analysis", "Registry Study", "Other"]
            )
            phases = st.multiselect(
                "Study Phases",
                ["Preclinical", "Phase I", "Phase II", "Phase III", "Phase IV", "Post-Market"]
            )
        
        with col3:
            pub_status = st.multiselect(
                "Publication Status",
                ["Published", "Submitted", "In Preparation", "Unpublished"]
            )
            stat_sig = st.multiselect(
                "Statistical Significance",
                ["Yes (p<0.05)", "No (p≥0.05)", "Not Reported", "Not Applicable"]
            )
    
    # Perform search
    if search_query or search_button:
        results = perform_evidence_search(
            evidence_entries, 
            search_query, 
            {
                "date_range": date_range,
                "quality": quality_multi,
                "evidence_types": evidence_types,
                "phases": phases,
                "publication_status": pub_status,
                "statistical_significance": stat_sig
            }
        )
        
        st.subheader(f"📊 Search Results ({len(results)} items)")
        
        if results:
            for evidence_id, evidence in results.items():
                render_evidence_card(evidence_id, evidence)
        else:
            st.info("No evidence items match your search criteria.")


def render_evidence_analytics() -> None:
    """Render evidence analytics and insights."""
    
    evidence_entries = get_session_data("evidence_entries", {})
    
    if not evidence_entries:
        st.info("📊 No evidence data to analyze yet. Add some evidence first!")
        return
    
    st.subheader("📈 Evidence Analytics")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Evidence", len(evidence_entries))
    
    with col2:
        high_quality_count = sum(1 for e in evidence_entries.values() if e.get('quality_rating') == 'High')
        st.metric("High Quality", high_quality_count)
    
    with col3:
        published_count = sum(1 for e in evidence_entries.values() if e.get('publication_status') == 'Published')
        st.metric("Published", published_count)
    
    with col4:
        significant_count = sum(1 for e in evidence_entries.values() if e.get('statistical_significance') == 'Yes (p<0.05)')
        st.metric("Statistically Significant", significant_count)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Evidence type distribution
        type_data = {}
        for evidence in evidence_entries.values():
            etype = evidence.get('evidence_type', 'Other')
            type_data[etype] = type_data.get(etype, 0) + 1
        
        st.subheader("Evidence Types")
        st.bar_chart(type_data)
    
    with col2:
        # Quality distribution
        quality_data = {}
        for evidence in evidence_entries.values():
            quality = evidence.get('quality_rating', 'Medium')
            quality_data[quality] = quality_data.get(quality, 0) + 1
        
        st.subheader("Quality Ratings")
        st.bar_chart(quality_data)
    
    # Detailed analytics
    st.subheader("📋 Detailed Insights")
    
    # Quality by evidence type
    st.markdown("**Quality Distribution by Evidence Type:**")
    quality_by_type = {}
    for evidence in evidence_entries.values():
        etype = evidence.get('evidence_type', 'Other')
        quality = evidence.get('quality_rating', 'Medium')
        
        if etype not in quality_by_type:
            quality_by_type[etype] = {"High": 0, "Medium": 0, "Low": 0}
        quality_by_type[etype][quality] += 1
    
    # Display as table
    import pandas as pd
    df = pd.DataFrame(quality_by_type).T.fillna(0)
    st.dataframe(df, use_container_width=True)


def filter_evidence(
    evidence_entries: Dict[str, Any], 
    evidence_type_filter: str, 
    quality_filter: str, 
    dossier_filter: str
) -> Dict[str, Any]:
    """Filter evidence entries based on criteria.
    
    Args:
        evidence_entries: Dictionary of evidence entries
        evidence_type_filter: Evidence type to filter by
        quality_filter: Quality rating to filter by
        dossier_filter: Associated dossier to filter by
        
    Returns:
        Filtered evidence entries dictionary
    """
    
    filtered = {}
    
    for evidence_id, evidence in evidence_entries.items():
        # Apply evidence type filter
        if evidence_type_filter != "All":
            if evidence.get('evidence_type', 'Other') != evidence_type_filter:
                continue
        
        # Apply quality filter
        if quality_filter != "All":
            if evidence.get('quality_rating', 'Medium') != quality_filter:
                continue
        
        # Apply dossier filter
        if dossier_filter != "All":
            dossier_id = dossier_filter.split(":")[0] if ":" in dossier_filter else None
            if evidence.get('associated_dossier') != dossier_id:
                continue
        
        filtered[evidence_id] = evidence
    
    return filtered


def create_new_evidence(evidence_data: Dict[str, Any]) -> None:
    """Create a new evidence item.
    
    Args:
        evidence_data: Evidence information dictionary
    """
    
    # Generate unique ID
    evidence_id = str(uuid.uuid4())
    
    # Add metadata
    evidence_data.update({
        "created_date": datetime.now().isoformat(),
        "last_modified": datetime.now().isoformat(),
        "version": "1.0.0"
    })
    
    # Save to session state
    evidence_entries = get_session_data("evidence_entries", {})
    evidence_entries[evidence_id] = evidence_data
    set_session_data("evidence_entries", evidence_entries)
    
    # Update associated dossier if any
    dossier_id = evidence_data.get('associated_dossier')
    if dossier_id:
        dossiers = get_session_data("dossiers", {})
        if dossier_id in dossiers:
            if 'evidence_items' not in dossiers[dossier_id]:
                dossiers[dossier_id]['evidence_items'] = []
            dossiers[dossier_id]['evidence_items'].append(evidence_id)
            set_session_data("dossiers", dossiers)
    
    # Show success message
    show_success_message(f"✅ Evidence '{evidence_data['title']}' added successfully!")
    
    st.rerun()


def perform_evidence_search(
    evidence_entries: Dict[str, Any], 
    search_query: str, 
    filters: Dict[str, Any]
) -> Dict[str, Any]:
    """Perform advanced search on evidence entries.
    
    Args:
        evidence_entries: Dictionary of evidence entries
        search_query: Text search query
        filters: Dictionary of advanced filters
        
    Returns:
        Filtered evidence entries dictionary
    """
    
    results = {}
    
    for evidence_id, evidence in evidence_entries.items():
        # Text search
        if search_query:
            searchable_text = " ".join([
                evidence.get('title', ''),
                evidence.get('key_findings', ''),
                evidence.get('study_population', ''),
                evidence.get('primary_endpoint', ''),
                evidence.get('primary_result', '')
            ]).lower()
            
            if search_query.lower() not in searchable_text:
                continue
        
        # Apply advanced filters
        if filters.get('quality') and evidence.get('quality_rating') not in filters['quality']:
            continue
        
        if filters.get('evidence_types') and evidence.get('evidence_type') not in filters['evidence_types']:
            continue
        
        if filters.get('phases') and evidence.get('study_phase') not in filters['phases']:
            continue
        
        if filters.get('publication_status') and evidence.get('publication_status') not in filters['publication_status']:
            continue
        
        if filters.get('statistical_significance') and evidence.get('statistical_significance') not in filters['statistical_significance']:
            continue
        
        # Date range filter
        if filters.get('date_range') and len(filters['date_range']) == 2:
            study_date = evidence.get('study_date')
            if study_date:
                try:
                    study_date_obj = datetime.fromisoformat(study_date).date()
                    if not (filters['date_range'][0] <= study_date_obj <= filters['date_range'][1]):
                        continue
                except:
                    continue
        
        results[evidence_id] = evidence
    
    return results


def get_quality_color(quality: str) -> str:
    """Get color for quality rating display.
    
    Args:
        quality: Quality rating string
        
    Returns:
        Color name for Streamlit
    """
    
    color_map = {
        "High": "green",
        "Medium": "orange",
        "Low": "red"
    }
    
    return color_map.get(quality, "gray")


def show_evidence_details(evidence_id: str, evidence: Dict[str, Any]) -> None:
    """Show detailed view of an evidence item.
    
    Args:
        evidence_id: Evidence ID
        evidence: Evidence data
    """
    
    with st.expander(f"📄 Details: {evidence.get('title', 'Untitled')}", expanded=True):
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Study Information:**")
            st.write(f"• **Type:** {evidence.get('evidence_type', 'N/A')}")
            st.write(f"• **Phase:** {evidence.get('study_phase', 'N/A')}")
            st.write(f"• **Population:** {evidence.get('study_population', 'N/A')}")
            st.write(f"• **Duration:** {evidence.get('study_duration', 'N/A')}")
            st.write(f"• **Comparator:** {evidence.get('comparator', 'N/A')}")
        
        with col2:
            st.markdown("**Publication & Quality:**")
            st.write(f"• **Quality:** {evidence.get('quality_rating', 'N/A')}")
            st.write(f"• **Status:** {evidence.get('publication_status', 'N/A')}")
            st.write(f"• **Journal:** {evidence.get('journal', 'N/A')}")
            st.write(f"• **DOI:** {evidence.get('doi', 'N/A')}")
            st.write(f"• **Statistical Significance:** {evidence.get('statistical_significance', 'N/A')}")
        
        st.markdown("**Primary Endpoint:**")
        st.write(evidence.get('primary_endpoint', 'Not specified'))
        
        st.markdown("**Primary Result:**")
        st.write(evidence.get('primary_result', 'Not specified'))
        
        st.markdown("**Key Findings:**")
        st.write(evidence.get('key_findings', 'No findings recorded'))
        
        st.markdown("**Safety Profile:**")
        st.write(evidence.get('safety_profile', 'No safety information recorded'))
        
        # Tags
        tags = evidence.get('tags', [])
        if tags:
            st.markdown("**Tags:**")
            st.write(", ".join([f"`{tag}`" for tag in tags]))


def show_evidence_analytics(evidence_id: str, evidence: Dict[str, Any]) -> None:
    """Show analytics for a specific evidence item.
    
    Args:
        evidence_id: Evidence ID
        evidence: Evidence data
    """
    
    with st.expander(f"📊 Analytics: {evidence.get('title', 'Untitled')}", expanded=True):
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            quality = evidence.get('quality_rating', 'Medium')
            quality_score = {"High": 3, "Medium": 2, "Low": 1}.get(quality, 2)
            st.metric("Quality Score", f"{quality_score}/3")
        
        with col2:
            is_published = evidence.get('publication_status') == 'Published'
            st.metric("Published", "✅" if is_published else "❌")
        
        with col3:
            is_significant = evidence.get('statistical_significance') == 'Yes (p<0.05)'
            st.metric("Statistically Significant", "✅" if is_significant else "❌")
        
        # Additional insights
        st.markdown("**Evidence Strength Assessment:**")
        
        strengths = []
        if quality == "High":
            strengths.append("High quality study design")
        if is_published:
            strengths.append("Peer-reviewed publication")
        if is_significant:
            strengths.append("Statistically significant results")
        if evidence.get('study_phase') in ["Phase III", "Phase IV"]:
            strengths.append("Late-phase clinical evidence")
        
        if strengths:
            for strength in strengths:
                st.write(f"✅ {strength}")
        else:
            st.write("⚠️ Consider strengthening evidence quality")


def edit_evidence_item(evidence_id: str) -> None:
    """Edit an evidence item (placeholder for future implementation).
    
    Args:
        evidence_id: ID of evidence to edit
    """
    
    st.info("📝 Edit functionality will be added in future version.")


def confirm_delete_evidence(evidence_id: str) -> None:
    """Confirm deletion of an evidence item.
    
    Args:
        evidence_id: ID of evidence to delete
    """
    
    # Simple confirmation using session state
    confirm_key = f"confirm_delete_evidence_{evidence_id}"
    
    if not st.session_state.get(confirm_key, False):
        st.session_state[confirm_key] = True
        st.warning("⚠️ Confirm deletion by clicking the delete button again.")
        st.rerun()
    else:
        # Actually delete
        evidence_entries = get_session_data("evidence_entries", {})
        if evidence_id in evidence_entries:
            title = evidence_entries[evidence_id].get('title', 'Unknown')
            
            # Remove from associated dossier
            dossier_id = evidence_entries[evidence_id].get('associated_dossier')
            if dossier_id:
                dossiers = get_session_data("dossiers", {})
                if dossier_id in dossiers and 'evidence_items' in dossiers[dossier_id]:
                    dossiers[dossier_id]['evidence_items'] = [
                        eid for eid in dossiers[dossier_id]['evidence_items'] if eid != evidence_id
                    ]
                    set_session_data("dossiers", dossiers)
            
            del evidence_entries[evidence_id]
            set_session_data("evidence_entries", evidence_entries)
            show_success_message(f"🗑️ Evidence '{title}' deleted successfully.")
        
        # Reset confirmation state
        if confirm_key in st.session_state:
            del st.session_state[confirm_key]
        
        st.rerun()
