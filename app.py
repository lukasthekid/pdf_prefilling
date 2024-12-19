import json
import os
import zipfile
import io
from datetime import datetime

import streamlit as st

from application.models.Person import Person
from application.service import load_mapping_config, render_pdf_fields, fill_pdf

# Ensure the contracts directory exists
DIRECTORY = "contracts"
if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

# Load customer data
with open("database/customer_data.json") as f:
    CUSTOMERS = json.load(f)

customer_names = [f"{c['first_name']} {c['last_name']}" for c in CUSTOMERS]

# Function to list PDF files in the contracts directory
def list_pdf_files(directory):
    pdf_files = []
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            full_path = os.path.join(directory, filename)
            if os.path.isfile(full_path):
                pdf_files.append(full_path)
    return pdf_files

# Initial listing of PDF files
pdf_files = list_pdf_files(DIRECTORY)

st.title("Generator")

# Sidebar for uploading PDF templates
st.sidebar.header("PDF Vorlagen upload")
uploaded_files = st.sidebar.file_uploader(
    "Hochladen",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = os.path.join(DIRECTORY, uploaded_file.name)
        # Save the uploaded PDF to the contracts directory
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"Hochladen von {len(uploaded_files)} PDFs erfolgreich!")
    # Refresh the list of PDF files after upload
    pdf_files = list_pdf_files(DIRECTORY)

# Main interface
st.header("Verträge Vorbefüllen")

# Customer selection
selected_name = st.selectbox("Bitte wählen Sie einen Kunden aus:", customer_names)

# PDF templates selection (multiselect)
selected_contracts = st.multiselect(
    "Vertragsvorlagen auswählen:",
    pdf_files,
    help="Select one or more PDF templates to prefill."
)

generate_btn = st.button("Vertrag vorbefüllen")

if generate_btn:
    if not selected_contracts:
        st.error("Please select at least one contract template.")
    else:
        # Get customer data
        customer: Person = None
        for c in CUSTOMERS:
            if f"{c['first_name']} {c['last_name']}" == selected_name:
                customer = Person.from_dict(c)
                break

        if not customer:
            st.error("Customer not found.")
        else:
            mapping = load_mapping_config("mapping.yaml")
            fields = render_pdf_fields(customer, mapping)

            # Create a BytesIO buffer for the ZIP file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for pdf_path in selected_contracts:
                    try:
                        filled_pdf = fill_pdf(pdf_path, fields)
                        # Extract the filename from the path
                        filename = os.path.basename(pdf_path)
                        # Define a name for the filled PDF
                        filled_filename = f"{datetime.now()}_{filename}"
                        # Write the filled PDF to the ZIP
                        zipf.writestr(filled_filename, filled_pdf.read())
                        filled_pdf.close()
                    except Exception as e:
                        st.error(f"Error processing {pdf_path}: {e}")

            zip_buffer.seek(0)

            # Provide a download button for the ZIP file
            st.download_button(
                label="Alle Verträge als ZIP herunterladen",
                data=zip_buffer,
                file_name=f"vertraege_{datetime.now()}.zip",
                mime="application/zip"
            )