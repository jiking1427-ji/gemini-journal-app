import base64
import os
import google.generativeai as genai
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Gemini API சாவியை அமைத்தல்
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ji Web Assistant</title>
    <meta name="description" content="Ji Web Assistant - Smart AI Companion for Students.">
    <meta name="keywords" content="Ji Web Assistant, Student AI, Tamil AI Assistant">
    <meta name="author" content="Balaji">
    <meta name="theme-color" content="#1e1e2f">
    
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { display: flex; height: 100vh; background-color: #1e1e2f; color: #fff; }
        
        /* Sidebar Design */
        #sidebar { width: 260px; background: #141423; display: flex; flex-direction: column; padding: 15px; border-right: 1px solid #2d2d42; }
        #sidebar h2 { font-size: 1.1rem; margin-bottom: 15px; color: #a2a2c2; text-align: center; }
        .new-chat-btn { padding: 10px; background: #28a745; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; margin-bottom: 15px; }
        .new-chat-btn:hover { background: #218838; }
        .history-list { flex: 1; overflow-y: auto; list-style: none; }
        .history-item { padding: 10px; margin-bottom: 8px; background: #232338; border-radius: 6px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; }
        .history-item:hover { background: #2d2d48; }
        .history-item.pinned { border-left: 3px solid #f39c12; }
        .pin-btn { background: none; border: none; color: #f39c12; cursor: pointer; }

        /* Main Chat Area */
        #main { flex: 1; display: flex; flex-direction: column; height: 100vh; }
        #header { padding: 15px; background: #181828; border-bottom: 1px solid #2d2d42; display: flex; justify-content: space-between; align-items: center; }
        #chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .message { max-width: 75%; padding: 12px 16px; border-radius: 12px; font-size: 0.95rem; line-height: 1.4; word-wrap: break-word; }
        .user-msg { align-self: flex-end; background: #007bff; color: white; border-bottom-right-radius: 2px; }
        .bot-msg { align-self: flex-start; background: #2c2c44; color: #e1e1e1; border-bottom-left-radius: 2px; }
        .chat-img { max-width: 100%; max-height: 200px; border-radius: 8px; margin-bottom: 8px; display: block; }
        .action-btns { display: flex; gap: 10px; margin-top: 8px; }
        .action-btn { font-size: 0.75rem; background: none; border: none; color: #8888b0; cursor: pointer; text-decoration: underline; }

        /* Input Bar */
        #input-container { padding: 15px; background: #181828; display: flex; gap: 10px; border-top: 1px solid #2d2d42; align-items: center; }
        textarea { flex: 1; height: 45px; background: #252538; border: 1px solid #3b3b54; border-radius: 6px; padding: 10px; color: white; resize: none; outline: none; }
        .icon-btn { width: 45px; height: 45px; background: #28a745; color: white; border: none; border-radius: 6px; font-size: 1.2rem; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        button.send-btn { width: 70px; height: 45px; background: #007bff; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        button.send-btn:hover { background: #0056b3; }
        button.recording { background: #dc3545; animation: pulse 1s infinite; }
        #imagePreviewContainer { position: relative; display: none; }
        #imagePreview { width: 45px; height: 45px; border-radius: 6px; object-fit: cover; }
        #removeImg { position: absolute; top: -5px; right: -5px; background: red; color: white; border: none; border-radius: 50%; width: 18px; height: 18px; font-size: 10px; cursor: pointer; }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    </style>
</head>
<body>

    <!-- Sidebar -->
    <div id="sidebar">
        <h2>Ji Web Assistant</h2>
        <button class="new-chat-btn" onclick="startNewChat()">+ New Chat</button>
        <ul class="history-list" id="historyList"></ul>
    </div>

    <!-- Main Content Area -->
    <div id="main">
        <div id="header">
            <h3>Ji Web Assistant AI</h3>
        </div>

        <div id="chat-box"></div>

        <div id="input-container">
            <!-- Image Input Button -->
            <input type="file" id="imageInput" accept="image/*" style="display: none;" onchange="previewSelectedImage(event)">
            <button class="icon-btn" onclick="document.getElementById('imageInput').click()" title="Attach Image">📷</button>
            
            <div id="imagePreviewContainer">
                <img id="imagePreview" src="" alt="Preview">
                <button id="removeImg" onclick="clearSelectedImage()">✕</button>
            </div>

            <!-- Voice Button -->
            <button class="icon-btn" id="micBtn" onclick="toggleVoiceInput()" title="Speak">🎙️</button>
            
            <textarea id="userInput" placeholder="Ask anything or upload photo..."></textarea>
            <button class="send-btn" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let currentChatId = Date.now();
        let chats = JSON.parse(localStorage.getItem('ji_chats')) || {};
        let recognition = null;
        let isRecording = false;
        let selectedBase64Image = null;

        // PWA Service Worker Registration
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('data:text/javascript,console.log("SW Registered");');
        }

        // Voice Recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'ta-IN';

            recognition.onresult = function(event) {
                document.getElementById('userInput').value = event.results[0][0].transcript;
                stopRecording();
            };
            recognition.onerror = function() { stopRecording(); };
            recognition.onend = function() { stopRecording(); };
        }

        function toggleVoiceInput() {
            if (!recognition) return alert('Voice input not supported in this browser.');
            if (isRecording) {
                recognition.stop();
                stopRecording();
            } else {
                recognition.start();
                isRecording = true;
                const btn = document.getElementById('micBtn');
                btn.classList.add('recording');
                btn.innerText = '🛑';
            }
        }

        function stopRecording() {
            isRecording = false;
            const btn = document.getElementById('micBtn');
            btn.classList.remove('recording');
            btn.innerText = '🎙️';
        }

        function speakText(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'ta-IN';
                window.speechSynthesis.speak(utterance);
            }
        }

        // Image Handling
        function previewSelectedImage(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    selectedBase64Image = e.target.result.split(',')[1];
                    document.getElementById('imagePreview').src = e.target.result;
                    document.getElementById('imagePreviewContainer').style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        }

        function clearSelectedImage() {
            selectedBase64Image = null;
            document.getElementById('imageInput').value = '';
            document.getElementById('imagePreviewContainer').style.display = 'none';
        }

        function saveChats() {
            localStorage.setItem('ji_chats', JSON.stringify(chats));
            renderHistory();
        }

        function renderHistory() {
            const list = document.getElementById('historyList');
            list.innerHTML = '';
            const keys = Object.keys(chats).sort((a, b) => (chats[b].pinned || 0) - (chats[a].pinned || 0));

            keys.forEach(id => {
                const li = document.createElement('li');
                li.className = history-item ${chats[id].pinned ? 'pinned' : ''};
                const title = chats[id].title || 'New Conversation';
                li.innerHTML = `
                    <span onclick="loadChat('${id}')">${title.substring(0, 18)}...</span>
                    <button class="pin-btn" onclick="togglePin('${id}', event)">📌</button>
                `;
                list.appendChild(li);
            });
        }

        function loadChat(id) {
            currentChatId = id;
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML = '';
            chats[id].messages.forEach(msg => appendMessage(msg.sender, msg.text, msg.image, false));
        }

        function startNewChat() {
            currentChatId = Date.now();
            document.getElementById('chat-box').innerHTML = '';
        }

        function togglePin(id, e) {
            e.stopPropagation();
            chats[id].pinned = !chats[id].pinned;
            saveChats();
        }

        function shareMessage(text) {
            if (navigator.share) {
                navigator.share({ title: 'Ji Web Assistant', text: text });
            } else {
                navigator.clipboard.writeText(text);
                alert('Copied to clipboard!');
            }
        }

        function appendMessage(sender, text, imageBase64 = null, save = true) {
            const chatBox = document.getElementById('chat-box');
            const msgDiv = document.createElement('div');
            msgDiv.className = message ${sender === 'user' ? 'user-msg' : 'bot-msg'};
            
            let html = '';
            if (imageBase64) {
                html += <img src="data:image/jpeg;base64,${imageBase64}" class="chat-img" />;
            }
            html += <div>${text}</div>;
            
            if (sender === 'bot') {
                const safeText = text.replace(/'/g, "\\'").replace(/\n/g, " ");
                html += `
                <div class="action-btns">
                    <button class="action-btn" onclick="shareMessage('${safeText}')">Share</button>
                    <button class="action-btn" onclick="speakText('${safeText}')">🔊 Listen</button>
                </div>`;
            }
            msgDiv.innerHTML = html;
            
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;

            if (save) {
                if (!chats[currentChatId]) {
                    chats[currentChatId] = { title: text || "Image Analysis", messages: [], pinned: false };
                }
                chats[currentChatId].messages.push({ sender, text, image: imageBase64 });
                saveChats();
            }
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const prompt = input.value.trim();
            const imgData = selectedBase64Image;

            if (!prompt && !imgData) return;

            appendMessage('user', prompt, imgData);
            input.value = '';
            clearSelectedImage();

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt, image: imgData })
                });
                const data = await response.json();
                appendMessage('bot', data.response);
            } catch (err) {
                appendMessage('bot', 'Error getting response.');
            }
        }

        renderHistory();
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
    image_b64 = data.get("image", None)
    
    try:
        contents = []
        if image_b64:
            image_data = base64.b64decode(image_b64)
            contents.append({
                "mime_type": "image/jpeg",
                "data": image_data
            })
        if prompt:
            contents.append(prompt)
        elif image_b64 and not prompt:
            contents.append("Describe this image in detail.")

        response = model.generate_content(contents)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
