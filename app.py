import os
from flask import Flask, jsonify, render_template_string, request
import google.generativeai as genai

app = Flask(__name__)

# Configure API Key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ji Web Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; display: flex; justify-content: center; }
        .chat-container { width: 100%; max-width: 500px; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        h2 { text-align: center; color: #333; }
        textarea { width: 100%; height: 100px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; font-size: 14px; }
        button { width: 100%; background-color: #28a745; color: white; border: none; padding: 12px; margin-top: 10px; border-radius: 5px; font-size: 16px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #218838; }
        #response-box { margin-top: 15px; padding: 10px; background: #e9ecef; border-radius: 5px; min-height: 50px; white-space: pre-wrap; font-size: 14px; }
    </style>
</head>
<body>
    <div class="chat-container">
        <h2>Ji Web Assistant</h2>
        <textarea id="prompt" placeholder="Enter your prompt here..."></textarea>
        <button onclick="generateAnswer()">Answer with Gemini</button>
        <div id="response-box">Your answer will appear here...</div>
    </div>

    <script>
        async function generateAnswer() {
            var prompt = document.getElementById('prompt').value;
            var responseBox = document.getElementById('response-box');
            if(!prompt) return alert('Please enter a prompt!');

            responseBox.innerText = 'Generating answer...';

            try {
                var res = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: prompt})
                });
                var data = await res.json();
                if(data.response) {
                    responseBox.innerText = data.response;
                } else {
                    responseBox.innerText = 'Error: ' + (data.error || 'Something went wrong');
                }
            } catch(e) {
                responseBox.innerText = 'Error connecting to server.';
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json() or {}
    prompt = data.get("prompt", "")
    try:
        response = model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
