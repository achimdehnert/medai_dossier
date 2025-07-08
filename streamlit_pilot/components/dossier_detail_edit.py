"""
Detailed dossier view and edit component.

Provides a comprehensive view/edit interface that mirrors the HTA-compliant 
Value Dossier structure with all 8 sections.
"""

import streamlit as st
import uuid
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import base64

from utils.session_state import (
    get_session_data, 
    set_session_data, 
    show_success_message
)

# Import the VALUE_DOSSIER_SECTIONS from value_dossier_structure
from components.value_dossier_structure import VALUE_DOSSIER_SECTIONS


def render() -> None:
    """Render the detailed dossier view/edit page."""
    
    # Get the dossier being edited/viewed
    dossier_id = st.session_state.get("editing_dossier")
    view_mode = st.session_state.get("dossier_view_mode", "edit")  # "edit" or "view"
    
    if not dossier_id:
        st.error("❌ Kein Dossier ausgewählt.")
        if st.button("🔙 Zurück zur Übersicht"):
            st.session_state.current_page = "dossier_management"
            st.rerun()
        return
    
    dossiers = get_session_data("dossiers", {})
    
    if dossier_id not in dossiers:
        st.error(f"❌ Dossier mit ID {dossier_id} nicht gefunden.")
        if st.button("🔙 Zurück zur Übersicht"):
            st.session_state.current_page = "dossier_management"
            st.rerun()
        return
    
    dossier = dossiers[dossier_id]
    
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        mode_icon = "✏️" if view_mode == "edit" else "👀"
        mode_text = "Bearbeiten" if view_mode == "edit" else "Ansicht"
        st.header(f"{mode_icon} {mode_text}: {dossier.get('title', 'Unbenanntes Dossier')}")
    
    with col2:
        if st.button("👀 Nur anzeigen" if view_mode == "edit" else "✏️ Bearbeiten"):
            st.session_state.dossier_view_mode = "view" if view_mode == "edit" else "edit"
            st.rerun()
    
    with col3:
        if st.button("🔙 Zurück"):
            st.session_state.current_page = "dossier_management"
            if "editing_dossier" in st.session_state:
                del st.session_state["editing_dossier"]
            if "dossier_view_mode" in st.session_state:
                del st.session_state["dossier_view_mode"]
            st.rerun()
    
    st.divider()
    
    # Dossier basic info
    render_basic_info(dossier, dossier_id, view_mode == "edit")
    
    st.divider()
    
    # Render HTA-compliant structure
    render_hta_structure(dossier, dossier_id, view_mode == "edit")
    
    # Save button (only in edit mode)
    if view_mode == "edit":
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("💾 Änderungen speichern", type="primary", use_container_width=True):
                save_dossier_changes(dossier_id)


