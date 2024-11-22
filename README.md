# Local RAG with Ollama

### Installation

1. git clone https://github.com/araviart/local-rag.git
2. cd dir
3. pip install -r requirements.txt
4. Installer Ollama (https://ollama.com/download)
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

### Paramètres du prompt

Liste non-exhaustive de paramètres que j'ai trouvé pertinent :

1. Température

- Contrôle la créativité ou la diversité des réponses.
0.0 : Réponses déterministes.
1.0 : Réponses plus créatives et diversifiées.

valeur 0.1 : 

Le texte discute des risques potentiels associés à la concentration du développement d'intelligence artificielle (IA) entre les mains de quelques pays, entreprises et individus. Il souligne que l'humanité n'est pas encore suffisamment préparée pour affronter ces risques, qui peuvent inclure des déclassements économiques, une concurrence injuste et des menaces existentielles pour l'humanité.

L'Auteurs ont proposé plusieurs actions pour répondre à ces défis, notamment :

*   Création d'un fonds d'investissement « France & IA » pour soutenir l'écosystème de l'IA en France.
*   Mise en place de la gouvernance des données pour garantir leur qualité et leur sécurité.

[...]


valeur 0.5 : 

Le document discute des risques et opportunités associés à l'intelligence artificielle (IA). Les auteurs soulignent que la concentration de la recherche en IA entre les mains d'un petit nombre de pays, d'entreprises et de personnes peut créer des problèmes de concurrence et de politique industrielle. Cependant, ils estiment qu'Aucune IA n'est encore capables de dépasser l'intelligence humaine dans toutes les tâches et qu'il est donc nécessaire de rester vigilant.

Les auteurs proposent une approche en termes de politiques industrielles et de concurrence pour développer la capacité d'évaluation des systèmes d'IA les plus avancés, ainsi que d'une gouvernance pour répondre aux risques potentiels. Ils ont également des idées sur comment France pourrait s'intégrer à la demande croissante en IA, notamment avec la création d'un fonds d'investissement « France & IA » qui mobilisera 10 M€ de capital-investissement et soutien public.

[...]


Description : Limite le nombre de tokens (unités de texte comme des mots ou morceaux de mots) que le modèle peut générer dans la réponse.
Impact :
Une valeur plus élevée permet des réponses plus longues.
Une valeur plus basse restreint la taille de la réponse pour limiter le coût ou mieux contrôler la longueur.

2. max_tokens
Description : Limite le nombre de tokens (unités de texte comme des mots ou morceaux de mots) que le modèle peut générer dans la réponse.
Une valeur plus élevée permet des réponses plus longues.
Une valeur plus basse restreint la taille de la réponse pour limiter le coût ou mieux contrôler la longueur.

3. messages

Description : Une liste structurée contenant le contexte et les instructions pour la génération. Chaque message a un rôle et un contenu.
En l'occurence, à chaque itération, la requête de l'utilisateur (user_input) est ajoutée avec un rôle user.
Une fois la réponse générée par l'assistant, celle-ci est ajoutée à conversation_history avec un rôle assistant.
Cela permet au modèle d’utiliser l’historique de la conversation pour produire des réponses contextuelles.