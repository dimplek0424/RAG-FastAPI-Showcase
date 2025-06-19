from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# ----------------------------------------
# Function: Create Vector Store Index
# ----------------------------------------
def get_vectorstore_from_chunks(chunks):
    """
    Converts text chunks into vector embeddings using OpenAI and stores them in a Chroma vector store.
    
    Args:
        chunks (List[Document]): List of LangChain Document chunks.
    
    Returns:
        Chroma: A vector store containing embedded chunks for retrieval.
    """
    try:
        # ✅ Ensure the OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY not found. Set it in your .env file or environment.")

        # ✅ Instantiate embedding model
        embeddings = OpenAIEmbeddings(openai_api_key=api_key)

        # ✅ Embed documents and create vector store
        vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)

        return vectorstore

    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        raise e

# ------------------------------------------------
# Function: Create Retrieval-Augmented QA Chain
# ------------------------------------------------
def create_rag_chain(vectorstore):
    """
    Builds a Retrieval-Augmented Generation (RAG) chain using the provided vectorstore and GPT-4.
    
    It uses a custom prompt to generate informative and structured answers based on retrieved content.
    
    Args:
        vectorstore (Chroma): The vector database containing embedded PDF chunks.
    
    Returns:
        RetrievalQA: A LangChain chain capable of answering questions using retrieval-augmented context.
    """
    try:
        # ✅ Use vectorstore to retrieve top 20 relevant chunks
        retriever = vectorstore.as_retriever(search_kwargs={"k": 20})

        # ✅ GPT-4 with low temperature for deterministic responses
        llm = ChatOpenAI(temperature=0, model_name="gpt-4")

        # ✅ Prompt template for list-style, contextual answers
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

        # ✅ Build RetrievalQA chain using the prompt
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt_template},
            return_source_documents=True
        )

        return qa_chain

    except Exception as e:
        print(f"❌ Error creating RAG chain: {e}")
        raise e
