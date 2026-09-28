import os
import requests
import streamlit as st
from config import BACKEND_URL, INVERSE_LOGO_PATH
from ai_core.generator import format_docx, format_pdf, format_html_preview, sanitize_text

st.set_page_config(page_title="LegalEase", layout="centered", page_icon="⚖️")

# UI Layout Title & Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists(INVERSE_LOGO_PATH):
        st.image(INVERSE_LOGO_PATH, use_container_width=True)

st.markdown("<h2 style='text-align: center;'>AI Legal Document Generator</h2>", unsafe_allow_html=True)

# User Form Inputs
document_type = st.text_input("Document Type (Ex: Agreement, Contract, NDA)", placeholder="Freelance Work Contract")
parties = st.text_area("Parties Involved", placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)")
terms = st.text_area("Terms & Conditions (Use semicolons for bullet points)", placeholder="Work must be delivered by May 15, 2025; Payment within 7 days of invoice;")
dates = st.text_input("Effective Date", placeholder="April 15, 2025")

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "show_edit" not in st.session_state:
    st.session_state.show_edit = False

if st.button("Generate Document"):
    if not document_type or not parties or not terms or not dates:
        st.error("Please fill out all input fields.")
    else:
        with st.spinner("Generating legal document via Gemini API..."):
            payload = {
                "document_type": document_type,
                "parties": parties,
                "terms": terms,
                "dates": dates
            }
            try:
                res = requests.post(f"{BACKEND_URL}/generate", json=payload)
                if res.status_code == 200:
                    st.session_state.generated_text = res.json().get("document", "")
                    st.session_state.show_edit = False
                    st.success("Document Generated Successfully!")
                else:
                    st.error(f"API Error ({res.status_code}): {res.json().get('detail')}")
            except Exception as e:
                st.error(f"Could not connect to FastAPI server at {BACKEND_URL}: {e}")

# Render Results & Download Controls
if st.session_state.generated_text:
    st.markdown("---")
    
    # Render Preview or Text Area
    if st.session_state.show_edit:
        edited_text = st.text_area("Edit Document Below:", st.session_state.generated_text, height=350)
        st.session_state.generated_text = edited_text
    else:
        styled_html = format_html_preview(st.session_state.generated_text)
        st.markdown(
            f"<div style='background-color: #1e1e1e; padding: 15px; border-radius: 8px; color: #ffffff;'>{styled_html}</div>",
            unsafe_allow_html=True
        )

    st.write("")
    
    # Toggle Edit Button
    if st.button("✏️ Click to Edit Document" if not st.session_state.show_edit else "✔️ Finish Editing"):
        st.session_state.show_edit = not st.session_state.show_edit
        st.rerun()

    st.write("")
    file_prefix = (document_type if document_type else "legal_document").replace(" ", "_").lower()

    # Formatted Downloads
    txt_data = st.session_state.generated_text
    st.download_button(
        label="📄 Download as .TXT",
        data=txt_data,
        file_name=f"{file_prefix}.txt",
        mime="text/plain"
    )

    docx_data = format_docx(st.session_state.generated_text, document_type or "Legal Document")
    st.download_button(
        label="📝 Download as .DOCX",
        data=docx_data,
        file_name=f"{file_prefix}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    pdf_data = format_pdf(st.session_state.generated_text, document_type or "Legal Document")
    st.download_button(
        label="📕 Download as .PDF",
        data=pdf_data,
        file_name=f"{file_prefix}.pdf",
        mime="application/pdf"
    )