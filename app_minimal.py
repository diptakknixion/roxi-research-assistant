from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    """Home page"""
    return jsonify({"message": "ROXI is running"})

# Vercel serverless handler
try:
    from serverless_wsgi import handle
    def handler(request):
        return handle(app, request)
except ImportError:
    handler = None

if __name__ == "__main__":
    app.run(debug=True)
    