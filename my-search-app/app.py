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
        doc = result.document
        results.append({
            "title": doc.struct_data.get("title", "Untitled") if doc.struct_data else "Untitled",
            "snippet": doc.struct_data.get("snippet", "") if doc.struct_data else "",
            "uri": doc.struct_data.get("uri", "#") if doc.struct_data else "#"
        })

    return render_template("index.html", results=results)
    # return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
