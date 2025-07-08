"""
Value Dossier Structure component for HTA-compliant dossiers.

Implements the standard HTA structure with document upload and assignment functionality.
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import io
import base64

from utils.session_state import (
    get_session_data, 
    set_session_data, 
    show_success_message
)
from components.template_management import get_all_templates, get_template_by_id


# HTA-compliant Value Dossier Structure
VALUE_DOSSIER_SECTIONS = {
    "executive_summary": {
        "title": "1. Executive Summary",
        "description": "Kurzzusammenfassung der wichtigsten Aussagen zu Wirksamkeit, Sicherheit, Kosten-Nutzen, Preisgestaltung etc.",
        "icon": "📋"
    },
    "disease_background": {
        "title": "2. Disease Background", 
        "description": "Krankheitsbeschreibung, Epidemiologie, Krankheitslast (Burden of Disease), Aktuelle Therapie-Landschaft",
        "icon": "🏥"
    },
    "unmet_medical_need": {
        "title": "3. Unmet Medical Need",
        "description": "Unerfüllter medizinischer Bedarf, Limitationen der bisherigen Therapieoptionen",
        "icon": "🚧"
    },
    "product_profile": {
        "title": "4. Produktprofil / Clinical Profile",
        "description": "Wirkmechanismus, Indikation(en), Klinische Studien (Design, Population, Endpunkte, Ergebnisse), Vergleich zur Standardtherapie",
        "icon": "🔬"
    },
    "health_economic_evidence": {
        "title": "5. Health Economic Evidence",
        "description": "Kosten-Nutzen-Analysen, Budget Impact Modellierungen, Lebensqualitätsdaten (z. B. QALYs, EQ-5D)",
        "icon": "💰"
    },
    "patient_perspective": {
        "title": "6. Patient Perspective",
        "description": "Patient Reported Outcomes (PROs), Adhärenz, Zufriedenheit, Lebensqualität",
        "icon": "👥"
    },
    "value_proposition": {
        "title": "7. Value Proposition",
        "description": "Zusammenfassende Nutzenargumentation ('Why should this product be reimbursed / funded?')",
        "icon": "💡"
    },
    "supporting_materials": {
        "title": "8. Supporting Materials",
        "description": "Publikationen, Modellierungen, Referenzen, Literaturquellen",
        "icon": "📚"
    }
}


def render() -> None:
    """Render the Value Dossier Structure page."""
    
    st.header("📊 Value Dossier Structure (HTA-compliant)")
    
    # Info about HTA compliance
    with st.expander("ℹ️ HTA-Standards Info", expanded=False):
        st.markdown("""
        **HTA-konforme Value Dossier Struktur**
        
        Diese Struktur orientiert sich an den Anforderungen von HTA-Behörden wie:
        - **NICE** (UK)
        - **IQWiG/G-BA** (Deutschland)  
        - **HAS** (Frankreich)
        - Andere internationale HTA-Organisationen
        
        Die 8 Hauptsektionen decken alle wesentlichen Bereiche für die Bewertung medizinischer Technologien ab.
        """)
    
    # Main functionality tabs
    tab1, tab2, tab3 = st.tabs([
        "📤 Upload & Create", 
        "📋 Structure Overview", 
        "🗂️ Manage Sections"
    ])
    
    with tab1:
        render_upload_create_dossier()
    
    with tab2:
        render_structure_overview()
    
    with tab3:
        render_section_management()


def render_upload_create_dossier() -> None:
    """Render the upload and create dossier functionality."""
    
    st.subheader("📤 Neues Dossier basierend auf hochgeladenem Dokument")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Basis-Dokument hochladen",
        type=['pdf', 'docx', 'doc', 'txt', 'md'],
        help="Laden Sie ein bestehendes Dokument hoch, um darauf basierend ein neues Value Dossier zu erstellen."
    )
    
    if uploaded_file is not None:
        # Display file info
        st.success(f"✅ Datei hochgeladen: **{uploaded_file.name}**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Dateigröße:** {uploaded_file.size:,} bytes")
            st.write(f"**Dateityp:** {uploaded_file.type}")
        
        with col2:
            if st.button("📄 Vorschau anzeigen", key="preview_btn"):
                show_document_preview(uploaded_file)
        
        st.divider()
        
        # Template selection
        available_templates = get_all_templates()
        
        if available_templates:
            st.subheader("🗂️ Template auswählen")
            
            template_options = {"Standard HTA": "hta_standard"}
            for template_id, template in available_templates.items():
                template_options[template.get('name', 'Unbenannt')] = template_id
            
            selected_template_name = st.selectbox(
                "Dossier-Template",
                options=list(template_options.keys()),
                help="Wählen Sie eine Vorlage für die Dossier-Struktur"
            )
            
            selected_template_id = template_options[selected_template_name]
            selected_template = get_template_by_id(selected_template_id)
            
            if selected_template:
                with st.expander(f"👁️ Template-Vorschau: {selected_template.get('name', 'Unbenannt')}", expanded=False):
                    st.write(f"**Beschreibung:** {selected_template.get('description', 'N/A')}")
                    st.write(f"**Kategorie:** {selected_template.get('category', 'N/A')}")
                    
                    sections = selected_template.get('sections', {})
                    if sections:
                        st.write(f"**Sektionen ({len(sections)}):**")
                        sorted_sections = sorted(sections.items(), key=lambda x: x[1].get('order', 999))
                        
                        for section_id, section in sorted_sections:
                            required_icon = "✅" if section.get('required', False) else "⭕"
                            st.write(f"  {section.get('icon', '📄')} **{section.get('title', 'Unbenannt')}** {required_icon}")
        else:
            selected_template_id = "hta_standard"
            st.info("💡 Verwende Standard HTA-Template")
        
        # Create dossier form
        with st.form("create_dossier_form"):
            st.subheader("📋 Neues Value Dossier erstellen")
            
            col1, col2 = st.columns(2)
            
            with col1:
                dossier_title = st.text_input(
                    "Dossier Titel*",
                    value=f"Value Dossier - {uploaded_file.name.split('.')[0]}",
                    help="Haupttitel des Value Dossiers"
                )
                
                product_name = st.text_input(
                    "Produktname*",
                    help="Name der medizinischen Technologie/des Produkts"
                )
                
                indication = st.text_input(
                    "Indikation",
                    help="Medizinische Indikation"
                )
            
            with col2:
                company = st.text_input(
                    "Unternehmen",
                    help="Herstellendes/antragstellendes Unternehmen"
                )
                
                hta_agency = st.selectbox(
                    "Ziel-HTA-Behörde",
                    options=[
                        "IQWiG/G-BA (Deutschland)",
                        "NICE (UK)", 
                        "HAS (Frankreich)",
                        "AIFA (Italien)",
                        "TLV (Schweden)",
                        "Andere"
                    ],
                    help="Primäre HTA-Behörde für die Bewertung"
                )
                
                priority = st.selectbox(
                    "Priorität",
                    options=["Hoch", "Mittel", "Niedrig"],
                    index=1
                )
            
            # Section assignment
            st.subheader("📂 Dokument-Sektion zuweisen")
            
            primary_section = st.selectbox(
                "Primäre Sektion",
                options=list(VALUE_DOSSIER_SECTIONS.keys()),
                format_func=lambda x: f"{VALUE_DOSSIER_SECTIONS[x]['icon']} {VALUE_DOSSIER_SECTIONS[x]['title']}",
                help="Hauptsektion, der das hochgeladene Dokument zugeordnet wird"
            )
            
            # Additional sections (multi-select)
            additional_sections = st.multiselect(
                "Zusätzliche relevante Sektionen",
                options=[k for k in VALUE_DOSSIER_SECTIONS.keys() if k != primary_section],
                format_func=lambda x: f"{VALUE_DOSSIER_SECTIONS[x]['icon']} {VALUE_DOSSIER_SECTIONS[x]['title']}",
                help="Weitere Sektionen, für die dieses Dokument relevant ist"
            )
            
            # Description/Notes
            notes = st.text_area(
                "Beschreibung/Notizen",
                help="Zusätzliche Informationen zum Dokument und Dossier"
            )
            
            submitted = st.form_submit_button("🚀 Value Dossier erstellen", type="primary")
            
            if submitted:
                if not dossier_title or not product_name:
                    st.error("❌ Bitte füllen Sie alle Pflichtfelder (*) aus.")
                else:
                    create_dossier_from_upload(
                        uploaded_file=uploaded_file,
                        dossier_title=dossier_title,
                        product_name=product_name,
                        indication=indication,
                        company=company,
                        hta_agency=hta_agency,
                        priority=priority,
                        primary_section=primary_section,
                        additional_sections=additional_sections,
                        notes=notes,
                        selected_template_id=selected_template_id
                    )


def render_structure_overview() -> None:
    """Render the Value Dossier structure overview."""
    
    st.subheader("📋 HTA-konforme Value Dossier Struktur")
    
    for section_key, section_info in VALUE_DOSSIER_SECTIONS.items():
        with st.expander(f"{section_info['icon']} {section_info['title']}", expanded=False):
            st.markdown(f"**Beschreibung:** {section_info['description']}")
            
            # Show assigned documents for this section
            show_section_documents(section_key)
            
            # Option to upload documents directly to this section
            if st.button(f"📤 Dokument zu {section_info['title']} hinzufügen", key=f"upload_{section_key}"):
                st.session_state[f"show_upload_{section_key}"] = True
            
            if st.session_state.get(f"show_upload_{section_key}", False):
                upload_to_section(section_key, section_info['title'])


def render_section_management() -> None:
    """Render section management functionality."""
    
    st.subheader("🗂️ Sektions-Management")
    
    dossiers = get_session_data("dossiers", {})
    
    if not dossiers:
        st.info("📭 Noch keine Dossiers vorhanden. Erstellen Sie zuerst ein Dossier.")
        return
    
    # Select dossier
    selected_dossier_id = st.selectbox(
        "Dossier auswählen",
        options=list(dossiers.keys()),
        format_func=lambda x: f"{dossiers[x].get('title', 'Unbenannt')} ({dossiers[x].get('product_name', 'N/A')})"
    )
    
    if selected_dossier_id:
        dossier = dossiers[selected_dossier_id]
        
        st.subheader(f"📊 {dossier.get('title', 'Unbenanntes Dossier')}")
        
        # Show sections with documents
        sections = dossier.get('sections', {})
        
        for section_key, section_info in VALUE_DOSSIER_SECTIONS.items():
            with st.container():
                st.markdown(f"### {section_info['icon']} {section_info['title']}")
                
                section_data = sections.get(section_key, {})
                documents = section_data.get('documents', [])
                
                if documents:
                    st.write(f"**{len(documents)} Dokument(e) zugewiesen:**")
                    for i, doc in enumerate(documents):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"📄 {doc.get('name', 'Unbekannt')}")
                        
                        with col2:
                            if st.button("👁️", key=f"view_{section_key}_{i}", help="Anzeigen"):
                                st.session_state[f"show_doc_{section_key}_{i}"] = True
                        
                        with col3:
                            if st.button("🗑️", key=f"delete_{section_key}_{i}", help="Löschen"):
                                remove_document_from_section(selected_dossier_id, section_key, i)
                                st.rerun()
                else:
                    st.info("Keine Dokumente zugewiesen")
                
                st.divider()


def show_document_preview(uploaded_file) -> None:
    """Show a preview of the uploaded document."""
    
    try:
        # Read file content based on type
        if uploaded_file.type == "text/plain":
            content = str(uploaded_file.read(), "utf-8")
            st.text_area("Dokumentvorschau", content, height=300, disabled=True)
        
        elif uploaded_file.type == "application/pdf":
            st.info("📄 PDF-Datei erkannt. Vollständige Vorschau wird nach der Verarbeitung verfügbar sein.")
            
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            st.info("📝 Word-Dokument erkannt. Vollständige Vorschau wird nach der Verarbeitung verfügbar sein.")
            
        else:
            st.info(f"Datei vom Typ {uploaded_file.type} hochgeladen. Vorschau nach Verarbeitung verfügbar.")
    
    except Exception as e:
        st.error(f"Fehler beim Laden der Vorschau: {str(e)}")


def create_dossier_from_upload(
    uploaded_file,
    dossier_title: str,
    product_name: str,
    indication: str,
    company: str,
    hta_agency: str,
    priority: str,
    primary_section: str,
    additional_sections: List[str],
    notes: str,
    selected_template_id: str = "hta_standard"
) -> None:
    """Create a new dossier based on uploaded document and selected template."""
    
    try:
        # Generate unique ID
        dossier_id = str(uuid.uuid4())
        
        # Store file content
        file_content = uploaded_file.read()
        file_data = {
            "name": uploaded_file.name,
            "type": uploaded_file.type,
            "size": uploaded_file.size,
            "content": base64.b64encode(file_content).decode(),
            "upload_date": datetime.now().isoformat()
        }
        
        # Get selected template
        selected_template = get_template_by_id(selected_template_id)
        template_sections = selected_template.get('sections', VALUE_DOSSIER_SECTIONS) if selected_template else VALUE_DOSSIER_SECTIONS
        
        # Create dossier structure
        dossier_data = {
            "id": dossier_id,
            "title": dossier_title,
            "product_name": product_name,
            "indication": indication,
            "company": company,
            "hta_agency": hta_agency,
            "priority": priority,
            "status": "In Bearbeitung",
            "created_date": datetime.now().isoformat(),
            "modified_date": datetime.now().isoformat(),
            "notes": notes,
            "template_id": selected_template_id,
            "template_name": selected_template.get('name', 'Standard HTA') if selected_template else 'Standard HTA',
            "sections": {}
        }
        
        # Initialize all sections based on template
        for section_key, section_info in template_sections.items():
            dossier_data["sections"][section_key] = {
                "title": section_info.get('title', 'Unbenannt'),
                "description": section_info.get('description', ''),
                "icon": section_info.get('icon', '📄'),
                "required": section_info.get('required', False),
                "order": section_info.get('order', 999),
                "documents": [],
                "content": "",
                "notes": "",
                "completion_status": "Nicht begonnen"
            }
        
        # Assign uploaded document to primary section
        dossier_data["sections"][primary_section]["documents"].append(file_data)
        dossier_data["sections"][primary_section]["completion_status"] = "In Bearbeitung"
        
        # Assign to additional sections if specified
        for section_key in additional_sections:
            dossier_data["sections"][section_key]["documents"].append(file_data.copy())
            dossier_data["sections"][section_key]["completion_status"] = "In Bearbeitung"
        
        # Save to session state
        dossiers = get_session_data("dossiers", {})
        dossiers[dossier_id] = dossier_data
        set_session_data("dossiers", dossiers)
        
        # Success message
        show_success_message(f"✅ Value Dossier '{dossier_title}' erfolgreich erstellt!")
        
        st.success(f"""
        🎉 **Dossier erfolgreich erstellt!**
        
        **Titel:** {dossier_title}  
        **Produkt:** {product_name}  
        **Dokument zugewiesen zu:** {VALUE_DOSSIER_SECTIONS[primary_section]['title']}  
        {f"**Zusätzliche Sektionen:** {', '.join([VALUE_DOSSIER_SECTIONS[s]['title'] for s in additional_sections])}" if additional_sections else ""}
        """)
        
        if st.button("📋 Zum Dossier wechseln"):
            st.session_state["current_page"] = "dossier_management"
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Fehler beim Erstellen des Dossiers: {str(e)}")


def show_section_documents(section_key: str) -> None:
    """Show documents assigned to a specific section across all dossiers."""
    
    dossiers = get_session_data("dossiers", {})
    section_docs = []
    
    for dossier_id, dossier in dossiers.items():
        sections = dossier.get("sections", {})
        if section_key in sections:
            documents = sections[section_key].get("documents", [])
            for doc in documents:
                section_docs.append({
                    "dossier_title": dossier.get("title", "Unbenannt"),
                    "dossier_id": dossier_id,
                    "document": doc
                })
    
    if section_docs:
        st.write(f"**{len(section_docs)} Dokument(e) in dieser Sektion:**")
        for i, item in enumerate(section_docs):
            st.write(f"• 📄 {item['document'].get('name', 'Unbekannt')} (aus: {item['dossier_title']})")
    else:
        st.info("Noch keine Dokumente in dieser Sektion")


def upload_to_section(section_key: str, section_title: str) -> None:
    """Allow direct upload to a specific section."""
    
    uploaded_file = st.file_uploader(
        f"Dokument zu {section_title} hinzufügen",
        type=['pdf', 'docx', 'doc', 'txt', 'md'],
        key=f"section_upload_{section_key}"
    )
    
    if uploaded_file:
        dossiers = get_session_data("dossiers", {})
        
        if dossiers:
            selected_dossier = st.selectbox(
                "Dossier auswählen",
                options=list(dossiers.keys()),
                format_func=lambda x: f"{dossiers[x].get('title', 'Unbenannt')}",
                key=f"select_dossier_{section_key}"
            )
            
            if st.button(f"➕ Zu {section_title} hinzufügen", key=f"add_to_{section_key}"):
                add_document_to_section(selected_dossier, section_key, uploaded_file)
                st.session_state[f"show_upload_{section_key}"] = False
                st.rerun()
        else:
            st.warning("Kein Dossier vorhanden. Erstellen Sie zuerst ein Dossier.")


def add_document_to_section(dossier_id: str, section_key: str, uploaded_file) -> None:
    """Add a document to a specific section of a dossier."""
    
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
        
        # Update dossier
        dossiers = get_session_data("dossiers", {})
        if dossier_id in dossiers:
            if "sections" not in dossiers[dossier_id]:
                dossiers[dossier_id]["sections"] = {}
            
            if section_key not in dossiers[dossier_id]["sections"]:
                dossiers[dossier_id]["sections"][section_key] = {
                    "documents": [],
                    "notes": "",
                    "completion_status": "Nicht begonnen"
                }
            
            dossiers[dossier_id]["sections"][section_key]["documents"].append(file_data)
            dossiers[dossier_id]["sections"][section_key]["completion_status"] = "In Bearbeitung"
            dossiers[dossier_id]["modified_date"] = datetime.now().isoformat()
            
            set_session_data("dossiers", dossiers)
            st.success(f"✅ Dokument zu {VALUE_DOSSIER_SECTIONS[section_key]['title']} hinzugefügt!")
    
    except Exception as e:
        st.error(f"❌ Fehler beim Hinzufügen des Dokuments: {str(e)}")


def remove_document_from_section(dossier_id: str, section_key: str, doc_index: int) -> None:
    """Remove a document from a section."""
    
    try:
        dossiers = get_session_data("dossiers", {})
        
        if (dossier_id in dossiers and 
            "sections" in dossiers[dossier_id] and 
            section_key in dossiers[dossier_id]["sections"]):
            
            documents = dossiers[dossier_id]["sections"][section_key]["documents"]
            
            if 0 <= doc_index < len(documents):
                removed_doc = documents.pop(doc_index)
                dossiers[dossier_id]["modified_date"] = datetime.now().isoformat()
                
                # Update completion status
                if not documents:
                    dossiers[dossier_id]["sections"][section_key]["completion_status"] = "Nicht begonnen"
                
                set_session_data("dossiers", dossiers)
                st.success(f"✅ Dokument '{removed_doc.get('name', 'Unbekannt')}' entfernt!")
    
    except Exception as e:
        st.error(f"❌ Fehler beim Entfernen des Dokuments: {str(e)}")
