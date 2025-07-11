import os
import ast
import sys

def get_docstrings_from_file(filepath):
    """Extracts and returns all docstrings from a given Python file."""
    docstrings = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)

        # Module-level docstring
        if ast.get_docstring(tree):
            #docstrings.append(f"--- Module Docstring for {filepath} ---\n{ast.get_docstring(tree)}\n")
            docstrings.append(f"{ast.get_docstring(tree)}")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                doc = ast.get_docstring(node)
                if doc:
                    #docstrings.append(f"--- Function Docstring for {node.name} in {filepath} ---\n{doc}\n")
                    docstrings.append(f"\t{doc}")
    except SyntaxError as e:
        print(f"Error parsing {filepath}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred while processing {filepath}: {e}", file=sys.stderr)
    return docstrings

def find_python_files(root_dir):
    """Finds all Python source and test files, excluding specified directories."""
    python_files = []
    script_path = os.path.abspath(__file__)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude pyenv and venv directories
        dirnames[:] = [d for d in dirnames if d not in ('pyenv', 'lib', 'bin', '__pycache__', '.pytest_cache')]

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if full_path == script_path:
                continue  # Exclude the script itself
            #if filename.endswith('.py') and (filename.startswith('test_') or not filename.startswith('test_')):
            if filename.endswith('.py') and not filename.startswith('__'):
                python_files.append(full_path)
    return python_files

if __name__ == "__main__":
    current_directory = os.getcwd()
    python_files_to_process = find_python_files(current_directory)
    #for filename in python_files_to_process:
        #print(filename)

    for py_file in python_files_to_process:
        all_docstrings = get_docstrings_from_file(py_file)
        for docstring in all_docstrings:
            print(docstring)