def render_basic_info(dossier: Dict[str, Any], dossier_id: str, editable: bool) -> None:
    """Render basic dossier information section."""
    
    st.subheader("📋 Grundinformationen")
    
    if editable:
        with st.form("basic_info_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input(
                    "Titel*",
                    value=dossier.get('title', ''),
                    key="edit_title"
                )
                
                product_name = st.text_input(
                    "Produktname",
                    value=dossier.get('product_name', ''),
                    key="edit_product_name"
                )
                
                indication = st.text_input(
                    "Indikation",
                    value=dossier.get('indication', ''),
                    key="edit_indication"
                )
                
                company = st.text_input(
                    "Unternehmen",
                    value=dossier.get('company', ''),
                    key="edit_company"
                )
            
            with col2:
                status_options = ["Draft", "In Bearbeitung", "Review", "Genehmigt", "Abgelehnt"]
                current_status = dossier.get('status', 'Draft')
                status = st.selectbox(
                    "Status",
                    options=status_options,
                    index=status_options.index(current_status) if current_status in status_options else 0,
                    key="edit_status"
                )
                
                priority_options = ["Niedrig", "Mittel", "Hoch", "Kritisch"]
                current_priority = dossier.get('priority', 'Mittel')
                priority = st.selectbox(
                    "Priorität",
                    options=priority_options,
                    index=priority_options.index(current_priority) if current_priority in priority_options else 1,
                    key="edit_priority"
                )
                
                hta_agency = st.text_input(
                    "HTA-Behörde",
                    value=dossier.get('hta_agency', ''),
                    key="edit_hta_agency"
                )
                
                # Target submission date
                target_date = dossier.get('target_date')
                target_submission_date = st.date_input(
                    "Ziel-Einreichungsdatum",
                    value=datetime.fromisoformat(target_date).date() if target_date else None,
                    key="edit_target_date"
                )
            
            description = st.text_area(
                "Beschreibung",
                value=dossier.get('description', ''),
                height=100,
                key="edit_description"
            )
            
            if st.form_submit_button("💾 Grundinformationen aktualisieren"):
                update_basic_info(
                    dossier_id, title, product_name, indication, company,
                    status, priority, hta_agency, str(target_submission_date) if target_submission_date else None, description
                )
    else:
        # Read-only view
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Titel:** {dossier.get('title', 'N/A')}")
            st.write(f"**Produktname:** {dossier.get('product_name', 'N/A')}")
            st.write(f"**Indikation:** {dossier.get('indication', 'N/A')}")
            st.write(f"**Unternehmen:** {dossier.get('company', 'N/A')}")
        
        with col2:
            st.write(f"**Status:** {dossier.get('status', 'N/A')}")
            st.write(f"**Priorität:** {dossier.get('priority', 'N/A')}")
            st.write(f"**HTA-Behörde:** {dossier.get('hta_agency', 'N/A')}")
            st.write(f"**Zieldatum:** {dossier.get('target_date', 'N/A')}")
        
        if dossier.get('description'):
            st.write(f"**Beschreibung:** {dossier.get('description')}")


def render_hta_structure(dossier: Dict[str, Any], dossier_id: str, editable: bool) -> None:
    """Render the complete template-based structure."""
    
    # Check if dossier has template structure
    template_structure = dossier.get('structure', {})
    template_info = {
        'template_name': dossier.get('template_name', 'Standard'),
        'template_category': dossier.get('template_category', ''),
        'template_id': dossier.get('template_id', '')
    }
    
    if template_structure:
        # Use template-based structure
        st.subheader(f"📊 {template_info['template_name']} Struktur")
        if template_info['template_category']:
            st.caption(f"Kategorie: {template_info['template_category']}")
        
        # Get or initialize sections based on template
        sections = dossier.get('sections', {})
        
        # Sort template sections by order
        sorted_sections = sorted(
            template_structure.items(), 
            key=lambda x: x[1].get('order', 999)
        )
        
        # Ensure all template sections exist in dossier sections
        for section_key, section_template in sorted_sections:
            if section_key not in sections:
                sections[section_key] = {
                    "documents": [],
                    "notes": "",
                    "completion_status": "Nicht begonnen",
                    "content": ""
                }
        
        # Create tabs for all template sections
        section_tabs = st.tabs([
            f"{section_template['icon']} {section_template['title']}"
            for section_key, section_template in sorted_sections
        ])
        
        # Render each section
        for i, (section_key, section_template) in enumerate(sorted_sections):
            with section_tabs[i]:
                render_section_detail(
                    section_key, 
                    section_template, 
                    sections.get(section_key, {}), 
                    dossier_id, 
                    editable
                )
        
        # Update dossier sections if changes were made
        dossiers = get_session_data("dossiers", {})
        if dossier_id in dossiers:
            dossiers[dossier_id]['sections'] = sections
            set_session_data("dossiers", dossiers)
    
    else:
        # Fallback to static VALUE_DOSSIER_SECTIONS for legacy dossiers
        st.subheader("📊 Standard HTA-Struktur")
        st.info("💡 Dieses Dossier verwendet die Standard-Struktur. Für erweiterte Template-Features erstellen Sie ein neues Dossier mit Template-Auswahl.")
        
        # Get or initialize sections
        sections = dossier.get('sections', {})
        
        # Ensure all sections exist
        for section_key in VALUE_DOSSIER_SECTIONS.keys():
            if section_key not in sections:
                sections[section_key] = {
                    "documents": [],
                    "notes": "",
                    "completion_status": "Nicht begonnen",
                    "content": ""
                }
        
        # Create tabs for all sections
        section_tabs = st.tabs([
            f"{VALUE_DOSSIER_SECTIONS[key]['icon']} {VALUE_DOSSIER_SECTIONS[key]['title'].split('.', 1)[1].strip()}"
            for key in VALUE_DOSSIER_SECTIONS.keys()
        ])
        
        for i, (section_key, section_info) in enumerate(VALUE_DOSSIER_SECTIONS.items()):
            with section_tabs[i]:
                render_section_detail(
                    section_key, 
                    section_info, 
                    sections.get(section_key, {}), 
                    dossier_id, 
                    editable
                )


