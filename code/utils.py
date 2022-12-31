import os


def traverse_files_with_ext(folder: str, ext=None):
    """
    :param folder: the folder storing apks.
    :param ext: expected extension.
    :return: list of all file paths.
    """
    ans = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if ext is not None and os.path.splitext(file)[1] != '.' + ext:
                continue
            ans.append(os.path.join(root, file))
    return ans


def cmd(command: str):
    print("-" * 40)
    print("CMD> " + command)
    print(os.popen(command).read())
