import os
import hashlib

def get_file_hash(file_path, hash_algo=hashlib.sha256):
    """Compute the hash of a file."""
    hash_obj = hash_algo()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def find_duplicate_txt_files(directory):
    """Find and print duplicate .txt files in the given directory."""
    files_hash = {}
    duplicates = []

    # Walk through the directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                file_hash = get_file_hash(file_path)

                if file_hash in files_hash:
                    duplicates.append((file_path, files_hash[file_hash]))
                else:
                    files_hash[file_hash] = file_path

    if duplicates:
        print("Duplicate .txt files found:")
        for duplicate, original in duplicates:
            print(f"{duplicate} is a duplicate of {original}")
    else:
        print("No duplicate .txt files found.")

# Example usage
directory_path = 'C:/backgnd_data'  # Replace with your directory path
find_duplicate_txt_files(directory_path)
