from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    """Home page"""
    return jsonify({"message": "ROXI is running"})

if __name__ == "__main__":
    app.run(debug=True)
