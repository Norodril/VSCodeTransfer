#All the imports
import os
import ollama
import uuid
import json
import psycopg2
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
import fitz
import streamlit as st
import sys
print("PYTHON PATH:", sys.executable)

#loads environment variables from the .env file
load_dotenv()
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASS     = os.getenv("DB_PASS")
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = int(os.getenv("DB_PORT"))

EMBED_MODEL = os.getenv("EMBED_MODEL")
LLM_MODEL   = os.getenv("LLM_MODEL")
TABLE_DIM   = int(os.getenv("TABLE_DIM"))

#opens a connection to the PostgreSQL database
def get_db_connection():
    conn = psycopg2.connect(
        dbname   = DB_NAME,
        user     = DB_USER,
        password = DB_PASS,
        host     = DB_HOST,
        port     = DB_PORT
    )
    conn.autocommit = True
    return conn

#ensure the vector extension is installed
#creates a table called document_chunks with the columns
#1. chunk_id- chunk ID
#2. document_id- which PDF it came from
#3. text- the actual text
#4. metadata- extra info 
#5. embedding- the embedding vector
def ensure_schema():
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    register_vector(conn)
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS document_chunks (
      chunk_id    UUID PRIMARY KEY,
      document_id TEXT      NOT NULL,
      text        TEXT      NOT NULL,
      metadata    JSONB     NOT NULL,
      embedding   VECTOR({TABLE_DIM}) NOT NULL
    );
    """)
    cur.close()
    conn.close()

#opens a PDF
#extracts the text from each page
#returns all the text as one big string
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n\n"
    doc.close()
    return text

#splits the text into paragraphs based on double newlines
#removes any extra whitespace
def chunk_paragraphs(text):
    return [p.strip() for p in text.split("\n\n") if p.strip()]

#calls on ollama's embedding model to get the embeddings for the text
#returns the embedding (a list of numbers)
def get_embedding(text: str):
    resp = ollama.embeddings(model=EMBED_MODEL, prompt=text)
    return resp["embedding"]

#splits the PDF into paragraphs
#generates embeddings for each paragraph
#Inserts each chunk into PostgreSQL database
#returns how many paragraphs were stored
def store_document(document_id: str, text: str):
    conn = get_db_connection()
    cur  = conn.cursor()
    paras = chunk_paragraphs(text)
    for idx, para in enumerate(paras):
        emb = get_embedding(para)
        cur.execute("""
          INSERT INTO document_chunks (chunk_id, document_id, text, metadata, embedding)
          VALUES (%s, %s, %s, %s, %s)
          ON CONFLICT (chunk_id) DO NOTHING;
        """, (
          str(uuid.uuid4()),
          document_id,
          para,
          json.dumps({"chunk_index": idx}),
          emb
        ))
    conn.commit()
    cur.close()
    conn.close()
    return len(paras)

#Turns the query into an embedding
#Searches PostgreSQL using <-> operator to find the top N most similar chunks
#Gets the top N most similar chunks and returns them
def retrieve_similar(query: str, top_n: int = 5):
    q_emb = get_embedding(query)
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute(f"""
      SELECT text, metadata, embedding <-> %s::vector AS similarity
      FROM document_chunks
      ORDER BY similarity
      LIMIT %s;
    """, (q_emb, top_n))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

#Retrieves the most similar chunks for the question
#Creates a variable 'context' that contains the text of the most similar chunks
#Creates a prompt for the LLM that includes the context and the question
#Calls the LLM to generate and return the answer based on the prompt provided
def answer_question(question: str, top_n: int = 5):
    results = retrieve_similar(question, top_n)
    if not results:
        return " No context found for that question."
    context = "\n\n".join(r[0] for r in results)
    prompt  = (
        "You are a helpful assistant. "
        "Answer the question using ONLY the context below.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        "Answer:"
    )
    resp = ollama.generate(model=LLM_MODEL, prompt=prompt)
    return resp["response"].strip()

# Creates the streamlit web UI
# Uploads PDF and saves it as a temporaty file so fitz can read it
# Keeps the app organized, and streamlit will re-run main() every time you change something on the page
# The entire process of extracting the text, chunking it, and storing it is done through the main() function
def main():
    st.title("PDF Q&A with Ollama + PostgreSQL")

    ensure_schema()

    # Instead of typing the file path, the user uploads the PDF in their browser
    #We save it as a temporary file so the rest of the code can still use it
    pdf_file = st.file_uploader("Upload a PDF", type="pdf")
    if pdf_file:
        pdf_path = f"temp_{pdf_file.name}"
        with open(pdf_path, "wb") as f:
            f.write(pdf_file.read()) 
        with st.spinner("Extracting text from PDF..."): #Show status while extracting text
            pdf_text = extract_text_from_pdf(pdf_path) #uses the function to store the text in 'text' variable
        with st.spinner("Storing chunks and embeddings..."): #Shows status while storing data
        #Streamlit will not display the text directly in the terminal, but it will be used for storing and answering questions
            stored = store_document(document_id=pdf_file.name, text=pdf_text) #uses the function 'store_document' to embed and store the text
        st.success(f"Stored {stored} paragraphs from {pdf_file.name}")
        st.subheader("Document Summary")
        doc = fitz.open(pdf_path)
        st.write(f"Pages: {len(doc)}")
        st.write(f"Paragraphs stored: {stored}")
        st.write("Preview (first 500 characters):")
        st.text(pdf_text[:500]) #preview of the first 500 characters
        doc.close()
    # Instead of typing the question in the terminal, the user can type it in the browser and pick a number with a little widget
    question = st.text_input("Enter your question")
    top_n    = st.number_input("How many top-k chunks to retrieve?", min_value=1, max_value=10, value=5)

    # Now you click a button to get the answer and the answer will be displayed in the browser
    if st.button("Get Answer") and question:
        with st.spinner("Thinking..."):
            answer = answer_question(question, top_n=top_n)
        st.subheader("Answer")
        st.write(answer)

if __name__ == "__main__":
    main()



