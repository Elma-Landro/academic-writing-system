
# Configuration des Secrets dans Replit

## Configuration Google OAuth

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez l'API Google Drive
4. Créez des identifiants OAuth 2.0
5. Ajoutez cette URL comme URI de redirection autorisée :
   `https://[votre-repl-name]-[votre-username].replit.app/`
6. Dans Replit Secrets, ajoutez :
   - `GOOGLE_CLIENT_ID` : Votre client ID
   - `GOOGLE_CLIENT_SECRET` : Votre client secret

## Configuration IA (Optionnel)

### OpenAI
- `OPENAI_API_KEY` : Votre clé API OpenAI

### Venice AI (Alternative)
- `VENICE_API_KEY` : Votre clé API Venice

## Configuration IPFS (Optionnel)

### Fileverse (Recommandé pour POC)
1. Créez un compte sur [Fileverse.io](https://fileverse.io)
2. Récupérez votre clé API
3. Ajoutez : `FILEVERSE_API_KEY`

### Pinata (Alternative)
- `PINATA_API_KEY` : Votre clé API Pinata
- `PINATA_SECRET` : Votre secret Pinata

## Test de Configuration

Lancez l'application et vérifiez dans les logs que les services sont correctement initialisés.
