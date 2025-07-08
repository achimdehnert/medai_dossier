"""
Template Management component for managing dossier structure templates.
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from utils.session_state import get_session_data, set_session_data, show_success_message

# Predefined HTA templates
PREDEFINED_TEMPLATES = {
    "hta_standard": {
        "name": "HTA Standard (International)",
        "description": "Standard HTA-konforme Struktur für internationale Behörden",
        "category": "HTA",
        "sections": {
            "executive_summary": {
                "title": "1. Executive Summary",
                "description": "Kurzzusammenfassung der wichtigsten Aussagen",
                "icon": "📋", "required": True, "order": 1
            },
            "disease_background": {
                "title": "2. Disease Background", 
                "description": "Krankheitsbeschreibung, Epidemiologie",
                "icon": "🏥", "required": True, "order": 2
            },
            "unmet_medical_need": {
                "title": "3. Unmet Medical Need",
                "description": "Unerfüllter medizinischer Bedarf",
                "icon": "🚧", "required": True, "order": 3
            },
            "product_profile": {
                "title": "4. Produktprofil / Clinical Profile",
                "description": "Wirkmechanismus, klinische Studien",
                "icon": "🔬", "required": True, "order": 4
            },
            "health_economic_evidence": {
                "title": "5. Health Economic Evidence",
                "description": "Kosten-Nutzen-Analysen, Budget Impact",
                "icon": "💰", "required": True, "order": 5
            },
            "patient_perspective": {
                "title": "6. Patient Perspective",
                "description": "Patient Reported Outcomes",
                "icon": "👥", "required": False, "order": 6
            },
            "value_proposition": {
                "title": "7. Value Proposition",
                "description": "Zusammenfassende Nutzenargumentation",
                "icon": "💡", "required": True, "order": 7
            },
            "supporting_materials": {
                "title": "8. Supporting Materials",
                "description": "Publikationen, Referenzen",
                "icon": "📚", "required": False, "order": 8
            }
        }
    },
    "iqwig_germany": {
        "name": "IQWiG/G-BA (Deutschland)",
        "description": "Spezifische Struktur für deutsche HTA-Bewertungen",
        "category": "HTA",
        "sections": {
            "zusammenfassung": {
                "title": "1. Zusammenfassung",
                "description": "Executive Summary für G-BA Verfahren",
                "icon": "📋", "required": True, "order": 1
            },
            "medizinische_indikation": {
                "title": "2. Medizinische Indikation", 
                "description": "Beschreibung der Erkrankung",
                "icon": "🏥", "required": True, "order": 2
            },
            "zusatznutzen": {
                "title": "3. Zusatznutzen",
                "description": "Darstellung des Zusatznutzens",
                "icon": "⭐", "required": True, "order": 3
            }
        }
    }
}

def render() -> None:
    """Render the template management page."""
    
    st.header("🗂️ Template Management")
    
    with st.expander("ℹ️ Template-System Info", expanded=False):
        st.markdown("""
        **Dossier-Template-System**
        
        Templates definieren die Struktur von Value Dossiers für verschiedene:
        - **HTA-Behörden** (NICE, IQWiG/G-BA, HAS, etc.)
        - **Regulatorische Behörden** (FDA, EMA, etc.)
        - **Unternehmensspezifische** Strukturen
        """)
    
    tab1, tab2, tab3 = st.tabs(["📋 Verfügbare Templates", "➕ Neues Template", "📊 Analytics"])
    
    with tab1:
        render_available_templates()
    with tab2:
        render_create_template()
    with tab3:
        render_template_analytics()

def render_available_templates() -> None:
    """Render list of available templates."""
    
    st.subheader("📋 Verfügbare Dossier-Templates")
    
    custom_templates = get_session_data("templates", {})
    all_templates = {**PREDEFINED_TEMPLATES, **custom_templates}
    
    if not all_templates:
        st.info("📭 Keine Templates verfügbar.")
        return
    
    for template_id, template in all_templates.items():
        render_template_card(template_id, template, is_predefined=(template_id in PREDEFINED_TEMPLATES))

def render_template_card(template_id: str, template: Dict[str, Any], is_predefined: bool) -> None:
    """Render a single template card."""
    
    with st.container():
        st.markdown("---")
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            category_icon = "🏛️" if template.get('category') == 'HTA' else "📁"
            st.subheader(f"{category_icon} {template.get('name', 'Unbenanntes Template')}")
            st.caption(f"ID: {template_id} {'(Vorinstalliert)' if is_predefined else '(Benutzerdefiniert)'}")
            st.write(f"**Beschreibung:** {template.get('description', 'Keine Beschreibung')}")
            
            sections = template.get('sections', {})
            required_count = sum(1 for s in sections.values() if s.get('required', False))
            st.write(f"**Sektionen:** {len(sections)} total ({required_count} erforderlich)")
        
        with col2:
            st.write(f"**Kategorie:** {template.get('category', 'Andere')}")
            usage_count = get_template_usage_count(template_id)
            st.metric("Verwendungen", usage_count)
        
        with col3:
            if st.button(f"👁️ Vorschau", key=f"preview_{template_id}", use_container_width=True):
                st.session_state.preview_template_id = template_id
                st.session_state.current_page = "template_preview"
                st.rerun()
            
            # Show edit button only for custom templates or allow editing predefined ones
            if not is_predefined or st.session_state.get("allow_edit_predefined", False):
                if st.button(f"✏️ Bearbeiten", key=f"edit_{template_id}", use_container_width=True):
                    st.session_state.template_edit_mode = "edit"
                    st.session_state.editing_template_id = template_id
                    st.session_state.current_page = "template_editor"
                    st.rerun()
            
            if st.button(f"🚀 Verwenden", key=f"use_{template_id}", use_container_width=True, type="primary"):
                st.session_state.selected_template = template_id
                st.session_state.current_page = "value_dossier_structure"
                st.rerun()

def render_create_template() -> None:
    """Render template creation form."""
    
    st.subheader("➕ Neues Template erstellen")
    st.info("💡 Erstellen Sie angepasste Templates für spezifische Anforderungen")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Template-Editor Features:**
        - 📝 Interaktive Sektions-Erstellung
        - 🎨 Anpassbare Icons und Reihenfolge
        - ✅ Pflicht-/Optional-Konfiguration
        - 👁️ Live-Vorschau während der Erstellung
        """)
    
    with col2:
        if st.button("🚀 Template-Editor öffnen", type="primary", use_container_width=True):
            st.session_state.template_edit_mode = "create"
            st.session_state.current_page = "template_editor"
            st.rerun()

