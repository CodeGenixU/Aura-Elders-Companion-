# Aura Companion (Local Dev)

Simple full-stack web app with an empathetic AI chat (Gemini) and Firestore-backed reminders.

## Prerequisites
- Python 3.9+
- Gemini API Key (Google AI Studio)
- Firebase project with Firestore (Start in test mode for local dev)

## Setup
1. Create and activate venv
   - Windows PowerShell
     ```powershell
     python -m venv venv
     .\\venv\\Scripts\\activate
     ```
2. Install deps
   ```bash
   pip install -r requirements.txt
   ```
3. Set Gemini API Key (either)
   - Edit `app.py` and set `API_KEY = "YOUR_KEY"`, or
   - Set environment variable before run:
     - PowerShell: `$env:GEMINI_API_KEY = "YOUR_KEY"`

4. Run backend (serves API + frontend)
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000/` (Flask now serves the website and API)

5. Configure Firebase in `index.html` and `reminders.html`
   - Replace the `firebaseConfig` object with your own from Firebase Console.

6. (Optional) If you prefer a separate static server, you can still run:
   ```bash
   python -m http.server 5500
   ```
   And set the frontend to call the API at 5000:
   ```
   localStorage.setItem('AURA_BACKEND_URL', 'http://127.0.0.1:5000')
   ```

## Pages
- `index.html`: Dashboard (chat + reminders overview)
- `chat.html`: Dedicated chat page using Flask `/chat`
- `reminders.html`: Create/list/delete reminders in Firestore with alerts
- `about.html`: App overview
- `privacy.html`: Privacy details

## Test
- Chat: send a message and receive AI reply (backend running, Gemini key set).
- Reminders: add a reminder; see it in the list and Firestore.
- Alert: when time arrives, a modal appears; Dismiss removes it.

## Notes
- CORS is enabled for local dev.
- Uses anonymous Firebase Auth for local testing.

