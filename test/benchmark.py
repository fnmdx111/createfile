# encoding: utf-8
import os
import stat
import time

from drive.disk import get_drive_obj
from stream import WindowsPhysicalDriveStream
from test.utils.rand_file_gen import write_random_file, usable_random_fp


ROOT = 'F:\\'

def main(random_file_num):
    print('WARNING: This will wipe out your partition.')
    os.system('rmdir /S /Q \"%s\"' % ROOT)

    for root, dirs, files in os.walk(ROOT):
        for f in files:
            fp = os.path.join(root, f)
            os.chmod(fp, stat.S_IWUSR)
            os.remove(fp)
        for d in dirs:
            os.rmdir(os.path.join(root, d))

    for i in range(random_file_num):
        write_random_file(usable_random_fp(root=ROOT))


    with WindowsPhysicalDriveStream(2) as stream:
        t1 = time.time()
        partition = next(get_drive_obj(stream))
        entries = partition.get_entries()
        t2 = time.time()

        print('Partition type is %s. '
              'Read %s entries, '
              'which took %s' % (partition.type,
                                 entries.shape[0],
                                 t2 - t1))
        return t2 - t1, entries.shape[0]


if __name__ == '__main__':
    c = 0
    e = 0
    for i in range(5):
        _c, _e = main(100)

        c += _c
        e += _e

    print('1. %s' % (e / c))

    c = 0
    e = 0
    for i in range(5):
        _c, _e = main(500)

        c += _c
        e += _e

    print('1. %s' % (e / c))

    c = 0
    e = 0
    for i in range(5):
        _c, _e = main(1000)

        c += _c
        e += _e

    print('1. %s' % (e / c))
