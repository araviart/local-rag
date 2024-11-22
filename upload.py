import io
import os
import re
import json
import boto3
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import messagebox
from dotenv import load_dotenv
from ttkbootstrap import Style  # Importation de ttkbootstrap pour une interface moderne
from ttkbootstrap.constants import *
import PyPDF2

# Charger les variables d'environnement
load_dotenv()

# Configuration AWS
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")

# Initialisation du client S3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME
)

# Création de la fenêtre principale avec ttkbootstrap
style = Style(theme="superhero")  # Utilisation du thème moderne "superhero"
root = style.master
root.title("Traitement de fichiers")
root.geometry("600x400")  # Taille de la fenêtre principale

# Barre de progression
progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="indeterminate")

# Fonction pour extraire le texte d'un PDF local
def convert_pdf_to_text():
    """Traitement d'un PDF local et extraction du texte."""
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers PDF", "*.pdf")])
    if file_path:
        progress.start()  # Démarrage de la barre de progression
        try:
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    if page.extract_text():
                        text += page.extract_text() + " "
                process_text_and_save(text)
            messagebox.showinfo("Succès", "Le texte du PDF a été ajouté à vault.txt.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du traitement du PDF : {e}")
        finally:
            progress.stop()  # Arrêt de la barre de progression

# Fonction pour traiter le texte extrait et le sauvegarder
def process_text_and_save(text):
    """Découper et sauvegarder le texte en petits morceaux."""
    text = re.sub(r'\s+', ' ', text).strip()  # Normalisation des espaces
    sentences = re.split(r'(?<=[.!?]) +', text)  # Découpage en phrases
    chunks = []
    current_chunk = ""

    # Découpage du texte en morceaux de taille maximale
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 < 1000:  # Limite de 1000 caractères
            current_chunk += (sentence + " ").strip()
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk)

    # Sauvegarde des morceaux dans le fichier vault.txt
    with open("vault.txt", "a", encoding="utf-8") as vault_file:
        for chunk in chunks:
            vault_file.write(chunk.strip() + "\n")

# Fonction pour traiter un fichier texte local
def upload_txtfile():
    """Traitement d'un fichier texte local et ajout à vault.txt."""
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers Texte", "*.txt")])
    if file_path:
        progress.start()  # Démarrage de la barre de progression
        try:
            with open(file_path, 'r', encoding="utf-8") as txt_file:
                text = txt_file.read()
                process_text_and_save(text)
            messagebox.showinfo("Succès", "Le contenu du fichier texte a été ajouté à vault.txt.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du traitement du fichier texte : {e}")
        finally:
            progress.stop()  # Arrêt de la barre de progression

# Fonction pour traiter un fichier JSON local
def upload_jsonfile():
    """Traitement d'un fichier JSON local et ajout à vault.txt."""
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers JSON", "*.json")])
    if file_path:
        progress.start()  # Démarrage de la barre de progression
        try:
            with open(file_path, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
                text = json.dumps(data, ensure_ascii=False)  # Conversion des données JSON en texte
                process_text_and_save(text)
            messagebox.showinfo("Succès", "Le contenu du fichier JSON a été ajouté à vault.txt.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du traitement du fichier JSON : {e}")
        finally:
            progress.stop()  # Arrêt de la barre de progression

# Fonction pour lister les fichiers d'un bucket S3
def list_files_in_s3(bucket_name):
    """Liste les fichiers dans un bucket S3 spécifié."""
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            return [item['Key'] for item in response['Contents']]
        else:
            return []
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la récupération des fichiers S3 : {e}")
        return []

# Fonction pour traiter un PDF depuis un bucket S3
def process_pdf_from_s3():
    """Permet de sélectionner et traiter un fichier depuis S3."""
    files = list_files_in_s3(BUCKET_NAME)  # Récupération des fichiers S3
    if not files:
        messagebox.showwarning("Aucun fichier", "Aucun fichier trouvé dans le bucket S3.")
        return

    # Fenêtre secondaire pour sélectionner un fichier S3
    s3_window = tk.Toplevel(root)
    s3_window.title("Sélectionner un fichier S3")
    s3_window.geometry("400x400")

    search_var = tk.StringVar()
    tk.Entry(s3_window, textvariable=search_var, width=40).pack(pady=10)

    def search_files():
        query = search_var.get().lower()
        filtered_files = [f for f in files if query in f.lower()]
        update_treeview(filtered_files)

    ttk.Button(s3_window, text="Rechercher", command=search_files).pack(pady=5)

    # Arbre pour afficher les fichiers disponibles
    tree = ttk.Treeview(s3_window, columns=("Nom du fichier",), show="headings")
    tree.heading("Nom du fichier", text="Nom du fichier")
    tree.pack(pady=10, fill="both", expand=True)

    def update_treeview(file_list):
        tree.delete(*tree.get_children())
        for file in file_list:
            tree.insert("", "end", values=(file,))

    update_treeview(files)

    def on_load():
        """Charger et traiter le fichier sélectionné depuis S3."""
        selected_item = tree.focus()
        if selected_item:
            file_key = tree.item(selected_item)["values"][0]
            text = read_pdf_from_s3(BUCKET_NAME, file_key)
            if text:
                process_text_and_save(text)
                messagebox.showinfo("Succès", f"Le contenu du fichier '{file_key}' a été ajouté à vault.txt.")
                s3_window.destroy()
            else:
                messagebox.showerror("Erreur", "Impossible de charger le fichier.")

    ttk.Button(s3_window, text="Charger le fichier", command=on_load).pack(pady=10)

# Fonction pour lire un fichier (PDF) depuis S3
def read_pdf_from_s3(bucket_name, s3_key):
    """Lit et extrait le texte d'un fichier PDF stocké dans S3."""
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
        messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier S3 : {e}")
        return None

# Fonction pour télécharger un fichier local sur S3
def upload_file_to_s3():
    """Télécharge un fichier local sur S3."""
    file_path = filedialog.askopenfilename(filetypes=[("Tous les fichiers", "*.*")])
    if file_path:
        try:
            file_name = os.path.basename(file_path)
            s3_client.upload_file(file_path, BUCKET_NAME, file_name)
            messagebox.showinfo("Succès", f"Le fichier '{file_name}' a été téléchargé sur S3.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du téléchargement du fichier sur S3 : {e}")

# Interface utilisateur
upload_frame = ttk.Frame(root, padding=20)
upload_frame.pack(fill="x")

s3_frame = ttk.Frame(root, padding=20)
s3_frame.pack(fill="x")

# Boutons d'action
ttk.Button(upload_frame, text="Télécharger un PDF", command=convert_pdf_to_text).pack(pady=5)
ttk.Button(upload_frame, text="Télécharger un fichier texte", command=upload_txtfile).pack(pady=5)
ttk.Button(upload_frame, text="Télécharger un fichier JSON", command=upload_jsonfile).pack(pady=5)
ttk.Button(upload_frame, text="Télécharger un fichier sur S3", command=upload_file_to_s3).pack(pady=5)
ttk.Button(s3_frame, text="Traiter un PDF depuis S3", command=process_pdf_from_s3).pack(pady=5)

# Lancer la boucle principale
root.mainloop()