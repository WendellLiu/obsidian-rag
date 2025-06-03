from pathlib import Path


def list_notes_paths(notes_dir: str):
    return [str(p) for p in Path(notes_dir).rglob("*.md") if p.is_file()]
