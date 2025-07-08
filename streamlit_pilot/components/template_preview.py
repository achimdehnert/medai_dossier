"""
Template Preview component for detailed template viewing.

Shows comprehensive template structure and details on a dedicated page.
"""

import streamlit as st
from typing import Dict, Any, Optional

from utils.session_state import get_session_data
from components.template_management import get_template_by_id, get_all_templates


def render() -> None:
    """Render the template preview page."""
    
    # Get template ID from session state
    template_id = st.session_state.get("preview_template_id")
    
    if not template_id:
        st.error("❌ Kein Template zum Anzeigen ausgewählt.")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔙 Zurück zu Templates"):
                st.session_state.current_page = "template_management"
                st.rerun()
        return
    
    # Get template data
    template = get_template_by_id(template_id)
    
    if not template:
        st.error(f"❌ Template mit ID '{template_id}' nicht gefunden.")
        
        if st.button("🔙 Zurück zu Templates"):
            st.session_state.current_page = "template_management"
            st.rerun()
        return
    
    # Header with navigation
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔙 Zurück zu Templates"):
            st.session_state.current_page = "template_management"
            if "preview_template_id" in st.session_state:
                del st.session_state.preview_template_id
            st.rerun()
    
    with col2:
        if st.button("🚀 Template verwenden", type="primary"):
            st.session_state.selected_template = template_id
            st.session_state.current_page = "value_dossier_structure"
            if "preview_template_id" in st.session_state:
                del st.session_state.preview_template_id
            st.rerun()
    
    st.divider()
    
    # Template header
    category_icon = get_category_icon(template.get('category', 'Andere'))
    st.header(f"{category_icon} {template.get('name', 'Unbenanntes Template')}")
    
    # Template metadata section
    render_template_metadata(template_id, template)
    
    # Template sections section
    render_template_sections(template)
    
    # Usage information
    render_template_usage(template_id)


def render_template_metadata(template_id: str, template: Dict[str, Any]) -> None:
    """Render template metadata information."""
    
    st.subheader("📋 Template-Informationen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Template-ID", template_id)
        st.metric("Kategorie", template.get('category', 'Nicht definiert'))
        
        sections = template.get('sections', {})
        required_count = sum(1 for s in sections.values() if s.get('required', False))
        optional_count = len(sections) - required_count
        
        st.metric("Sektionen (gesamt)", len(sections))
    
    with col2:
        st.metric("Erforderliche Sektionen", required_count)
        st.metric("Optionale Sektionen", optional_count)
        
        # Usage count
        usage_count = get_template_usage_count(template_id)
        st.metric("Verwendungen", usage_count)
    
    # Description
    if template.get('description'):
        st.markdown("**Beschreibung:**")
        st.info(template.get('description'))


def render_template_sections(template: Dict[str, Any]) -> None:
    """Render detailed template sections."""
    
    st.subheader("📑 Template-Sektionen")
    
    sections = template.get('sections', {})
    
    if not sections:
        st.warning("⚠️ Dieses Template hat keine definierten Sektionen.")
        return
    
    # Sort sections by order
    sorted_sections = sorted(sections.items(), key=lambda x: x[1].get('order', 999))
    
    # Display sections in organized manner
    for i, (section_id, section_info) in enumerate(sorted_sections):
        render_section_card(i + 1, section_id, section_info)


def render_section_card(index: int, section_id: str, section_info: Dict[str, Any]) -> None:
    """Render individual section card."""
    
    # Section container
    with st.container():
        # Section header
        col1, col2, col3 = st.columns([6, 1, 1])
        
        with col1:
            icon = section_info.get('icon', '📄')
            title = section_info.get('title', 'Unbenannte Sektion')
            st.subheader(f"{icon} {title}")
        
        with col2:
            required = section_info.get('required', False)
            if required:
                st.markdown("**🔴 Erforderlich**")
            else:
                st.markdown("**🟡 Optional**")
        
        with col3:
            order = section_info.get('order', index)
            st.markdown(f"**Reihenfolge:** {order}")
        
        # Section description
        description = section_info.get('description', 'Keine Beschreibung verfügbar')
        st.markdown(f"**Beschreibung:** {description}")
        
        # Section ID for reference
        st.caption(f"**Sektion-ID:** `{section_id}`")
        
        st.markdown("---")


def render_template_usage(template_id: str) -> None:
    """Render template usage information."""
    
    st.subheader("📊 Verwendungsinformationen")
    
    # Get dossiers using this template
    dossiers = get_session_data("dossiers", {})
    template_dossiers = []
    
    for dossier_id, dossier in dossiers.items():
        if dossier.get('template_id') == template_id:
            template_dossiers.append({
                'id': dossier_id,
                'title': dossier.get('title', 'Unbenannt'),
                'product': dossier.get('product_name', 'N/A'),
                'status': dossier.get('status', 'Unbekannt'),
                'created': dossier.get('created_date', 'N/A')
            })
    
    if template_dossiers:
        st.write(f"**{len(template_dossiers)} Dossier(s) verwenden dieses Template:**")
        
        # Display dossiers in table format
        for dossier in template_dossiers:
            with st.expander(f"📊 {dossier['title']}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Produkt:** {dossier['product']}")
                    st.write(f"**Status:** {dossier['status']}")
                
                with col2:
                    st.write(f"**Erstellt:** {dossier['created'][:10] if len(dossier['created']) > 10 else dossier['created']}")
                
                if st.button(f"📋 Zu Dossier wechseln", key=f"goto_{dossier['id']}"):
                    st.session_state.current_page = "dossier_management"
                    if "preview_template_id" in st.session_state:
                        del st.session_state.preview_template_id
                    st.rerun()
    else:
        st.info("ℹ️ Dieses Template wird derzeit von keinem Dossier verwendet.")


def get_category_icon(category: str) -> str:
    """Get icon for template category."""
    
    category_icons = {
        'HTA': '🏛️',
        'Regulatory': '🏢', 
        'Internal': '🏠',
        'Andere': '📁'
    }
    
    return category_icons.get(category, '📁')


def get_template_usage_count(template_id: str) -> int:
    """Get usage count for a template."""
    
    dossiers = get_session_data("dossiers", {})
    return sum(1 for dossier in dossiers.values() if dossier.get('template_id') == template_id)
