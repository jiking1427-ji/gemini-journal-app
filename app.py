import os
from flask import Flask, jsonify, render_template_string, request
from google import genai

app = Flask(__name__)

# Gemini API சாவியை அமைத்தல் (புதிய google-genai SDK)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ji Web Assistant</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
        body { display: flex; height: 100vh; background-color: #1e1e2f; color: #fff; }
        
        #sidebar { width: 250px; background: #141423; padding: 15px; border-right: 1px solid #2d2d42; display: flex; flex-direction: column; }
        #sidebar h2 { font-size: 1.1rem; margin-bottom: 15px; color: #a2a2c2; text-align: center; }
        .new-btn { padding: 10px; background: #28a745; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; margin-bottom: 15px; }
        
        #main { flex: 1; display: flex; flex-direction: column; height: 100vh; }
        #header { padding: 15px; background: #181828; border-bottom: 1px solid #2d2d42; }
        #chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        
        .message { max-width: 75%; padding: 12px 16px; border-radius: 12px; font-size: 0.95rem; line-height: 1.4; word-wrap: break-word; }
        .user-msg { align-self: flex-end; background: #007bff; color: white; }
        .bot-msg { align-self: flex-start; background: #2c2c44; color: #e1e1e1; }
        
        #input-container { padding: 15px; background: #181828; display: flex; gap: 10px; border-top: 1px solid #2d2d42; }
        textarea { flex: 1; height: 45px; background: #252538; border: 1px solid #3b3b54; border-radius: 6px; padding: 10px; color: white; resize: none; outline: none; }
        button.send-btn { width: 80px; height: 45px; background: #007bff; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        button.send-btn:hover { background: #0056b3; }
    </style>
</head>
<body>

    <div id="sidebar">
        <h2>Ji Web Assistant</h2>
        <button class="new-btn" onclick="startNewChat()">+ New Chat</button>
    </div>

    <div id="main">
        <div id="header">
            <h3>Ji Web Assistant AI</h3>
        </div>

        <div id="chat-box"></div>

        <div id="input-container">
            <textarea id="userInput" placeholder="Ask anything..."></textarea>
            <button class="send-btn" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        function startNewChat() {
            document.getElementById('chat-box').innerHTML = '';
        }

        function appendMessage(sender, text) {
            const chatBox = document.getElementById('chat-box');
            const msgDiv = document.createElement('div');
            msgDiv.className = message ${sender === 'user' ? 'user-msg' : 'bot-msg'};
            msgDiv.innerText = text;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const prompt = input.value.trim();
            if (!prompt) return;

            appendMessage('user', prompt);
            input.value = '';

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt })
                });
                const data = await response.json();
                if (data.response) {
                    appendMessage('bot', data.response);
                } else {
                    appendMessage('bot', 'Error: ' + (data.error || 'No response from server'));
                }
            } catch (err) {
                appendMessage('bot', 'Error connecting to server.');
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
    data = request.get_json()
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
    app.run(host="0.0.0.0", port=5000)