def render_section_detail(section_key: str, section_info: Dict[str, Any], 
                         section_data: Dict[str, Any], dossier_id: str, editable: bool) -> None:
    """Render detailed view of a single HTA section."""
    
    st.markdown(f"## {section_info['icon']} {section_info['title']}")
    st.markdown(f"**Beschreibung:** {section_info['description']}")
    
    # Completion status indicator
    status = section_data.get('completion_status', 'Nicht begonnen')
    status_colors = {
        'Nicht begonnen': 'red',
        'In Bearbeitung': 'orange', 
        'Review': 'blue',
        'Abgeschlossen': 'green'
    }
    status_color = status_colors.get(status, 'gray')
    st.markdown(f"**Status:** :{status_color}[{status}]")
    
    st.divider()
    
    # Content section
    if editable:
        st.subheader("📝 Inhalt")
        content = st.text_area(
            "Sektionsinhalt",
            value=section_data.get('content', ''),
            height=200,
            help="Detaillierter Inhalt für diese Sektion",
            key=f"content_{section_key}_{dossier_id}"
        )
        
        # Update status based on content
        status_options = ['Nicht begonnen', 'In Bearbeitung', 'Review', 'Abgeschlossen']
        current_status = section_data.get('completion_status', 'Nicht begonnen')
        new_status = st.selectbox(
            "Bearbeitungsstatus",
            options=status_options,
            index=status_options.index(current_status) if current_status in status_options else 0,
            key=f"status_{section_key}_{dossier_id}"
        )
        
        # Save section content
        if st.button(f"💾 {section_info['title']} speichern", key=f"save_{section_key}_{dossier_id}"):
            update_section_content(dossier_id, section_key, content, new_status)
    else:
        # Read-only content view
        content = section_data.get('content', '')
        if content:
            st.subheader("📝 Inhalt")
            st.markdown(content)
        else:
            st.info("Noch kein Inhalt vorhanden")
    
    st.divider()
    
    # Documents section
    st.subheader("📄 Zugeordnete Dokumente")
    documents = section_data.get('documents', [])
    
    if documents:
        for i, doc in enumerate(documents):
            with st.expander(f"📄 {doc.get('name', 'Unbekanntes Dokument')}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Typ:** {doc.get('type', 'N/A')}")
                    st.write(f"**Größe:** {doc.get('size', 0):,} bytes")
                    st.write(f"**Upload-Datum:** {doc.get('upload_date', 'N/A')}")
                
                with col2:
                    if st.button("📥 Download", key=f"download_{section_key}_{i}_{dossier_id}"):
                        download_document(doc)
                    
                    if editable and st.button("🗑️ Entfernen", key=f"remove_doc_{section_key}_{i}_{dossier_id}"):
                        remove_document_from_section(dossier_id, section_key, i)
                        st.rerun()
    else:
        st.info("Keine Dokumente zugeordnet")
    
    # Add document functionality (only in edit mode)
    if editable:
        st.divider()
        
        with st.expander(f"📤 Dokument zu {section_info['title']} hinzufügen", expanded=False):
            uploaded_file = st.file_uploader(
                "Dokument auswählen",
                type=['pdf', 'docx', 'doc', 'txt', 'md', 'xlsx', 'pptx'],
                key=f"upload_{section_key}_{dossier_id}"
            )
            
            if uploaded_file and st.button(f"➕ Hinzufügen", key=f"add_doc_{section_key}_{dossier_id}"):
                add_document_to_section_direct(dossier_id, section_key, uploaded_file)
                st.rerun()
    
    # Notes section
    st.divider()
    st.subheader("📝 Notizen")
    
    if editable:
        notes = st.text_area(
            "Sektionsnotizen",
            value=section_data.get('notes', ''),
            height=100,
            help="Zusätzliche Notizen und Kommentare zu dieser Sektion",
            key=f"notes_{section_key}_{dossier_id}"
        )
        
        if st.button(f"💾 Notizen speichern", key=f"save_notes_{section_key}_{dossier_id}"):
            update_section_notes(dossier_id, section_key, notes)
    else:
        notes = section_data.get('notes', '')
        if notes:
            st.markdown(notes)
        else:
            st.info("Keine Notizen vorhanden")