def render_template_analytics() -> None:
    """Render template usage analytics."""
    
    st.subheader("📊 Template Analytics")
    
    templates = {**PREDEFINED_TEMPLATES, **get_session_data("templates", {})}
    
    if not templates:
        st.info("📭 Keine Templates verfügbar.")
        return
    
    usage_data = []
    for template_id, template in templates.items():
        usage_count = get_template_usage_count(template_id)
        usage_data.append({
            'Template': template.get('name', 'Unbenannt'),
            'Kategorie': template.get('category', 'Andere'),
            'Verwendungen': usage_count
        })
    
    st.write("**Meistgenutzte Templates:**")
    sorted_usage = sorted(usage_data, key=lambda x: x['Verwendungen'], reverse=True)
    for i, item in enumerate(sorted_usage[:5]):
        st.write(f"{i+1}. {item['Template']}: {item['Verwendungen']} Verwendungen")

def show_template_preview(template_id: str, template: Dict[str, Any]) -> None:
    """Show detailed preview of a template."""
    
    with st.expander(f"👁️ Vorschau: {template.get('name', 'Unbenannt')}", expanded=True):
        st.write(f"**Kategorie:** {template.get('category', 'N/A')}")
        
        sections = template.get('sections', {})
        if sections:
            st.write(f"**Sektionen ({len(sections)}):**")
            sorted_sections = sorted(sections.items(), key=lambda x: x[1].get('order', 999))
            
            for section_id, section in sorted_sections:
                required_icon = "✅" if section.get('required', False) else "⭕"
                st.write(f"  {section.get('icon', '📄')} **{section.get('title', 'Unbenannt')}** {required_icon}")

def get_template_usage_count(template_id: str) -> int:
    """Get usage count for a template."""
    
    dossiers = get_session_data("dossiers", {})
    return sum(1 for dossier in dossiers.values() if dossier.get('template_id') == template_id)

def get_template_by_id(template_id: str) -> Optional[Dict[str, Any]]:
    """Get template by ID."""
    
    if template_id in PREDEFINED_TEMPLATES:
        return PREDEFINED_TEMPLATES[template_id]
    
    custom_templates = get_session_data("templates", {})
    return custom_templates.get(template_id)

def get_all_templates() -> Dict[str, Dict[str, Any]]:
    """Get all available templates."""
    
    custom_templates = get_session_data("templates", {})
    return {**PREDEFINED_TEMPLATES, **custom_templates}
