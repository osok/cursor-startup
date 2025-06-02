import os

from common.logger import get_logger


def generate_tree(directory: str, exclusions: list[str] = None) -> str:
    """Generate a directory tree as a string."""
    if exclusions is None:
        exclusions = []  # Default to an empty list if no exclusions are provided

    tree_lines = []

    def walk_directory(dir_path: str, prefix: str = ""):
        entries = sorted(os.listdir(dir_path))
        # Filter entries based on the exclusions list
        entries = [e for e in entries if e not in exclusions and not e.endswith('.pyc')]

        for i, entry in enumerate(entries):
            full_path = os.path.join(dir_path, entry)
            connector = "├── " if i < len(entries) - 1 else "└── "
            tree_lines.append(f"{prefix}{connector}{entry}")

            if os.path.isdir(full_path):
                extension = "│   " if i < len(entries) - 1 else "    "
                walk_directory(full_path, prefix + extension)

    tree_lines.append(directory)
    walk_directory(directory)
    return "\n".join(tree_lines)


def clean_tree_content(tree_content: str) -> str:
    """Remove NBSP characters and clean up the content."""
    # Replace non-breaking spaces (Unicode \u00A0) with regular spaces
    cleaned_content = tree_content.replace("\u00A0", " ")
    return cleaned_content


def write_tree_to_file(tree_content: str, file_path: str):
    """Write the tree content to a file."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(tree_content)
    print(f"Tree structure written to {file_path}")


def insert_tree_into_readme(tree_content: str, readme_path: str):
    """Insert the cleaned tree structure into the README.md file."""
    with open(readme_path, "r") as readme:
        readme_lines = readme.readlines()

    start_marker = "## Project File Structure"
    end_marker = "## Base Agent Design"

    pre_section = []
    post_section = []
    in_tree_section = False
    end_marker_found = False

    for line in readme_lines:
        if start_marker in line:
            in_tree_section = True
            pre_section.append(line)
            pre_section.append("\n<details>\n<summary>Click to view the full project file structure</summary>\n\n")
            pre_section.append("```\n")
            pre_section.append(tree_content)
            pre_section.append("\n```\n</details>\n\n")
        elif in_tree_section and end_marker in line:
            in_tree_section = False
            end_marker_found = True
            post_section.append(line)
        elif in_tree_section:
            pass
        elif end_marker_found:
            post_section.append(line)
        elif not in_tree_section and not end_marker_found:
            pre_section.append(line)

    # Combine sections
    updated_readme = "".join(pre_section) + "".join(post_section)

    with open(readme_path, "w") as readme:
        readme.write(updated_readme)

    print(f"Updated README with tree structure.")


def main():
    directory = "."  # Current directory
    readme_file = "README.md"
    tree_output_file = "tree_structure.txt"
    exclusions = ['__pycache__',
                  'data',
                  '.idea',
                  '.git',
                  '.pytest_cache',
                  "eveidences",
                  '.test-net-debug-dashboard']

    logger = get_logger("Build Tree")

    logger.info(f"Current working directory: {os.getcwd()}")

    # Step 1: Generate the directory tree
    logger.info("generating tree structure")
    tree_content =  generate_tree(directory, exclusions)

    # Step 2: Clean the tree structure
    logger.info("cleaning tree structure")
    tree_content = clean_tree_content(tree_content)

    # Step 3: Write cleaned content to tree_structure.txt
    logger.info("writing tree structure to file")
    write_tree_to_file(tree_content, tree_output_file)

    # Step 4: Insert cleaned tree structure into README.md
    # logger.info("inserting tree structure into readme")
    # insert_tree_into_readme(tree_content, readme_file)

    logger.info("Process completed successfully.")


if __name__ == "__main__":
    main()