def update_basic_info(dossier_id: str, title: str, product_name: str, indication: str, 
                     company: str, status: str, priority: str, hta_agency: str, 
                     target_date: Optional[str], description: str) -> None:
    """Update basic dossier information."""
    
    try:
        dossiers = get_session_data("dossiers", {})
        
        if dossier_id in dossiers:
            dossiers[dossier_id].update({
                'title': title,
                'product_name': product_name,
                'indication': indication,
                'company': company,
                'status': status,
                'priority': priority,
                'hta_agency': hta_agency,
                'target_date': target_date,
                'description': description,
                'modified_date': datetime.now().isoformat()
            })
            
            set_session_data("dossiers", dossiers)
            st.success("✅ Grundinformationen erfolgreich aktualisiert!")
    
    except Exception as e:
        st.error(f"❌ Fehler beim Aktualisieren: {str(e)}")


def update_section_content(dossier_id: str, section_key: str, content: str, status: str) -> None:
    """Update section content and status."""
    
    try:
        dossiers = get_session_data("dossiers", {})
        
        if dossier_id in dossiers:
            if 'sections' not in dossiers[dossier_id]:
                dossiers[dossier_id]['sections'] = {}
            
            if section_key not in dossiers[dossier_id]['sections']:
                dossiers[dossier_id]['sections'][section_key] = {
                    'documents': [],
                    'notes': '',
                    'completion_status': 'Nicht begonnen',
                    'content': ''
                }
            
            dossiers[dossier_id]['sections'][section_key]['content'] = content
            dossiers[dossier_id]['sections'][section_key]['completion_status'] = status
            dossiers[dossier_id]['modified_date'] = datetime.now().isoformat()
            
            set_session_data("dossiers", dossiers)
            st.success(f"✅ {VALUE_DOSSIER_SECTIONS[section_key]['title']} erfolgreich gespeichert!")
    
    except Exception as e:
        st.error(f"❌ Fehler beim Speichern: {str(e)}")


def update_section_notes(dossier_id: str, section_key: str, notes: str) -> None:
    """Update section notes."""
    
    try:
        dossiers = get_session_data("dossiers", {})
        
        if dossier_id in dossiers:
            if 'sections' not in dossiers[dossier_id]:
                dossiers[dossier_id]['sections'] = {}
            
            if section_key not in dossiers[dossier_id]['sections']:
                dossiers[dossier_id]['sections'][section_key] = {
                    'documents': [],
                    'notes': '',
                    'completion_status': 'Nicht begonnen',
                    'content': ''
                }
            
            dossiers[dossier_id]['sections'][section_key]['notes'] = notes
            dossiers[dossier_id]['modified_date'] = datetime.now().isoformat()
            
            set_session_data("dossiers", dossiers)
            st.success("✅ Notizen erfolgreich gespeichert!")
    
    except Exception as e:
        st.error(f"❌ Fehler beim Speichern der Notizen: {str(e)}")


