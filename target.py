#!/usr/bin/env python3

from flask import Flask, jsonify, request

app = Flask(__name__)

# Counter for requests sent and responses received
requests_sent = 0
responses_received = 0

@app.route('/ping', methods=['GET'])
def ping_endpoint():
    # Simulated test endpoint logic
    global responses_received
    responses_received += 1
    return "Ping response\n"

@app.route('/metrics', methods=['GET'])
def metrics_endpoint():
    global requests_sent, responses_received
    return jsonify({"requests_sent": requests_sent, "responses_received": responses_received})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # Target server listens on port 8080

