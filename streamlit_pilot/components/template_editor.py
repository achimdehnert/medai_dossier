"""
Template Editor component for creating and editing dossier templates.

Provides comprehensive template editing capabilities on a dedicated page.
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from utils.session_state import (
    get_session_data, 
    set_session_data, 
    show_success_message
)
from components.template_management import get_template_by_id, get_all_templates


def render() -> None:
    """Render the template editor page."""
    
    # Get editing mode and template ID
    edit_mode = st.session_state.get("template_edit_mode", "create")  # "create" or "edit"
    template_id = st.session_state.get("editing_template_id")
    
    # Header with navigation
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔙 Zurück zu Templates"):
            st.session_state.current_page = "template_management"
            cleanup_editor_session()
            st.rerun()
    
    with col2:
        if edit_mode == "edit" and template_id:
            if st.button("👁️ Vorschau", type="secondary"):
                st.session_state.preview_template_id = template_id
                st.session_state.current_page = "template_preview"
                cleanup_editor_session()
                st.rerun()
    
    st.divider()
    
    # Main editor content
    if edit_mode == "create":
        render_create_template_editor()
    elif edit_mode == "edit" and template_id:
        render_edit_template_editor(template_id)
    else:
        st.error("❌ Ungültiger Editor-Modus oder fehlende Template-ID.")
        if st.button("🔙 Zurück zu Templates"):
            st.session_state.current_page = "template_management"
            cleanup_editor_session()
            st.rerun()


def render_create_template_editor() -> None:
    """Render the create new template editor."""
    
    st.header("➕ Neues Template erstellen")
    
    # Template basic information
    with st.form("create_template_form"):
        st.subheader("📋 Template-Grundinformationen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            template_name = st.text_input(
                "Template-Name *",
                placeholder="z.B. 'NICE HST Template'"
            )
            
            template_category = st.selectbox(
                "Kategorie *",
                options=["HTA", "Regulatory", "Internal", "Andere"],
                index=0
            )
        
        with col2:
            template_description = st.text_area(
                "Beschreibung",
                placeholder="Kurze Beschreibung des Templates..."
            )
        
        st.subheader("📑 Template-Sektionen")
        
        # Section management
        if "new_template_sections" not in st.session_state:
            st.session_state.new_template_sections = {}
        
        render_section_editor(st.session_state.new_template_sections)
        
        # Add new section
        with st.expander("➕ Neue Sektion hinzufügen"):
            render_add_section_form()
        
        # Submit button
        submitted = st.form_submit_button("💾 Template erstellen", type="primary")
        
        if submitted:
            if template_name and template_category:
                create_new_template(
                    template_name,
                    template_category,
                    template_description,
                    st.session_state.new_template_sections
                )
            else:
                st.error("❌ Bitte füllen Sie alle Pflichtfelder aus.")


def render_edit_template_editor(template_id: str) -> None:
    """Render the edit existing template editor."""
    
    template = get_template_by_id(template_id)
    
    if not template:
        st.error(f"❌ Template mit ID '{template_id}' nicht gefunden.")
        return
    
    st.header(f"✏️ Template bearbeiten: {template.get('name', 'Unbenannt')}")
    
    # Template basic information
    with st.form("edit_template_form"):
        st.subheader("📋 Template-Grundinformationen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            template_name = st.text_input(
                "Template-Name *",
                value=template.get('name', ''),
                placeholder="z.B. 'NICE HST Template'"
            )
            
            template_category = st.selectbox(
                "Kategorie *",
                options=["HTA", "Regulatory", "Internal", "Andere"],
                index=["HTA", "Regulatory", "Internal", "Andere"].index(
                    template.get('category', 'Andere')
                )
            )
        
        with col2:
            template_description = st.text_area(
                "Beschreibung",
                value=template.get('description', ''),
                placeholder="Kurze Beschreibung des Templates..."
            )
        
        st.subheader("📑 Template-Sektionen")
        
        # Initialize sections from template
        if f"edit_template_sections_{template_id}" not in st.session_state:
            st.session_state[f"edit_template_sections_{template_id}"] = template.get('sections', {}).copy()
        
        current_sections = st.session_state[f"edit_template_sections_{template_id}"]
        render_section_editor(current_sections)
        
        # Add new section
        with st.expander("➕ Neue Sektion hinzufügen"):
            render_add_section_form(template_id)
        
        # Submit button
        submitted = st.form_submit_button("💾 Template aktualisieren", type="primary")
        
        if submitted:
            if template_name and template_category:
                update_template(
                    template_id,
                    template_name,
                    template_category,
                    template_description,
                    current_sections
                )
            else:
                st.error("❌ Bitte füllen Sie alle Pflichtfelder aus.")


def render_section_editor(sections: Dict[str, Any]) -> None:
    """Render the section editor interface."""
    
    if not sections:
        st.info("ℹ️ Noch keine Sektionen definiert. Fügen Sie unten eine neue Sektion hinzu.")
        return
    
    # Sort sections by order
    sorted_sections = sorted(sections.items(), key=lambda x: x[1].get('order', 999))
    
    for section_id, section_data in sorted_sections:
        render_section_card_editor(section_id, section_data, sections)


def render_section_card_editor(section_id: str, section_data: Dict[str, Any], all_sections: Dict[str, Any]) -> None:
    """Render individual section editor card."""
    
    with st.expander(f"📄 {section_data.get('title', 'Unbenannte Sektion')}", expanded=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Section title
            new_title = st.text_input(
                "Sektions-Titel",
                value=section_data.get('title', ''),
                key=f"title_{section_id}"
            )
            
            # Section description
            new_description = st.text_area(
                "Beschreibung",
                value=section_data.get('description', ''),
                key=f"desc_{section_id}"
            )
            
            # Section settings
            col_settings1, col_settings2 = st.columns(2)
            
            with col_settings1:
                new_icon = st.text_input(
                    "Icon",
                    value=section_data.get('icon', '📄'),
                    key=f"icon_{section_id}"
                )
                
                new_required = st.checkbox(
                    "Erforderlich",
                    value=section_data.get('required', False),
                    key=f"required_{section_id}"
                )
            
            with col_settings2:
                new_order = st.number_input(
                    "Reihenfolge",
                    min_value=1,
                    max_value=100,
                    value=section_data.get('order', 1),
                    key=f"order_{section_id}"
                )
        
        with col2:
            st.write("**Aktionen:**")
            
            if st.button("💾 Speichern", key=f"save_{section_id}"):
                # Update section data
                all_sections[section_id].update({
                    'title': new_title,
                    'description': new_description,
                    'icon': new_icon,
                    'required': new_required,
                    'order': new_order
                })
                st.success(f"✅ Sektion '{new_title}' gespeichert!")
                st.rerun()
            
            if st.button("🗑️ Löschen", key=f"delete_{section_id}"):
                del all_sections[section_id]
                st.success(f"✅ Sektion gelöscht!")
                st.rerun()


def render_add_section_form(template_id: str = None) -> None:
    """Render form to add new section."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_section_title = st.text_input(
            "Sektions-Titel",
            placeholder="z.B. 'Clinical Evidence'",
            key=f"new_section_title_{template_id or 'create'}"
        )
        
        new_section_description = st.text_area(
            "Beschreibung",
            placeholder="Beschreibung der Sektion...",
            key=f"new_section_desc_{template_id or 'create'}"
        )
    
    with col2:
        new_section_icon = st.text_input(
            "Icon",
            value="📄",
            key=f"new_section_icon_{template_id or 'create'}"
        )
        
        new_section_required = st.checkbox(
            "Erforderlich",
            key=f"new_section_required_{template_id or 'create'}"
        )
        
        new_section_order = st.number_input(
            "Reihenfolge",
            min_value=1,
            max_value=100,
            value=1,
            key=f"new_section_order_{template_id or 'create'}"
        )
    
    if st.button("➕ Sektion hinzufügen", key=f"add_section_{template_id or 'create'}"):
        if new_section_title:
            # Generate section ID
            section_id = f"section_{uuid.uuid4().hex[:8]}"
            
            # Add to appropriate sections dict
            if template_id:
                sections_key = f"edit_template_sections_{template_id}"
            else:
                sections_key = "new_template_sections"
            
            if sections_key not in st.session_state:
                st.session_state[sections_key] = {}
            
            st.session_state[sections_key][section_id] = {
                'title': new_section_title,
                'description': new_section_description,
                'icon': new_section_icon,
                'required': new_section_required,
                'order': new_section_order
            }
            
            st.success(f"✅ Sektion '{new_section_title}' hinzugefügt!")
            st.rerun()
        else:
            st.error("❌ Bitte geben Sie einen Sektions-Titel ein.")


