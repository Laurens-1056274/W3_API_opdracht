from flask import Flask,redirect,render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'De server draait nu'

@app.route('/inzicht')
def inzicht_leerling():
    return render_template("leerling/inzicht_onderwerp_leerling.html")

@app.route('/login')
def login():
    return render_template("systeem/login.html")

@app.route('/check_gebruiker', methods=['GET', 'POST'])
def check_gebruiker():
    print("It works!")
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)