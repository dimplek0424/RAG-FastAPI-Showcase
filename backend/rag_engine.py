# LangChain Community - RECOMMENDED
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOpenAI

# LangChain Core and Chains
from langchain_core.prompts import PromptTemplate
#from langchain_core.chains.retrieval_qa import RetrievalQA

import sys
print(sys.path)
# Then your imports
from langchain.chains import RetrievalQA

# Core imports
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
        llm = ChatOpenAI(temperature=0.3, model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))

        # ✅ Prompt template for list-style, contextual answers
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are a helpful and concise assistant. Use ONLY the context below to answer the question.

If the question asks for strategies, tips, or steps:
- Extract and list all specific strategies mentioned.
- If the user asks for a subset (e.g., top 3), pick the most actionable or impactful ones based on the context.
- Number the items clearly and quote phrases or sentences if helpful.

If the question is vague, do your best to summarize relevant insights from the document.

Only use information from the context. Do not invent or assume.

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
