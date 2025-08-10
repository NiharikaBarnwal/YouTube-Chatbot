# YouTube Transcript Chatbot

A Streamlit-based chatbot that lets you chat with the transcript of any YouTube video.  
Paste a YouTube link, load its transcript (supports multiple languages), and ask questions about the video content. The chatbot answers using the video transcript as context.

---

## Features

- Extracts and processes YouTube video transcripts using [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api).
- Splits transcript text into manageable chunks for better semantic search.
- Creates vector embeddings of transcript chunks using HuggingFace embeddings.
- Uses a text-to-text generation model (`google/flan-t5-base`) for answering questions based on transcript context.
- Supports multiple transcript languages available for the video.
- Interactive chat interface built with Streamlit.
- Session-based chat history.
  
> **Note:**  
> To get answers in languages other than English, a heavier LLM with multilingual capabilities is needed. The current lightweight model is primarily English-focused and uses transcript text only.

---

## Demo Screenshot

*Include a screenshot or GIF here showing the app UI*

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/youtube-transcript-chatbot.git
cd youtube-transcript-chatbot
````

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root if needed (for example, if you plan to add API keys or configure settings).
For now, the project uses no required external API keys.

---

### 5. Run the Streamlit app

```bash
streamlit run home.py
```

---

## Usage

1. Paste a YouTube video URL in the input box.
2. Click **Load Languages** to fetch available transcript languages.
3. Select the preferred transcript language.
4. Click **Process Video** to load the transcript embeddings.
5. Ask questions about the video content using the chat interface.

---

## Requirements

* Python 3.8+
* `streamlit`
* `youtube-transcript-api`
* `langchain` and `langchain_community`
* `transformers`
* `huggingface_hub`
* `faiss-cpu` or `faiss-gpu` (depending on your hardware)
* `python-dotenv`

(See `requirements.txt` for full list)

---

## Notes & Limitations

* The transcript extraction depends on YouTube's transcript availability. Some videos may have no transcripts or disabled captions.
* The current model (`google/flan-t5-base`) is relatively small and primarily supports English well.
* For **answers in other languages**, you should use a heavier multilingual language model (e.g., `mistralai/Mistral-7B-Instruct-v0.2` or similar) which requires more memory and compute.
* The chatbot answers only based on the transcript context — it cannot access external information or knowledge beyond the video.
* Timestamp linking and enhanced UI features are planned improvements.

---

## Future Improvements

* Add clickable timestamps in answers to jump to video moments.
* Enable conversation memory for better contextual chat.
* Support user-uploaded transcripts or subtitle files.
* Integrate voice input/output.
* Add dark mode toggle.
* Provide summarization and keyword search over transcripts.

---

## Contributing

Feel free to open issues or pull requests for improvements or bug fixes!

---

## License

MIT License © Your Name

---

## Contact

For questions or suggestions, reach me at [your.email@example.com](mailto:your.email@example.com)

```

---

If you want, I can also generate a `requirements.txt` for you based on your project dependencies!
```