def create_new_template(name: str, category: str, description: str, sections: Dict[str, Any]) -> None:
    """Create a new template."""
    
    try:
        # Generate template ID
        template_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        # Create template data
        template_data = {
            'name': name,
            'category': category,
            'description': description,
            'sections': sections,
            'created_date': datetime.now().isoformat(),
            'modified_date': datetime.now().isoformat(),
            'is_custom': True
        }
        
        # Save to session state
        templates = get_session_data("templates", {})
        templates[template_id] = template_data
        set_session_data("templates", templates)
        
        # Success message
        show_success_message(f"✅ Template '{name}' erfolgreich erstellt!")
        
        st.success(f"""
        🎉 **Template erfolgreich erstellt!**
        
        **Name:** {name}  
        **Kategorie:** {category}  
        **Sektionen:** {len(sections)} definiert
        """)
        
        # Clean up session state
        if "new_template_sections" in st.session_state:
            del st.session_state.new_template_sections
        
        # Navigate back
        if st.button("📋 Zu Templates wechseln"):
            st.session_state.current_page = "template_management"
            cleanup_editor_session()
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Fehler beim Erstellen des Templates: {str(e)}")


def update_template(template_id: str, name: str, category: str, description: str, sections: Dict[str, Any]) -> None:
    """Update an existing template."""
    
    try:
        # Get existing templates
        templates = get_session_data("templates", {})
        
        if template_id not in templates:
            st.error(f"❌ Template mit ID '{template_id}' nicht gefunden.")
            return
        
        # Update template data
        templates[template_id].update({
            'name': name,
            'category': category,
            'description': description,
            'sections': sections,
            'modified_date': datetime.now().isoformat()
        })
        
        # Save to session state
        set_session_data("templates", templates)
        
        # Success message
        show_success_message(f"✅ Template '{name}' aktualisiert!")
        
        st.success(f"""
        🎉 **Template erfolgreich aktualisiert!**
        
        **Name:** {name}  
        **Kategorie:** {category}  
        **Sektionen:** {len(sections)} definiert
        """)
        
        # Clean up session state
        if f"edit_template_sections_{template_id}" in st.session_state:
            del st.session_state[f"edit_template_sections_{template_id}"]
        
        # Navigate back
        if st.button("📋 Zu Templates wechseln"):
            st.session_state.current_page = "template_management"
            cleanup_editor_session()
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Fehler beim Aktualisieren des Templates: {str(e)}")


def cleanup_editor_session() -> None:
    """Clean up template editor session state variables."""
    
    keys_to_remove = [
        "template_edit_mode",
        "editing_template_id",
        "new_template_sections"
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    # Remove edit-specific section keys
    keys_to_remove_pattern = [
        "edit_template_sections_",
        "new_section_title_",
        "new_section_desc_",
        "new_section_icon_",
        "new_section_required_",
        "new_section_order_"
    ]
    
    for key in list(st.session_state.keys()):
        for pattern in keys_to_remove_pattern:
            if key.startswith(pattern):
                del st.session_state[key]
                break
