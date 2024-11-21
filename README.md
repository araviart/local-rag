# Local RAG with Ollama + Email RAG

### Installation

1. git clone https://github.com/AllAboutAI-YT/easy-local-rag.git
2. cd dir
3. pip install -r requirements.txt
4. Install Ollama (https://ollama.com/download)
5. ollama pull llama3.2

#### Configuration du bucket S3

Créez un bucket S3 et chargez vos fichiers pdf dessus, créez un utilisateur avec les droits admin ( le code utilise s3:ListBucket et ListObjectV2 ).
Créez un fichier .env à la racine du projet, en complétant les informations ci-joints : 

```
AWS_ACCESS_KEY = "#"
AWS_SECRET_KEY = "#"
BUCKET_NAME = "#"
REGION_NAME = "#" 
```

#### Lancement : 

6. python upload.py
7. python localrag.py

### Tests avec différentes valeurs




