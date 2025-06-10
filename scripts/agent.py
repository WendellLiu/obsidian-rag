import gradio as gr
import os
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# define LLM
llm = OpenAI(temperature=1.1, model="gpt-4o-mini")

# change the global default LLM
Settings.llm = llm
embed_model = HuggingFaceEmbedding(
    model_name="nomic-ai/nomic-embed-text-v2-moe", trust_remote_code=True
)

Settings.embed_model = embed_model


def build_ask_rag(query_engine):
    def ask_rag(question):
        response = query_engine.query(question)
        answer = str(response)
        sources = [
            f"[{node.score:.3f}] {node.metadata.get('source_file', '')} {node.metadata.get('heading', '')}\n{node.text}\n"
            for node in response.source_nodes
        ]
        sources_text = "\n---\n".join(sources) if sources else "No source chunks found."
        return answer, sources_text

    return ask_rag


def main():
    index_path = os.getenv("INDEX_DIR")
    if not index_path:
        raise ValueError("Environment variable 'INDEX_DIR' is not set.")

    storage_context = StorageContext.from_defaults(persist_dir=index_path)
    index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine(similarity_top_k=5)
    ask_rag = build_ask_rag(query_engine)

    gui = gr.Interface(
        fn=ask_rag,
        inputs=gr.Textbox(label="Ask a question (English or Mandarin)"),
        outputs=[gr.Textbox(label="RAG Answer"), gr.Textbox(label="Source Chunks")],
        title="Obsidian RAG Search",
        description="Ask questions and get answers from your Obsidian notes (English/Traditional Mandarin supported).",
    )
    gui.launch(debug=True, share=False)


if __name__ == "__main__":
    main()
