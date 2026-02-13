import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

GROQ_API_KEY = "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"
MODEL_NAME = "openai/gpt-oss-20b"
# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Simple Doc Q&A", layout="centered")

st.title("📄 Simple Document Q&A")
st.write("Upload multiple text documents, select one, and ask a question.")

# -----------------------------
# Session storage
# -----------------------------
if "documents" not in st.session_state:
    st.session_state.documents = {}

# -----------------------------
# Upload Multiple Files
# -----------------------------
uploaded_files = st.file_uploader(
    "Upload .txt files",
    type=["txt"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        content = uploaded_file.read().decode("utf-8")
        st.session_state.documents[uploaded_file.name] = content

    st.success("Files uploaded successfully!")

# -----------------------------
# Select File
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
