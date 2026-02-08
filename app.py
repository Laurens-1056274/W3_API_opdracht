from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'De server draait nu'

if __name__ == '__main__':
    app.run(debug=True)