# Importing  necessary libraries
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace, HuggingFacePipeline
from transformers import pipeline
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from youtube_transcript_api._errors import TranscriptsDisabled  # for catching errors
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()

def process_video(url: str):
    # Extract video ID
    video_id = url.split("v=")[-1]
    try:
        transcript_list = YouTubeTranscriptApi().fetch(video_id=video_id, languages=['en'])
        transcript = " ".join([d.text for d in transcript_list])
    except TranscriptsDisabled:
        raise ValueError("Transcript is disabled for this video.")
    
    # Split transcript
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcript])
    
    # Create embeddings and FAISS vector store
    embeddings = HuggingFaceEmbeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Return retriever
    return vector_store.as_retriever(search_type='similarity', search_kwargs={"k":4})

def chat_with_video(retriever, query: str):
    def format_docs(retrieved_docs):
        # Joins the retrieved context
        return "\n\n".join(doc.page_content for doc in retrieved_docs)
    
    # """Returns answer based on query & chat history."""

    # Augmentation

    # llm = HuggingFaceEndpoint(
    #     repo_id = "mistralai/Mistral-7B-Instruct-v0.2", # This model doesn't work with json_schema
    #     task = "text-generation"
    # )
    # model = ChatHuggingFace(llm=llm)

    generator = pipeline(
        "text2text-generation",           # Task type for T5 models
        model="google/flan-t5-base",       # Small, instruction-tuned model
        device=-1,                         # -1 means CPU
        max_new_tokens=512
    )

    llm = HuggingFacePipeline(pipeline=generator)

    prompt =  PromptTemplate(template = """
        You are a helpful assistant.
        Answer ONLY from the provided transcript context.
        If the context is insufficient, just say you don't know.
        {context}
        Question: {question}
        """,
        input_variables = ['context', 'question']
    )
    
    parralel_chain = RunnableParallel({
        'context': retriever | RunnableLambda(format_docs),
        'question': RunnablePassthrough()
    })

    parser = StrOutputParser()

    chain = parralel_chain | prompt | llm | parser
    
    return chain.invoke(query)

