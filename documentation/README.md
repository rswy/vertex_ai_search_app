# Vertex AI Search POC

This project demonstrates how to integrate **Google Cloud Vertex AI Search** into a simple Flask web application.  
It supports **two modes**:
1. **Embedded Search Widget (JWT secured with auto-refresh)**  
2. **Direct API Search (server-side via Vertex AI Discovery Engine API)**  

---

## 📌 Features
- Simple **Flask backend** serving HTML templates.  
- **JWT token generator** for authenticating the search widget.  
- **Auto-refreshing JWT** (every 55 minutes) so widget sessions never expire.  
- `/api_search` endpoint to query Vertex AI Search programmatically.  
- Deployable locally and on **Render** with minimal configuration.  

---

## 🗂 Project Structure

```
my-search-app/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── Procfile               # Render startup config
├── .gitignore             # Exclude venv, secrets.json
├── templates/
│   └── index.html         # Frontend page with widget + search bar
└── static/
    └── style.css          # Optional styling
```

---

## 🔑 Prerequisites

1. **Google Cloud Project**
   - Vertex AI Search API enabled.
   - A **Data Store** (custom/unstructured) created.
   - At least one document (HTML/PDF) uploaded and indexed.
   - Widget/App Builder configuration created → copy your `configId`.
   - **Authorized domains** set:  
     - `localhost`  
     - `127.0.0.1`  
     - `your-app.onrender.com`  

2. **Service Account**
   - Create one in IAM.  
   - Assign role: `Discovery Engine Searcher` (or `Vertex AI Search Admin` for testing).  
   - Download the JSON key.  

3. **Local Setup**
   - Python 3.9+ installed.  
   - Recommended: use a virtual environment.  

---

## ⚙️ Installation

### Clone Repo
```bash
git clone https://github.com/<your-username>/my-search-app.git
cd my-search-app
```

### Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scriptsctivate      # Windows
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔧 Configuration

Create a `.env` file (or export manually):

```bash
GOOGLE_APPLICATION_CREDENTIALS=./secrets.json
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=global
GCP_DATA_STORE_ID=your-data-store-id
WIDGET_CONFIG_ID=your-widget-config-id
```

- Place the **service account JSON** locally as `secrets.json`.  
- For Render deployment → upload it as a **Secret File** and point env var to `/etc/secrets/secrets.json`.  

---

## ▶️ Running Locally

```bash
python app.py
```

Visit:  
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)  

---

## 🚀 Deploying to Render

1. Push repo to GitHub (exclude `venv/` + `secrets.json`).  
2. In Render:  
   - Create **New Web Service** → connect repo.  
   - Build Command:  
     ```bash
     pip install -r requirements.txt
     ```
   - Start Command:  
     ```bash
     gunicorn app:app
     ```
   - Add **Environment Variables** (same as local).  
   - Upload `secrets.json` as a **Secret File** at `/etc/secrets/secrets.json`.  

3. Add your Render URL to **Authorized Domains** in Vertex AI Console.  

---

## 🔍 Endpoints

- `/` → Renders `index.html` with widget + search bar.  
- `/token` → Returns JWT (used by widget).  
- `/api_search` → Accepts POST JSON `{ "query": "your search text" }` and returns results.  

---

## 🔄 Widget Auth (JWT)

The widget fetches `/token` and sets `authToken`.  
Token refresh logic in `index.html`:

```javascript
async function setAuthToken() {
  const res = await fetch("/token");
  const data = await res.json();
  const searchWidget = document.querySelector('gen-search-widget');
  searchWidget.authToken = data.token;
}

// Initial fetch
setAuthToken();

// Refresh every 55 minutes
setInterval(setAuthToken, 55 * 60 * 1000);
```

---

## 🛠 Troubleshooting

- **`ModuleNotFoundError: flask`** → Use `python -m pip install flask` with the same Python version you run.  
- **`Configuration is not authorized`** → Add your domain to **Authorized Domains** in Vertex AI Console.  
- **`DefaultCredentialsError`** → Check `GOOGLE_APPLICATION_CREDENTIALS` path.  
- **Empty results** → Wait a few minutes after uploading docs, indexing takes time.  

---

## ✅ Next Steps
- Secure `/token` route with authentication if app is user-facing.  
- Add a richer UI for displaying results (cards, snippets).  
- Automate doc ingestion pipeline (upload PDFs automatically).  
