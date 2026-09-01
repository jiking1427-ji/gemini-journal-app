import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure API Key
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        user_text = data.get("text", "")
        
        if not user_text:
            return jsonify({"error": "No text provided"}), 400

        if not api_key:
            return jsonify({"error": "GEMINI_API_KEY is missing in Render environment variables"}), 500

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(user_text)
        
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '+_main__':
    app.run(host='0.0.0.0', port=10000)
