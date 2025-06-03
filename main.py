import os

from lib.files import list_notes_paths


def main():
    notes_dir = os.getenv("NOTES_DIR")

    print(f"Using notes directory: {notes_dir}")
    if not notes_dir:
        raise ValueError("Environment variable 'NOTES_DIR' is not set.")

    notes_dir = os.path.expanduser(notes_dir)
    if not os.path.exists(notes_dir):
        raise ValueError(f"Directory '{notes_dir}' does not exist.")

    notes_files = list_notes_paths(notes_dir)

    # print path name from notes_files
    for file in notes_files:
        print(file)

    index_save_path = "./obsidian_index"


if __name__ == "__main__":
    main()
