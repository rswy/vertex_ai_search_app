import os
import json
import datetime
import jwt  # PyJWT
from flask import Flask, render_template, request, jsonify

from google.cloud import discoveryengine_v1

app = Flask(__name__)


from dotenv import load_dotenv
import os

# This will load local `.env` if present (for dev).
# On Render, it won’t find one, and that’s fine.
load_dotenv()

# --- Vertex AI Search config (set these) ---
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-project-id")
LOCATION   = os.getenv("GCP_LOCATION", "global")
DATA_STORE = os.getenv("GCP_DATA_STORE_ID", "your-datastore-id")  # Data Store ID
WIDGET_CONFIG_ID = os.getenv("WIDGET_CONFIG_ID", "your-config-id")  # widget configId from console

# --- Load service account key from GOOGLE_APPLICATION_CREDENTIALS ---
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not CREDENTIALS_PATH or not os.path.exists(CREDENTIALS_PATH):
    raise RuntimeError(
        "GOOGLE_APPLICATION_CREDENTIALS is not set or path not found. "
        "Set it to the absolute path of your service-account JSON."
    )

with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
    service_account_info = json.load(f)

SERVICE_ACCOUNT_EMAIL = service_account_info["client_email"]
PRIVATE_KEY = service_account_info["private_key"]
# --- Helpers ---
def generate_jwt():
    """
    Generate a short-lived JWT for the widget using the service account.
    """
    from datetime import datetime, timedelta, timezone

    # issued_at = datetime.datetime.utcnow()
    # exp = issued_at + datetime.timedelta(minutes=60)  # expires in 60 min
    issued_at = datetime.now(timezone.utc)
    exp = issued_at + timedelta(minutes=59)

    
    payload = {
        "iss": SERVICE_ACCOUNT_EMAIL,
        "sub": SERVICE_ACCOUNT_EMAIL,
        "aud": "https://gen-app-builder.googleapis.com/",
        "iat": int(issued_at.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
    print(f"\n\nJWT Token!!!!:\n{token}\n\n")
    # PyJWT returns str in new versions; ensure string
    return token if isinstance(token, str) else token.decode("utf-8")

def serving_config_path():
    # default path helper; adjust serving config name if your console shows a different one
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores/{DATA_STORE}/servingConfigs/default_config"

# --- Routes ---
@app.get("/")
def home():
    # Show widget + API UI on same page
    return render_template("index.html", widget_config_id=WIDGET_CONFIG_ID)

@app.get("/token")
def token():
    return jsonify({"token": generate_jwt()})

@app.post("/api_search")
def api_search():
    """
    Direct API integration to Vertex AI Search.
    Frontend posts JSON: {"query": "..."} ; returns JSON list of results.
    """
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Missing query"}), 400

    client = discoveryengine_v1.SearchServiceClient()
    # req = discoveryengine_v1.SearchRequest(
    #     serving_config=serving_config_path(),
    #     query=query,
    #     page_size=5,
    # )

    
    req = discoveryengine_v1.SearchRequest(
        serving_config=serving_config_path(),
        query=query,
        page_size=10,
        query_expansion_spec={"condition": "AUTO"},
        content_search_spec={
            "summary_spec": {"summary_result_count": 5}  # ask for summary too
        },
    )

    response = client.search(request=req)

    results = []
    for result in response:
        doc = result.document
        derived = getattr(doc, "derived_struct_data", None)

        title = "Untitled"
        uri = "#"
        snippet = ""

        # pull from derived_struct_data if present
        if derived:
            title = derived.get("title", title)
            uri = derived.get("link", uri) or derived.get("uri", uri)

        # prefer result.snippet, fallback to struct_data
        if hasattr(result, "snippet"):
            snippet = result.snippet
        elif doc.struct_data:
            snippet = doc.struct_data.get("snippet", "")

        results.append({
            "title": title,
            "snippet": snippet,
            "uri": uri
        })

    # grab summary if Vertex AI Search generated one
    summary_text = None
    if response.summary and response.summary.summary_text:
        summary_text = response.summary.summary_text

    return jsonify({
        "results": results,
        "summary": summary_text
    })


    # results = []
    # for result in response:
    #     doc = result.document
    #     # Be defensive across doc formats
    #     # Try derived_struct_data -> struct_data -> individual fields
    #     derived = getattr(doc, "derived_struct_data", None)
    #     struct   = getattr(doc, "struct_data", None)

    #     def get_field(obj, key, default=None):
    #         try:
    #             return obj.get(key, default) if obj else default
    #         except Exception:
    #             return default

    #     title   = get_field(derived, "title") or get_field(struct, "title") or getattr(doc, "title", None) or "Untitled"
    #     snippet = get_field(derived, "snippet") or get_field(struct, "snippet") or ""
    #     uri     = get_field(derived, "uri") or get_field(struct, "uri") or getattr(doc, "uri", None) or "#"

    #     results.append({"title": title, "snippet": snippet, "uri": uri})

    # return jsonify(results)

if __name__ == "__main__":
    # Local dev server (use gunicorn in production)
    app.run(host="0.0.0.0", port=5000, debug=True)
