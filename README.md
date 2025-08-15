# Pronostici Roma - PostgreSQL Version

## Come usare

1. **Crea un database gratis su ElephantSQL**
   - Vai su [https://www.elephantsql.com/](https://www.elephantsql.com/)
   - Crea un account gratuito
   - Crea un nuovo instance
   - Copia la `URL` di connessione

2. **Carica su GitHub**
   - Sostituisci i file di questo progetto nel tuo repo GitHub

3. **Deploy su Render**
   - Vai su [https://render.com/](https://render.com/)
   - Crea un nuovo Web Service collegando il repo GitHub
   - In `Environment Variables` aggiungi:
     - Chiave: `DATABASE_URL`
     - Valore: la URL di ElephantSQL
   - Command: `gunicorn app:app`
   - Build Command: `pip install -r requirements.txt`

4. **Inizializza il DB**
   - Vai su `https://TUO-SITO/render.com/init` per creare le tabelle

5. **Usa l'app**
   - `/` → Classifica
   - `/pronostico` → Inserire pronostico
   - `/risultati` → Inserire risultati ufficiali e calcolare punti
