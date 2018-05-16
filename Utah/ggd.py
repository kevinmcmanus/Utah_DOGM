import os
from shutil import copy
from zipfile import ZipFile

from g_download import get_files

#DOWNLOADING_FOLDER = 'C:/OGCC/UT/ZipDown'
#EXTRACTING_FOLDER = 'C:/OGCC/UT/Well Files'
#PREVIOUS_FOLDER = 'C:/OGCC/UT/PrevWellFiles'

DOWNLOADING_FOLDER = './download'
EXTRACTING_FOLDER = './extract'
PREVIOUS_FOLDER = './prev'

SLUG = '0ByStJjVZ7c7mM2hOYmF4ZENpNVE'


def main():
    if not os.path.isdir(DOWNLOADING_FOLDER):
        print('Download folder not exists or not valid')
        return
    if not os.path.isdir(EXTRACTING_FOLDER):
        print('Extract folder not exists or not valid')
        return

    for dirname, dirnames, filenames in os.walk(EXTRACTING_FOLDER):
        for subdirname in dirnames:
            subdirpath = os.path.join(dirname, subdirname)
            copy(subdirpath, os.path.join(PREVIOUS_FOLDER, subdirname))
            print ('Copying directory ' + subdirpath)

        for filename in filenames:
            filepath = os.path.join(dirname, filename)
            copy(filepath, os.path.join(PREVIOUS_FOLDER, filename))
            print ('Copying file ' + filepath)
            os.remove(filepath)
    get_files(SLUG, DOWNLOADING_FOLDER, EXTRACTING_FOLDER)


if __name__ == '__main__':
    main()
