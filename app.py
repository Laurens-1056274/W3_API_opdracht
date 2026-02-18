from flask import Flask,redirect,render_template,session,request
from login_check import search_user

app = Flask(__name__)

# secrect key is needed to run sessions, so you can't just remove this line (It also cant be empty)
app.secret_key = "_"

@app.route('/')
def hello_world():
    session.clear()
    return 'De server draait nu'

@app.route('/login')
def login():
    return render_template("systeem/login.html", invalid_user=False)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/error_page')
def error_page():
    return render_template("/systeem/error_page.html")

#--------------------------------------------------------------------------------------------------------------------

@app.route('/check_gebruiker', methods=['GET', 'POST'])
def check_gebruiker():
    gebruikersnaam = request.form.get("gebruikersnaam")
    ID = request.form.get("ID")
    session['gebruikersnaam'] = gebruikersnaam
    session['gebruikers id'] = ID
    user_exists = search_user(session['gebruikersnaam'],session['gebruikers id']).search_leerling()
    if user_exists:
        # If user_exist send to the page listed beneath (atm only students exist)
        session["typeUser"] = "leerling"
        return redirect("/leerling/kernwoord_en_onderwerp")
    # user does noet exist, make user redo the login
    return render_template("systeem/login.html", invalid_user=True)

#--------------------------------------------------------------------------------------------------------------------

@app.route('/leerling/kernwoord_en_onderwerp', methods=['GET', 'POST'])
def leerling_kernwoord_en_onderwerp():
    try:
        return render_template('leerling/kernwoord_en_onderwerp.html',user_type=session["typeUser"])
    except:
        return redirect('/error_page')

if __name__ == '__main__':
    app.run(debug=True)