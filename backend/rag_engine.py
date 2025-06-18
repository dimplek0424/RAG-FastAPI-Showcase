# Imports for working with PDF, text splitting, embedding, and retrieval
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # Make sure this is at the top if using a .env file

def get_vectorstore_from_chunks(chunks):
    try:
        # 🔐 Check API key is accessible
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found. Please set it as an environment variable or in .env file.")

        # ✅ Create embedding model (this is where error occurs if key is bad or credits are exhausted)
        embeddings = OpenAIEmbeddings(openai_api_key=api_key)

        # Build vectorstore from chunks
        from langchain_community.vectorstores import Chroma
        vectorstore = Chroma.from_documents(chunks, embeddings)

        return vectorstore

    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        raise  # Reraise to let FastAPI handler show it in /upload

# ---------------------------
# Function: Load & Split PDF
# ---------------------------
def load_and_split_pdf(pdf_path):
    """
    Loads a PDF file and splits its text content into chunks for embedding.
    """
    try:
        # Load PDF using LangChain's PyPDFLoader
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # Use RecursiveCharacterTextSplitter to break text into overlapping chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,      # Each chunk contains ~800 characters
            chunk_overlap=100     # Overlapping helps retain context
        )

        # Split the documents into chunks
        chunks = text_splitter.split_documents(documents)
        return chunks

    except Exception as e:
        print(f"❌ Error loading/splitting PDF: {e}")
        return []


# ------------------------------------
# Function: Create Vector Store Index
# ------------------------------------
def get_vectorstore_from_chunks(chunks):
    """
    Converts text chunks into vector embeddings and stores them in a Chroma vector store.
    """
    try:
        # Use OpenAI's embedding model to embed the chunks
        embeddings = OpenAIEmbeddings()

        # Store the embedded chunks in Chroma vector database
        vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
        return vectorstore

    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        raise e


# ---------------------------------------
# Function: Create RetrievalQA (RAG) Chain
# ---------------------------------------
def create_rag_chain(vectorstore):
    """
    Builds a Retrieval-Augmented Generation (RAG) chain using the given vectorstore,
    GPT-4 model, and a custom prompt template for better structured answers.
    """
    try:
        # Set up retriever to fetch top 20 relevant document chunks for any query
        retriever = vectorstore.as_retriever(search_kwargs={"k": 20})

        # Initialize the GPT-4 model with low temperature for deterministic responses
        llm = ChatOpenAI(temperature=0, model_name="gpt-4")

        # Create a custom prompt to guide the language model for clear, list-style answers
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
        You are a helpful assistant. Use ONLY the context below to answer the question.

        If the question asks to list strategies, tips, or points, include **all complete items** found in the context and number them clearly.

        Do NOT answer if the context does not provide full details.

        Context:
        {context}

        Question:
        {question}

        Answer:
        """
        )

        # Combine everything into a RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # Stuff = combine all context chunks into one prompt
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt_template},
            return_source_documents=True  # Change to True to return docs with the answer
        )

        return qa_chain

    except Exception as e:
        print(f"❌ Error creating RAG chain: {e}")
        raise e