import os
from fastapi import UploadFile
import zipfile
import io
import requests
import shutil
from dotenv import load_dotenv
import json


def download_file(url, file_name, directory="downloads"):
    response = requests.head(url, allow_redirects=True, verify=True)
    if response.headers.get("Content-Encoding") == 'gzip' or response.headers.get("Content-Type") == 'application/zip' or response.headers.get('Content-Type') == 'application/octet-stream':
        response = requests.get(url, stream=True, allow_redirects=True, verify=True)
        if not os.path.exists(directory):
            os.makedirs(directory)
        filepath = os.path.join(directory, f"{file_name}.zip")
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
                

        return filepath
    else:
        return False

def extract_zip(zip_file_path: str, extracted_folder):
    if not os.path.exists(extracted_folder):
        os.makedirs(extracted_folder)
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extracted_folder)
    extracted_folder_path = os.path.abspath(extracted_folder)
    return extracted_folder_path

def is_zip_file(file_path):
    file_extension = os.path.splitext(file_path)[1]
    if file_extension.lower() == ".zip":
        return True
    else:
        return False

def remove_directory(directory):
    try:
        shutil.rmtree(directory)
        return True
    except Exception as e:
        return False
