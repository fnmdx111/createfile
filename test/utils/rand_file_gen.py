# encoding: utf-8
import os
import random
import string

FOLDER_NUM = 20
PATH_DEPTH = 5
FILE_NAME_LENGTH = 10


def write_random_file(path, size=8192, buffer=4096):
    with open(path, 'wb') as f:
        while size > 0:
            f.write(os.urandom(min(size, buffer)))
            size -= buffer


def random_word(length):
    return ''.join([random.choice(string.ascii_letters) for _ in range(length)])


def random_fp(parent):
    return os.path.join(parent,
                        random_word(random.randint(1, FILE_NAME_LENGTH)))


random_folders = [random_word(random.randint(2, 10)) for _ in range(FOLDER_NUM)]
def random_path(root='F:\\'):
    path = os.path.join(root, *[random.choice(random_folders)
                                for _ in range(random.randint(1, PATH_DEPTH))])
    return path


def usable_random_path(root='F:\\'):
    path = random_path(root=root)
    while os.path.exists(path):
        path = random_path(root=root)

    os.makedirs(path)

    return path


def usable_random_fp(root='F:\\'):
    parent = usable_random_path(root=root)

    fp = random_fp(parent)
    while os.path.exists(fp):
        fp = random_fp(parent)

    return fp
