import os

def find_todos(root='.'):
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            try:
                if '.git' not in filepath:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        for lineno, line in enumerate(file, start=1):
                            if 'TODO' in line:
                                print(f"{filepath}:{lineno}: {line.strip()}")
            except (UnicodeDecodeError, PermissionError):
                # Skip binary or protected files
                continue

if __name__ == "__main__":
    find_todos()
