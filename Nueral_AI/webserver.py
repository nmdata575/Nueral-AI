# webserver.py
from flask import Flask, request, render_template_string, jsonify
import os
from jan_ai_integration import JanAI

app = Flask(__name__)

# Initialize Jan AI client - Replace with your actual API key
# You can set this as an environment variable for security
JAN_AI_API_KEY = "5757068924"
jan_ai_client = JanAI(JAN_AI_API_KEY)

# Simple HTML interface for direct AI interaction
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=0.8">
    <title>Nueral AI Interface</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            color: #333;
        }
        .container {
            background-color: smoke;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 25px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2c3e50;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            box-sizing: border-box;
            font-size: 16px;
        }
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        button {
            background-color: #3498db;
            color: smoke;
            padding: 14px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        .chat-container {
            margin-top: 30px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .chat-header {
            background-color: #3498db;
            color: white;
            padding: 12px 15px;
            font-weight: 600;
        }
        .chat-messages {
            max-height: 400px;
            overflow-y: auto;
            padding: 15px;
            background-color: #f8f9fa;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 8px;
            line-height: 1.5;
        }
        .user-message {
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
            text-align: right;
        }
        .ai-message {
            background-color: #f1f8e9;
            border-left: 4px solid #4caf50;
        }
        .status {
            margin-top: 15px;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
            display: none;
        }
        .loading {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            color: #856404;
        }
        .error {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            color: #721c24;
        }
        .success {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            color: #155724;
        }
        .model-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .model-option {
            flex: 1;
        }
        .model-option input {
            margin-right: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Nueral AI </h1>
        
        <form id="aiForm">
            <div class="form-group">
                <label for="userMessage">Your Message:</label>
                <textarea id="userMessage" name="userMessage" placeholder="Type your message here..." required></textarea>
            </div>
            
            <div class="form-group">
                <label>Model Selection:</label>
                <div class="model-selector">
                    <div class="model-option">
                        <input type="radio" id="model1" name="modelSelect" value="gpt-4" checked>
                        <label for="model1">GPT-4</label>
                    </div>
                    <div class="model-option">
                        <input type="radio" id="model2" name="modelSelect" value="gpt-3.5-turbo">
                        <label for="model2">GPT-3.5</label>
                    </div>
                    <div class="model-option">
                        <input type="radio" id="model3" name="modelSelect" value="claude-2">
                        <label for="model3">Claude 2</label>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label for="temperature">Temperature (0.0-1.0):</label>
                <input type="range" id="temperature" name="temperature" min="0" max="1" step="0.1" value="0.7">
                <span id="tempValue">0.7</span>
            </div>
            
            <button type="submit">Send to Nueral AI</button>
        </form>
        
        <div id="statusMessage" class="status"></div>
        
        <div class="chat-container">
            <div class="chat-header">Conversation History</div>
            <div id="chatMessages" class="chat-messages">
                <div class="message ai-message">Welcome! Send a message to interact with Nueral AI directly.</div>
            </div>
        </div>
    </div>

    <script>
        // Update temperature value display
        const tempSlider = document.getElementById('temperature');
        const tempValue = document.getElementById('tempValue');
        
        tempSlider.addEventListener('input', function() {
            tempValue.textContent = this.value;
        });
        
        // Handle form submission
        document.getElementById('aiForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const statusDiv = document.getElementById('statusMessage');
            const chatMessages = document.getElementById('chatMessages');
            const userMessage = document.getElementById('userMessage').value.trim();

            if (!userMessage) return;

            // Add user message to chat
            const userMsgDiv = document.createElement('div');
            userMsgDiv.className = 'message user-message';
            userMsgDiv.innerHTML = '<strong>You:</strong> ' + userMessage;
            chatMessages.appendChild(userMsgDiv);

            // Clear input
            document.getElementById('userMessage').value = '';

            // Show loading status
            statusDiv.className = 'status loading';
            statusDiv.textContent = 'Sending request to Jan.ai...';
            statusDiv.style.display = 'block';

            // Prepare data as JSON object
            const jsonData = {
                userMessage: userMessage,
                modelSelect: formData.get('modelSelect'),
                temperature: formData.get('temperature')
            };

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json' // Important!
                    },
                    body: JSON.stringify(jsonData)
                });

                const result = await response.json();

                if (result.error) {
                    statusDiv.className = 'status error';
                    statusDiv.textContent = 'Error: ' + result.error;
                } else {
                    statusDiv.className = 'status success';
                    statusDiv.textContent = 'Response received successfully!';

                    // Add AI response to chat
                    const aiMsgDiv = document.createElement('div');
                    aiMsgDiv.className = 'message ai-message';
                    aiMsgDiv.innerHTML = '<strong>Jan.ai:</strong> ' + result.response;
                    chatMessages.appendChild(aiMsgDiv);

                    // Scroll to bottom
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            } catch (error) {
                statusDiv.className = 'status error';
                statusDiv.textContent = 'Network error: ' + error.message;
                console.error("Network Error:", error);
            } finally {
                // Hide status after 3 seconds
                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 3000);

                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Check if data is JSON
        if request.is_json:
            data = request.get_json()
            user_message = data.get('userMessage', '').strip()
            model = data.get('modelSelect', 'gpt-4')
            temperature = float(data.get('temperature', 0.7))
        else:
            # Fallback for form data (though your JS sends JSON)
            user_message = request.form.get('userMessage', '').strip()
            model = request.form.get('modelSelect', 'gpt-4')
            temperature = float(request.form.get('temperature', 0.7))

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Prepare messages for API call
        messages = [
            {"role": "user", "content": user_message}
        ]

        # Call Jan AI API
        ai_response = jan_ai_client.chat(messages, model, temperature)

        # Handle response
        if 'error' in ai_response:
            return jsonify({"error": ai_response['error']}), 500

        response_text = ""
        if 'choices' in ai_response and len(ai_response['choices']) > 0:
            response_text = ai_response['choices'][0]['message']['content'].strip()
        else:
            response_text = "No response from Jan.ai"

        return jsonify({
            "response": response_text
        })

    except Exception as e:
        # Log the error for debugging
        print(f"Error in /chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Direct Jan.ai Web Interface...")
    print("No registration required - just load the page and start chatting!")
    print("Make sure to set your JAN_AI_API_KEY environment variable")
    print("Visit http://localhost:5000 to begin interacting with Jan.ai")
    app.run(host='0.0.0.0', port=5000, debug=True) # Changed this line
