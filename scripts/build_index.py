import os

from lib.files import list_notes_paths
from lib.index import build_index


def main():
    notes_dir = os.getenv("NOTES_DIR")

    print(f"Using notes directory: {notes_dir}")
    if not notes_dir:
        raise ValueError("Environment variable 'NOTES_DIR' is not set.")

    notes_dir = os.path.expanduser(notes_dir)
    if not os.path.exists(notes_dir):
        raise ValueError(f"Directory '{notes_dir}' does not exist.")

    notes_files = list_notes_paths(notes_dir)

    index_path = os.getenv("INDEX_DIR")
    if not index_path:
        raise ValueError("Environment variable 'INDEX_DIR' is not set.")

    if not os.path.exists(index_path):
        os.makedirs(index_path)

    index = build_index(notes_files)
    index.storage_context.persist(persist_dir=index_path)


if __name__ == "__main__":
    main()
