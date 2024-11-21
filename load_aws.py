import boto3
import PyPDF2
import re

# Configuration AWS
AWS_ACCESS_KEY = "votre_access_key"
AWS_SECRET_KEY = "votre_secret_key"
BUCKET_NAME = "nom_du_bucket"
REGION_NAME = "votre_region" 

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME
)

def download_pdf_from_s3(bucket_name, s3_key, local_path):
    try:
        s3_client.download_file(bucket_name, s3_key, local_path)
        print(f"Fichier {s3_key} téléchargé avec succès depuis S3.")
        return local_path
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        return None

# Fonction pour convertir le PDF en texte
def convert_pdf_to_text(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                text += page_text + " "

        # Nettoyage du texte
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        print(f"Erreur lors de la conversion du PDF : {e}")
        return None

# Fonction pour sauvegarder le texte dans le fichier 'vault.txt'
def save_text_to_vault(text, vault_path="vault.txt"):
    try:
        with open(vault_path, "a", encoding="utf-8") as vault_file:
            vault_file.write(text + "\n")
        print(f"Texte sauvegardé dans {vault_path}.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")

# Fonction principale
def process_pdf_from_s3(bucket_name, s3_key):
    local_pdf_path = "temp.pdf"
    
    # Télécharger le fichier PDF depuis S3
    pdf_path = download_pdf_from_s3(bucket_name, s3_key, local_pdf_path)
    if pdf_path:
        # Convertir le PDF en texte
        pdf_text = convert_pdf_to_text(pdf_path)
        if pdf_text:
            # Sauvegarder dans le vault
            save_text_to_vault(pdf_text)
        # Nettoyer le fichier temporaire
        try:
            os.remove(local_pdf_path)
        except OSError:
            pass

# Exemple d'utilisation
if __name__ == "__main__":
    # Nom du fichier dans S3 (clé S3)
    s3_key = "dossier/mon_fichier.pdf"

    # Télécharger et traiter le fichier PDF
    process_pdf_from_s3(BUCKET_NAME, s3_key)
