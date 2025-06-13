from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Flask server is running"

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)