def add_document_to_section_direct(dossier_id: str, section_key: str, uploaded_file) -> None:
    """Add document directly to a section."""
    
    try:
        # Store file data
        file_content = uploaded_file.read()
        file_data = {
            "name": uploaded_file.name,
            "type": uploaded_file.type,
            "size": uploaded_file.size,
            "content": base64.b64encode(file_content).decode(),
            "upload_date": datetime.now().isoformat()
        }
        
        dossiers = get_session_data("dossiers", {})
        
        if dossier_id in dossiers:
            if 'sections' not in dossiers[dossier_id]:
                dossiers[dossier_id]['sections'] = {}
            
            if section_key not in dossiers[dossier_id]['sections']:
                dossiers[dossier_id]['sections'][section_key] = {
                    'documents': [],
                    'notes': '',
                    'completion_status': 'Nicht begonnen',
                    'content': ''
                }
            
            dossiers[dossier_id]['sections'][section_key]['documents'].append(file_data)
            if dossiers[dossier_id]['sections'][section_key]['completion_status'] == 'Nicht begonnen':
                dossiers[dossier_id]['sections'][section_key]['completion_status'] = 'In Bearbeitung'
            
            dossiers[dossier_id]['modified_date'] = datetime.now().isoformat()
            
            set_session_data("dossiers", dossiers)
            st.success(f"✅ Dokument erfolgreich zu {VALUE_DOSSIER_SECTIONS[section_key]['title']} hinzugefügt!")
    
    except Exception as e:
        st.error(f"❌ Fehler beim Hinzufügen des Dokuments: {str(e)}")


def remove_document_from_section(dossier_id: str, section_key: str, doc_index: int) -> None:
    """Remove a document from a section."""
    
    try:
        dossiers = get_session_data("dossiers", {})
        
        if (dossier_id in dossiers and 
            'sections' in dossiers[dossier_id] and 
            section_key in dossiers[dossier_id]['sections']):
            
            documents = dossiers[dossier_id]['sections'][section_key]['documents']
            
            if 0 <= doc_index < len(documents):
                removed_doc = documents.pop(doc_index)
                dossiers[dossier_id]['modified_date'] = datetime.now().isoformat()
                
                # Update completion status if no documents left
                if not documents and not dossiers[dossier_id]['sections'][section_key].get('content'):
                    dossiers[dossier_id]['sections'][section_key]['completion_status'] = 'Nicht begonnen'
                
                set_session_data("dossiers", dossiers)
                st.success(f"✅ Dokument '{removed_doc.get('name', 'Unbekannt')}' entfernt!")
    
    except Exception as e:
        st.error(f"❌ Fehler beim Entfernen des Dokuments: {str(e)}")


def download_document(doc: Dict[str, Any]) -> None:
    """Provide document download functionality."""
    
    try:
        file_content = base64.b64decode(doc.get('content', ''))
        
        st.download_button(
            label=f"💾 {doc.get('name', 'document')} herunterladen",
            data=file_content,
            file_name=doc.get('name', 'document'),
            mime=doc.get('type', 'application/octet-stream')
        )
    
    except Exception as e:
        st.error(f"❌ Fehler beim Download: {str(e)}")


def save_dossier_changes(dossier_id: str) -> None:
    """Save all pending changes to the dossier."""
    
    try:
        dossiers = get_session_data("dossiers", {})
        
        if dossier_id in dossiers:
            dossiers[dossier_id]['modified_date'] = datetime.now().isoformat()
            set_session_data("dossiers", dossiers)
            show_success_message("✅ Alle Änderungen erfolgreich gespeichert!")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Speichern: {str(e)}")
