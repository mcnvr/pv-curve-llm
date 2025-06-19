from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from ai_service import get_ai_response_stream
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def status():
    return "Flask server is running"

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question']
        
        if not question.strip():
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        def generate():
            try:
                for chunk in get_ai_response_stream(question):
                    # Format as Server-Sent Events
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Send end signal
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            generate(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            }
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)