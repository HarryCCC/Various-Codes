import os

def list_files(startpath):
    with open('file_tree.txt', 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            f.write('{}{}/\n'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                f.write('{}{}\n'.format(subindent, file))

if __name__ == "__main__":
    current_path = os.getcwd()
    target_folder = os.path.join(current_path, '国海金工量化-学习资料')
    list_files(target_folder)
