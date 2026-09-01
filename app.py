import os
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# HTML UI Content
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Personal AI Journal</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        textarea { width: 100%; height: 120px; padding: 10px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #ccc; }
        button { background-color: #28a745; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #218838; }
        #result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-left: 4px solid #28a745; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h2>My Personal AI Journal</h2>
    <textarea id="journalText" placeholder="Write your daily thoughts here..."></textarea>
    <button onclick="analyzeText()">Analyze Thoughts with Gemini</button>
    <div id="result"></div>

    <script>
        async function analyzeText() {
            const text = document.getElementById('journalText').value;
            const resultDiv = document.getElementById('result');
            if(!text) { alert('Please enter some text!'); return; }
            
            resultDiv.innerText = "Thinking...";
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                const data = await response.json();
                if(data.result) {
                    resultDiv.innerText = data.result;
                } else {
                    resultDiv.innerText = "Error: " + (data.error || "Something went wrong!");
                }
            } catch (err) {
                resultDiv.innerText = "Error: " + err.message;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        user_text = data.get("text", "")
        
        if not user_text:
            return jsonify({"error": "No text provided"}), 400

        if not api_key:
            return jsonify({"error": "GEMINI_API_KEY is missing in Render environment"}), 500

        model = genai.GenerativeModel('gemini-3.5-flash')
        response = model.generate_content(user_text)
        
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
