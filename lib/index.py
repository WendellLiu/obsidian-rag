import os
import re
import yaml
from typing import List, Dict, Any
from llama_index.core import VectorStoreIndex, Document, Settings

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Set up embedding model (multilingual)
embed_model = HuggingFaceEmbedding(
    model_name="nomic-ai/nomic-embed-text-v2-moe", trust_remote_code=True
)

Settings.embed_model = embed_model


def extract_yaml_frontmatter(text: str) -> Dict[str, Any]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if match:
        yaml_block = match.group(1)
        try:
            return yaml.safe_load(yaml_block)
        except Exception:
            return {}
    return {}


def extract_hashtags(text: str) -> List[str]:
    return list(set(re.findall(r"#(\w+)", text)))


def extract_backlinks(text: str) -> List[str]:
    return list(set(re.findall(r"\[\[([^\]]+)\]\]", text)))


def split_into_chunks(text: str) -> List[Dict[str, Any]]:
    # You can improve this to split by heading, paragraph, or sliding window
    # Here, we split by top-level headings for example
    pattern = r"(#+ .+)"
    splits = re.split(pattern, text)
    chunks = []
    for i in range(1, len(splits), 2):
        heading = splits[i].strip()
        content = splits[i + 1].strip()
        chunks.append({"heading": heading, "content": content})
    if not chunks:  # If no headings, treat as a single chunk
        chunks = [{"heading": None, "content": text.strip()}]
    return chunks


def parse_note(filepath: str, all_note_titles: List[str]) -> List[Document]:
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    frontmatter = extract_yaml_frontmatter(text)
    # Remove YAML frontmatter before further processing
    if frontmatter:
        text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
    hashtags = extract_hashtags(text)
    backlinks = extract_backlinks(text)
    chunks = split_into_chunks(text)
    note_title = os.path.splitext(os.path.basename(filepath))[0]
    documents = []
    for chunk in chunks:
        metadata = {
            "source_file": filepath,
            "note_title": note_title,
            "heading": chunk["heading"],
            "hashtags": hashtags,
            "backlinks": [b for b in backlinks if b in all_note_titles],
            "frontmatter": frontmatter,
        }
        documents.append(Document(text=chunk["content"], metadata=metadata))
    return documents


def get_all_note_titles(notes_paths: List[str]) -> List[str]:
    titles = []
    for path in notes_paths:
        if not path.endswith(".md"):
            continue
        title = os.path.splitext(os.path.basename(path))[0]
        titles.append(title)
    return titles


def build_index(notes_paths: List[str]):
    all_note_titles = get_all_note_titles(notes_paths)
    all_docs = []
    for file_path in notes_paths:
        docs = parse_note(file_path, all_note_titles)
        all_docs.extend(docs)

    index = VectorStoreIndex.from_documents(all_docs, show_progress=True)
    return index
