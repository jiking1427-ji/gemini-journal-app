import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Complete HTML + JS Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant Studio</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { display: flex; height: 100vh; background-color: #f0f2f5; }
        .sidebar { width: 260px; background: #1e1e2d; color: #fff; display: flex; flex-direction: column; padding: 15px; }
        .new-chat-btn { background: #4b6cb7; color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px; }
        .chat-container { flex: 1; display: flex; flex-direction: column; height: 100vh; }
        .chat-header { background: #fff; padding: 15px 20px; border-bottom: 1px solid #ddd; font-weight: bold; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .message { max-width: 75%; padding: 12px 16px; border-radius: 12px; font-size: 15px; line-height: 1.5; }
        .user-message { background: #4b6cb7; color: white; align-self: flex-end; }
        .bot-message { background: #ffffff; color: #333; align-self: flex-start; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .input-area { background: #fff; padding: 15px 20px; border-top: 1px solid #ddd; }
        .input-wrapper { display: flex; align-items: center; background: #f8f9fa; border: 1px solid #ccc; border-radius: 25px; padding: 5px 15px; }
        .input-wrapper input[type="text"] { flex: 1; border: none; background: transparent; padding: 10px; outline: none; }
        .send-btn { background: #4b6cb7; color: white; border: none; width: 35px; height: 35px; border-radius: 50%; cursor: pointer; }
        .bot-actions { margin-top: 8px; }
        .action-btn { cursor: pointer; border: none; background: none; color: #555; }
    </style>
</head>
<body>
    <div class="sidebar">
        <button class="new-chat-btn" onclick="location.reload()"><i class="fas fa-plus"></i> New Chat</button>
        <p style="color: #8a8a9e; font-size: 13px;">Chat History Active</p>
    </div>
    <div class="chat-container">
        <div class="chat-header">AI Assistant Studio</div>
        <div class="chat-box" id="chatBox">
            <div class="message bot-message">
                வணக்கம்! நான் உங்களுக்கு எப்படி உதவட்டும்?
                <div class="bot-actions">
                    <button class="action-btn" onclick="speakText(this)"><i class="fas fa-volume-up"></i></button>
                </div>
            </div>
        </div>
        <div class="input-area">
            <div class="input-wrapper">
                <input type="text" id="userInput" placeholder="Ask anything..." onkeydown="if(event.key==='Enter') sendMessage()">
                <button class="send-btn" id="sendBtn" onclick="sendMessage()"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('userInput');
            const chatBox = document.getElementById('chatBox');
            const text = input.value.trim();
            if(!text) return;

            const userMsg = document.createElement('div');
            userMsg.className = 'message user-message';
            userMsg.innerText = text;
            chatBox.appendChild(userMsg);

            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            })
            .then(res => res.json())
            .then(data => {
                const botMsg = document.createElement('div');
                botMsg.className = 'message bot-message';
                botMsg.innerHTML = data.reply + <div class="bot-actions"><button class="action-btn" onclick="speakText(this)"><i class="fas fa-volume-up"></i></button></div>;
                chatBox.appendChild(botMsg);
                chatBox.scrollTop = chatBox.scrollHeight;
            })
            .catch(() => {
                const botMsg = document.createElement('div');
                botMsg.className = 'message bot-message';
                botMsg.innerText = "பதில் பெறுவதில் சிறு பிரச்சனை.";
                chatBox.appendChild(botMsg);
            });
        }

        function speakText(btn) {
            const text = btn.parentElement.parentElement.innerText;
            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(text);
            u.lang = 'ta-IN';
            window.speechSynthesis.speak(u);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_msg = data.get('message', '')
    # Simple Response Generator
    reply = f"உங்கள் கேள்வி பெறப்பட்டது: '{user_msg}'. AI பதில் தயார்!"
    return jsonify({'reply': reply})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
