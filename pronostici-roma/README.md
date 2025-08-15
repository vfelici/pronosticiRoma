# Pronostici Roma - Web App Flask

Questa app permette a 5 utenti di inserire pronostici su partite della Roma.
I pronostici sono nascosti fino alla fine della partita.

## Deploy su Render

1. Crea un repository su GitHub e carica questa cartella.
2. Su [Render.com](https://render.com), crea un nuovo **Web Service**.
3. Build Command:
   ```
   pip install -r requirements.txt
   ```
4. Start Command:
   ```
   gunicorn app:app --preload
   ```
5. Aggiungi variabile d'ambiente `SECRET_KEY` con un valore casuale.
6. Crea un disco persistente `/data` per il database.
7. Dopo il primo deploy, visita `/init` per creare il DB e gli utenti:
   - admin / adminpass
   - user1 / pass1
   - user2 / pass2
   - user3 / pass3
   - user4 / pass4
