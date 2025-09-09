from flask import Flask, render_template, request, jsonify
from google.cloud import discoveryengine_v1

app = Flask(__name__)

PROJECT_ID = "uobsearchhtool"
LOCATION = "global"  # or your Vertex AI Search region
SEARCH_ENGINE_ID = "uob-store_1748309184589"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.json.get("query")

    client = discoveryengine_v1.SearchServiceClient()
    serving_config = f"projects/{PROJECT_ID}/locations/{LOCATION}/dataStores/{SEARCH_ENGINE_ID}/servingConfigs/default_config"

    search_request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=5,
    )

    response = client.search(search_request)

    results = []
    for result in response:
        results.append({
            "title": result.document.title if result.document.title else "Untitled",
            "snippet": result.document.snippet if result.document.snippet else "",
            "uri": result.document.uri if result.document.uri else "#"
        })

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
