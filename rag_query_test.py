from pinecone import Pinecone
from openai import OpenAI
import google.generativeai as genai
import os
from dotenv import load_dotenv


load_dotenv()

# Initialize clients
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=GOOGLE_API_KEY)
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

# Pinecone index
INDEX_NAME = "model-earth-jam-stack"
index = pinecone_client.Index(INDEX_NAME)

# Gemini model (free tier)
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to query RAG system
def query_rag(repo_name, question):
    namespace = repo_name.replace("/", "_")
    # Embed the question
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )
    query_vector = response.data[0].embedding

    # Query Pinecone for top-5 relevant chunks
    results = index.query(
        vector=query_vector,
        top_k=5,
        namespace=namespace,
        include_metadata=True
    )

    # Extract context from matches
    context = "\n\n".join(
        match["metadata"].get("content", "")
        for match in results["matches"]
        if match["metadata"].get("content")
    )

    if not context:
        return f"No relevant information found for {question} in {repo_name}."

    # Create prompt for Gemini
    prompt = f"""
    Question: {question}
    Context:
    {context}
    Answer the question based on the provided context. Be accurate.
    """

    # Call Gemini
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"

# Test queries
repo_name = "ModelEarth/localsite"
questions = [
    "can i get more context on this repo in like 5 lines . after the solution i need to undertsand the repo clearly?",
    "My skillset is in JS, HTML, CSS. Which TO DOs i need to work on this repo"
]

for question in questions:
    print(f"\n🔍 Query: {question}")
    answer = query_rag(repo_name, question)
    print(f"✅ Answer: {answer}")