# Importing  necessary libraries
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace, HuggingFacePipeline
from transformers import pipeline
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from typing import List, Tuple
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

load_dotenv()

# ---------- Helper to get the video id ----------
def extract_video_id(url: str):
    query = urlparse(url).query
    params = parse_qs(query)
    video_id = params.get("v")
    if video_id:
        return video_id[0]
    else:
        raise ValueError("Invalid YouTube URL: no video id found.")

# ---------- Helper to get available languages ----------
def get_available_languages(url: str):
    try:
        video_id = extract_video_id(url)
        api = YouTubeTranscriptApi()
        transcripts = api.list(video_id=video_id)
        return [(t.language, t.language_code) for t in transcripts]
    except Exception as e:
        print("Error fetching transcripts:", e)
        return []

# ---------- To create retriever ----------
def process_video(url: str, language: str = 'en'):
    video_id = extract_video_id(url)
    api = YouTubeTranscriptApi()
    try:
        transcript_list = api.fetch(video_id=video_id, languages=[language])
        transcript = " ".join([d.text for d in transcript_list])
    except NoTranscriptFound:
        if language != 'en':
            transcript_list = api.fetch(video_id, languages=['en'])
            transcript = " ".join([d.text for d in transcript_list])
        else:
            raise ValueError(f"No transcript found for language '{language}'.")
    except TranscriptsDisabled:
        raise ValueError("Transcript is disabled for this video.")

    # Split transcript
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcript])
    
    # Create embeddings and FAISS vector store
    embeddings = HuggingFaceEmbeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    return vector_store.as_retriever(search_type='similarity', search_kwargs={"k":4})

# ---------- Chat function ----------
def chat_with_video(retriever, query: str):

    def format_docs(retrieved_docs):
        return "\n\n".join(doc.page_content for doc in retrieved_docs)

    generator = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        device=-1,
        max_new_tokens=512
    )

    llm = HuggingFacePipeline(pipeline=generator)

    prompt = PromptTemplate(
        template="""
        You are a helpful assistant.
        Answer ONLY from the provided transcript context.
        If the context is insufficient, just say you don't know.
        {context}
        Question: {question}
        """,
        input_variables=['context', 'question']
    )
    
    parallel_chain = RunnableParallel({
        'context': retriever | RunnableLambda(format_docs),
        'question': RunnablePassthrough()
    })

    parser = StrOutputParser()
    chain = parallel_chain | prompt | llm | parser
    
    return chain.invoke(query)
