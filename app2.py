import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import PyPDF2
from docx import Document

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Simple Doc Q&A", layout="centered")

st.title("Document Q&A")
st.write("Upload TXT, PDF, or DOCX files and ask questions.")

def extract_text(file):
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    if file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)

    return None


if "documents" not in st.session_state:
    st.session_state.documents = {}

uploaded_files = st.file_uploader(
    "Upload files",
    type=["txt", "pdf", "docx"],
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        content = extract_text(file)
        if content:
            st.session_state.documents[file.name] = content
    st.success("Files uploaded successfully")

doc_names = list(st.session_state.documents.keys())

if doc_names:
    selected_doc = st.selectbox("Select a document", doc_names)
else:
    selected_doc = None
    st.warning("Upload at least one document")

question = st.text_input("Enter your question")

if st.button("Get Answer"):
    if not GROQ_API_KEY:
        st.error("API key not found")
    elif not selected_doc:
        st.warning("Select a document")
    elif not question.strip():
        st.warning("Enter a question")
    else:
        document_text = st.session_state.documents[selected_doc]

        prompt = f"""
Answer the question using only the document below.
If the answer is not in the document, say "I don't know."

Document:
{document_text}

Question:
{question}
"""

        try:
            with st.spinner("Generating answer..."):
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )

            answer = response.choices[0].message.content
            st.subheader("Answer")
            st.write(answer)

        except Exception as e:
            st.error(str(e))
