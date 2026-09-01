import os
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(_name_)

# Environment Variable-ல் இருந்து API Key எடுத்தல்
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Personal Gemini Journal</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        textarea { width: 100%; height: 100px; margin-bottom: 10px; }
        button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px; }
    </style>
</head>
<body>
    <h2>My Personal AI Journal</h2>
    <textarea id="entry" placeholder="Write your daily thoughts here..."></textarea><br>
    <button onclick="analyzeJournal()">Analyze Thoughts with Gemini</button>
    <div id="response" class="result" style="display:none;"></div>

    <script>
        async function analyzeJournal() {
            const entry = document.getElementById('entry').value;
            const resDiv = document.getElementById('response');
            resDiv.style.display = 'block';
            resDiv.innerHTML = 'Thinking...';

            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: entry })
            });
            const data = await response.json();
            resDiv.innerHTML = '<b>Gemini Insight:</b><br>' + data.result;
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
    data = request.json
    user_text = data.get("text", "")
    
    if not api_key:
        return jsonify({"result": "API Key configured இல்லை!"})

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"Analyze this journal entry and provide a thoughtful reflection: {user_text}")
    return jsonify({"result": response.text})

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))