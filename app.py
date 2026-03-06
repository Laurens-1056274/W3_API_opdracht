from flask import Flask,redirect,render_template,session,request
from SQL_queries.login_check import search_user
from SQL_queries.get_student_data import *
import statistics

app = Flask(__name__)

# secrect key is needed to run sessions, so you can't just remove this line (It also cant be empty)
app.secret_key = "_"

@app.route('/')
def landlingpage():
    return render_template("landingpage.html")


@app.route('/login_leerling')
def login_leerling():
    session["user type"] = "leerling"
    return render_template("systeem/login.html", invalid_user=False, user=session["user type"])

@app.route('/login_docent')
def login_docent():
    session["user type"] = "docent"
    return render_template("systeem/login.html", invalid_user=False, user=session["user type"])

@app.route("/logout")
def logout():
    return render_template("systeem/uitloggen.html", 
                           page_title="confirmatie uitloggen", 
                           description="Pagina om uit te loggen, klik op de uitloggen knop om uit te loggen.")

@app.route('/clear_session')
def clear_session():
    session.clear()
    return redirect('/')

@app.route('/error_page')
def error_page():
    return render_template("/systeem/error_page.html")

@app.route('/check_gebruiker', methods=['GET', 'POST'])
def check_gebruiker():
    gebruikersnaam = request.form.get("gebruikersnaam")
    ID = request.form.get("ID")
    session['gebruikersnaam'] = gebruikersnaam
    session['gebruikers id'] = ID
    if session["user type"] == "leerling":
        user_exists = search_user(session['gebruikersnaam'],session['gebruikers id']).search_leerling()
        if user_exists:
            return redirect("/leerling/kernwoord_en_onderwerp")

    elif session["user type"] == "docent" :
        user_exists = search_user(session['gebruikersnaam'],session['gebruikers id']).search_docent()
        if user_exists:
            return redirect("docent/voorbeeld")
    

    return render_template("systeem/login.html", invalid_user=True, user=session["user type"])


# Deze flask route doet niks, het bestaat alleen om te testen of de login werkt
@app.route('/docent/voorbeeld')
def docent_voorbeeld():
    try:
        print(session["gebruikersnaam"])
    except:
        return redirect('/error_page')
        
    return render_template("/pages/docent/test.html")


@app.route('/leerling/kernwoord_en_onderwerp', methods=['GET', 'POST'])
def leerling_kernwoord_en_onderwerp():
    # Check if user is logged in, else go to error page
    try:
        student_data = GetStudentData()
        learning_goals = student_data.get_learning_goal_overview(session["gebruikers id"])
    except:
        return redirect('/error_page')
    

    return render_template(
        "leerling/kernwoord_en_onderwerp.html",
        name=session["gebruikersnaam"],
        learning_goals=learning_goals)

if __name__ == '__main__':
    app.run(debug=True)