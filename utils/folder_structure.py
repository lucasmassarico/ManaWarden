import os


def list_structure(base_path, ignored_dirs=None):
    if ignored_dirs is None:
        ignored_dirs = ["__pycache__", ".venv-mana"]

    for root, dirs, files in os.walk(base_path):
        # Remove diretórios ignorados
        dirs[:] = [d for d in dirs if d not in ignored_dirs]

        # Print estrutura
        level = root.replace(base_path, "").count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")


# Use o caminho da pasta do projeto
list_structure("C:\\Users\\Niih\\Documents\\Projetos\\ManaWarden")
