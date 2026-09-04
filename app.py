import os
from flask import Flask, jsonify, render_template_string, request
from google import genai

app = Flask(__name__)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ji Web Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: white; display: flex; flex-direction: column; height: 100vh; margin: 0; }
        #header { padding: 15px; background: #1f1f1f; text-align: center; font-size: 1.2rem; font-weight: bold; border-bottom: 1px solid #333; }
        #chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .msg { max-width: 80%; padding: 10px 14px; border-radius: 8px; line-height: 1.4; }
        .user { align-self: flex-end; background: #007bff; color: white; }
        .bot { align-self: flex-start; background: #2a2a2a; color: #e1e1e1; }
        #input-box { padding: 15px; background: #1f1f1f; display: flex; gap: 10px; }
        input { flex: 1; padding: 10px; border-radius: 5px; border: 1px solid #444; background: #2a2a2a; color: white; outline: none; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div id="header">Ji Web Assistant</div>
    <div id="chat-box"></div>
    <div id="input-box">
        <input type="text" id="userInput" placeholder="Ask anything...">
        <button onclick="send()">Send</button>
    </div>

    <script>
        async function send() {
            var input = document.getElementById('userInput');
            var txt = input.value.trim();
            if (!txt) return;

            var box = document.getElementById('chat-box');
            box.innerHTML += '<div class="msg user">' + txt + '</div>';
            input.value = '';
            box.scrollTop = box.scrollHeight;

            try {
                var res = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: txt})
                });
                var data = await res.json();
                box.innerHTML += '<div class="msg bot">' + (data.response || data.error) + '</div>';
            } catch(e) {
                box.innerHTML += '<div class="msg bot">Error connecting to server.</div>';
            }
            box.scrollTop = box.scrollHeight;
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
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
