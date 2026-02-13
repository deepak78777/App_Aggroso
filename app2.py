import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import PyPDF2
from docx import Document

# Load environment variables
load_dotenv()

GROQ_API_KEY = "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"
MODEL_NAME = "openai/gpt-oss-20b"

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Simple Doc Q&A", layout="centered")

st.title("📄 Simple Document Q&A")
st.write("Upload TXT, PDF, or DOCX files. Select one and ask a question.")

# -----------------------------
# Helper function to extract text
# -----------------------------
def extract_text(file):
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    elif file.name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text

    elif file.name.endswith(".docx"):
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    else:
        return None

# -----------------------------
# Session storage
# -----------------------------
if "documents" not in st.session_state:
    st.session_state.documents = {}

# -----------------------------
# File Upload
# -----------------------------
uploaded_files = st.file_uploader(
    "Upload files",
    type=["txt", "pdf", "docx"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        text_content = extract_text(uploaded_file)

        if text_content:
            st.session_state.documents[uploaded_file.name] = text_content
        else:
            st.warning(f"Unsupported file type: {uploaded_file.name}")

    st.success("Files uploaded successfully!")

# -----------------------------
# File Selection
# -----------------------------
doc_names = list(st.session_state.documents.keys())

if doc_names:
    selected_doc = st.selectbox("Select a Document", doc_names)
    st.info(f"Currently selected: {selected_doc}")
else:
    selected_doc = None
    st.warning("Please upload at least one document.")

# -----------------------------
# Question Input
# -----------------------------
question = st.text_input("Enter your question")

# -----------------------------
# Get Answer
# -----------------------------
if st.button("Get Answer"):

    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY not found.")

    elif not selected_doc:
        st.warning("Please select a document.")

    elif not question.strip():
        st.warning("Please enter a question.")

    else:
        document_text = st.session_state.documents[selected_doc]

        prompt = f"""
You are a helpful assistant.
Answer the question ONLY using the document below.
If the answer is not found in the document, say "I don't know."

Document:
{document_text}

Question:
{question}
"""

        try:
            with st.spinner("Generating answer..."):
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )

                answer = response.choices[0].message.content

                st.subheader("Answer:")
                st.write(answer)

        except Exception as e:
            st.error(f"Error: {str(e)}")
