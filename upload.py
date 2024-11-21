import io
import os
import tkinter as tk
from tkinter import filedialog
import PyPDF2
import re
import json
import boto3
import os

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")

# Client S3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME
)


def convert_pdf_to_text():
    """
    Lit un PDF depuis le système local, extrait le texte et l'enregistre dans vault.txt.
    """
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                if page.extract_text():
                    text += page.extract_text() + " "
            process_text_and_save(text)
            
            
def read_pdf_from_s3(bucket_name, s3_key):
    """
    Lit un PDF depuis S3, extrait le texte et le retourne.
    :param bucket_name: Nom du bucket S3.
    :param s3_key: Clé du fichier dans le bucket S3.
    :return: Texte brut extrait du PDF ou None en cas d'erreur.
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        pdf_file = response['Body'].read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            if page.extract_text():
                text += page.extract_text() + " "
        return text
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier PDF {s3_key} depuis S3: {e}")
        return None


def convert_pdf_from_s3_to_text(s3_key):
    """
    Lit un PDF depuis S3, extrait le texte et l'enregistre dans vault.txt.
    :param s3_key: Clé du fichier dans le bucket S3.
    """
    text = read_pdf_from_s3(BUCKET_NAME, s3_key)
    if text:
        process_text_and_save(text)
    else:
        print("Erreur : Impossible de lire le contenu du PDF depuis S3.")

            
def process_text_and_save(text):
    """
    Divise le texte en chunks et les ajoute à vault.txt.
    :param text: Texte brut extrait d'un PDF.
    """
    # Normaliser le texte
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Découper en phrases et chunks
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 pour l'espace
            current_chunk += (sentence + " ").strip()
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk)
    
    # Écrire les chunks dans vault.txt
    with open("vault.txt", "a", encoding="utf-8") as vault_file:
        for chunk in chunks:
            vault_file.write(chunk.strip() + "\n")
    print(f"Le texte a été ajouté à vault.txt avec chaque chunk sur une ligne.")


# Function to upload a text file and append to vault.txt
def upload_txtfile():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, 'r', encoding="utf-8") as txt_file:
            text = txt_file.read()
            
            # Normalize whitespace and clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split text into chunks by sentences, respecting a maximum chunk size
            sentences = re.split(r'(?<=[.!?]) +', text)  # split on spaces following sentence-ending punctuation
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                # Check if the current sentence plus the current chunk exceeds the limit
                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 for the space
                    current_chunk += (sentence + " ").strip()
                else:
                    # When the chunk exceeds 1000 characters, store it and start a new one
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:  # Don't forget the last chunk!
                chunks.append(current_chunk)
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    # Write each chunk to its own line
                    vault_file.write(chunk.strip() + "\n")  # Two newlines to separate chunks
            print(f"Text file content appended to vault.txt with each chunk on a separate line.")

# Function to upload a JSON file and append to vault.txt
def upload_jsonfile():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
            
            # Flatten the JSON data into a single string
            text = json.dumps(data, ensure_ascii=False)
            
            # Normalize whitespace and clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split text into chunks by sentences, respecting a maximum chunk size
            sentences = re.split(r'(?<=[.!?]) +', text)  # split on spaces following sentence-ending punctuation
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                # Check if the current sentence plus the current chunk exceeds the limit
                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 for the space
                    current_chunk += (sentence + " ").strip()
                else:
                    # When the chunk exceeds 1000 characters, store it and start a new one
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:  # Don't forget the last chunk!
                chunks.append(current_chunk)
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    # Write each chunk to its own line
                    vault_file.write(chunk.strip() + "\n")  # Two newlines to separate chunks
            print(f"JSON file content appended to vault.txt with each chunk on a separate line.")
            
from tkinter import simpledialog, ttk

def process_pdf_from_s3():
    """
    Affiche une liste des fichiers S3 disponibles et traite le fichier sélectionné.
    """
    # Lister les fichiers dans le bucket S3
    files = list_files_in_s3(BUCKET_NAME)
    if not files:
        print("Aucun fichier trouvé dans le bucket S3.")
        return
    
    # Créer une fenêtre pour sélectionner le fichier
    s3_window = tk.Toplevel(root)
    s3_window.title("Sélectionner un fichier S3")

    tk.Label(s3_window, text="Sélectionnez un fichier PDF dans S3 :").pack(pady=10)
    selected_file = tk.StringVar(s3_window)

    dropdown = ttk.Combobox(s3_window, textvariable=selected_file, values=files)
    dropdown.pack(pady=10)

    def on_confirm():
        s3_key = selected_file.get()
        if s3_key:
            convert_pdf_from_s3_to_text(s3_key)
            s3_window.destroy()
    
    tk.Button(s3_window, text="Confirmer", command=on_confirm).pack(pady=10)

def list_files_in_s3(bucket_name):
    """
    Liste tous les fichiers dans un bucket S3.
    :param bucket_name: Nom du bucket S3.
    :return: Liste des clés des fichiers dans le bucket.
    """
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            return [item['Key'] for item in response['Contents']]
        else:
            print("Aucun fichier trouvé dans le bucket.")
            return []
    except Exception as e:
        print(f"Erreur lors de la récupération des fichiers dans le bucket {bucket_name}: {e}")
        return []


# Create the main window
root = tk.Tk()
root.title("Upload .pdf, .txt, or .json")

# Create a button to open the file dialog for PDF
pdf_button = tk.Button(root, text="Upload PDF", command=convert_pdf_to_text)
pdf_button.pack(pady=10)

# Create a button to open the file dialog for text file
txt_button = tk.Button(root, text="Upload Text File", command=upload_txtfile)
txt_button.pack(pady=10)

# Create a button to open the file dialog for JSON file
json_button = tk.Button(root, text="Upload JSON File", command=upload_jsonfile)
json_button.pack(pady=10)

s3_button = tk.Button(root, text="Process PDF from S3", command=process_pdf_from_s3)
s3_button.pack(pady=10)

# Run the main event loop
root.mainloop()
