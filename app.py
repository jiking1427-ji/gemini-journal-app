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
        
        /* Sidebar Styles */
        .sidebar { width: 260px; background: #1e1e2d; color: #fff; display: flex; flex-direction: column; padding: 15px; }
        .new-chat-btn { background: #4b6cb7; color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .history-section { flex: 1; overflow-y: auto; }
        .history-title { font-size: 12px; color: #8a8a9e; margin-bottom: 10px; text-transform: uppercase; }
        .chat-list { list-style: none; }
        .chat-item { padding: 10px; margin-bottom: 5px; background: #2b2b3d; border-radius: 6px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; font-size: 14px; }
        .chat-item.pinned { border-left: 4px solid #f1c40f; }

        /* Main Chat Area */
        .chat-container { flex: 1; display: flex; flex-direction: column; height: 100vh; }
        .chat-header { background: #fff; padding: 15px 20px; border-bottom: 1px solid #ddd; font-weight: bold; color: #333; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        
        /* Message Bubbles */
        .message { max-width: 75%; padding: 12px 16px; border-radius: 12px; font-size: 15px; line-height: 1.5; position: relative; }
        .user-message { background: #4b6cb7; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
        .bot-message { background: #ffffff; color: #333; align-self: flex-start; border-bottom-left-radius: 2px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .preview-img { max-width: 200px; border-radius: 8px; margin-bottom: 8px; display: block; }
        
        /* Audio/Action Controls */
        .bot-actions { margin-top: 8px; display: flex; gap: 10px; color: #666; font-size: 14px; }
        .action-btn { cursor: pointer; border: none; background: none; color: #555; }
        .action-btn:hover { color: #4b6cb7; }

        /* Input Area */
        .input-area { background: #fff; padding: 15px 20px; border-top: 1px solid #ddd; }
        .input-wrapper { display: flex; align-items: center; background: #f8f9fa; border: 1px solid #ccc; border-radius: 25px; padding: 5px 15px; }
        .input-wrapper input[type="text"] { flex: 1; border: none; background: transparent; padding: 10px; outline: none; font-size: 15px; }
        .icon-btn { background: none; border: none; font-size: 18px; color: #666; cursor: pointer; margin: 0 5px; }
        .send-btn { background: #4b6cb7; color: white; border: none; width: 35px; height: 35px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .send-btn:hover { background: #182848; }

        /* Hidden File Inputs */
        input[type="file"] { display: none; }
    </style>
</head>
<body>

    <!-- Sidebar / Chat History -->
    <div class="sidebar">
        <button class="new-chat-btn" onclick="startNewChat()"><i class="fas fa-plus"></i> New Chat</button>
        <div class="history-section">
            <div class="history-title">Chat History</div>
            <ul class="chat-list" id="chatList">
                <li class="chat-item pinned"><span><i class="fas fa-thumbtack"></i> Important Project</span></li>
                <li class="chat-item"><span><i class="far fa-comment"></i> General Inquiry</span></li>
            </ul>
        </div>
    </div>

    <!-- Main Workspace -->
    <div class="chat-container">
        <div class="chat-header">AI Assistant Studio</div>
        
        <!-- Messages Display -->
        <div class="chat-box" id="chatBox">
            <div class="message bot-message">
                வணக்கம்! நான் உங்களுக்கு எப்படி உதவட்டும்? கீழே உள்ள பட்டன்களை பயன்படுத்தி படங்கள் அனுப்பலாம் அல்லது தட்டச்சு செய்யலாம்.
                <div class="bot-actions">
                    <button class="action-btn" onclick="speakText(this)"><i class="fas fa-volume-up"></i></button>
                </div>
            </div>
        </div>

        <!-- Input Control Panel -->
        <div class="input-area">
            <div class="input-wrapper">
                <!-- Gallery Button -->
                <button class="icon-btn" title="Gallery" onclick="document.getElementById('galleryInput').click()">
                    <i class="fas fa-image"></i>
                </button>
                <input type="file" id="galleryInput" accept="image/*" onchange="handleImageUpload(event)">

                <!-- Camera Button -->
                <button class="icon-btn" title="Camera" onclick="document.getElementById('cameraInput').click()">
                    <i class="fas fa-camera"></i>
                </button>
                <input type="file" id="cameraInput" accept="image/*" capture="environment" onchange="handleImageUpload(event)">

                <!-- Text Input -->
                <input type="text" id="userInput" placeholder="Ask anything..." onkeydown="checkEnter(event)">

                <!-- Send Button -->
                <button class="send-btn" id="sendBtn" onclick="sendMessage()">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chatBox');
        const userInput = document.getElementById('userInput');
        let selectedImageSrc = null;

        // Send Message Functionality
        function sendMessage() {
            const text = userInput.value.trim();
            if (text === "" && !selectedImageSrc) return;

            // Display User Message
            const userDiv = document.createElement('div');
            userDiv.className = 'message user-message';
            
            if (selectedImageSrc) {
                const img = document.createElement('img');
                img.src = selectedImageSrc;
                img.className = 'preview-img';
                userDiv.appendChild(img);
            }

            if (text !== "") {
                const textNode = document.createElement('p');
                textNode.innerText = text;
                userDiv.appendChild(textNode);
            }

            chatBox.appendChild(userDiv);
            userInput.value = '';
            selectedImageSrc = null;
            chatBox.scrollTop = chatBox.scrollHeight;

            // Generate Automated Bot Response (Gemini/ChatGPT Style)
            setTimeout(() => {
                generateBotResponse(text);
            }, 800);
        }

        // Handle Enter Key Press
        function checkEnter(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Image Selection Handler (Gallery & Camera)
        function handleImageUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    selectedImageSrc = e.target.result;
                    alert("படம் தேர்ந்தெடுக்கப்பட்டது! இப்போது Send பட்டனை அழுத்தவும்.");
                }
                reader.readAsDataURL(file);
            }
        }

        // Text-to-Speech (Voice Reader)
        function speakText(button) {
            const messageContent = button.parentElement.parentElement.childNodes[0].nodeValue || button.parentElement.parentElement.innerText;
            
            // Stop existing speech
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(messageContent);
            utterance.lang = 'ta-IN'; // Set language (Tamil/English supported by system)
            
            window.speechSynthesis.speak(utterance);
        }

        // Bot Response Generator
        function generateBotResponse(userQuery) {
            const botDiv = document.createElement('div');
            botDiv.className = 'message bot-message';
            
            let replyText = "உங்கள் செய்தி பெறப்பட்டது: " + (userQuery ? userQuery : "படம் அனுப்பப்பட்டுள்ளது.");
            
            botDiv.innerHTML = `
                ${replyText}
                <div class="bot-actions">
                    <button class="action-btn" onclick="speakText(this)"><i class="fas fa-volume-up"></i> Listen</button>
                </div>
            `;

            chatBox.appendChild(botDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        // New Chat Creation
        function startNewChat() {
            chatBox.innerHTML = `
                <div class="message bot-message">
                    புதிய உரையாடல் தொடங்கப்பட்டது. என்ன உதவி வேண்டும்?
                    <div class="bot-actions">
                        <button class="action-btn" onclick="speakText(this)"><i class="fas fa-volume-up"></i></button>
                    </div>
                </div>
            `;
        }
    </script>
</body>
</html>
