from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from zipfile import ZipFile

import os
import shutil


def download_file_and_extract(f, download_folder, extract_folder):
    print('Downloading file: {0}'.format(f['title']))
    try:
        path = os.path.join(download_folder, f['title'])
        f.GetContentFile(path)
        zf = ZipFile(path)
        zf.extractall(path=extract_folder)
        zf.close()
    except Exception as e:
        print('Error {0} at {1}'.format(e, f['embedLink']))
        return
    print('Downloading and extracting is over: {0}'.format(f['embedLink']))


def write_folder_to_output(f):
    print('{0}\n'.format(f['title']))


def list_folder(parent, drive, download_folder, extract_folder, is_top=True):
    try:
        file_list = drive.ListFile(
            {'q': "'{}' in parents and trashed=false".format(
                parent)}).GetList()
        for f in file_list:
            if f['mimeType'] == 'application/vnd.google-apps.folder':
                write_folder_to_output(f)
                list_folder(f['id'], drive, is_top=False)
            else:
                download_file_and_extract(f, download_folder, extract_folder)
        # Return list of extracted files
        filelist = [f for f in listdir(extract_folder)]
        return (filelist)

    except Exception as e:
        print(e)


def get_files(slug, download_folder, extract_folder):
    gauth = GoogleAuth()
    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        print('here')
        os.remove('mycreds.txt')
        gauth.LocalWebserverAuth()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")

    drive = GoogleDrive(gauth)

    return list_folder(slug, drive, download_folder, extract_folder)


if __name__ == '__main__':
    get_files('0ByStJjVZ7c7mM2hOYmF4ZENpNVE', './download', './extract')
