from SQL_queries.get_student_data import GetStudentData
from SQL_queries.login_check import search_user
from flask import Flask, jsonify, redirect, render_template, session, request

app = Flask(__name__)

# secrect key is needed to run sessions, so you can't just remove this line (It also cant be empty)
app.secret_key = "_"

@app.route('/')
def landlingpage():
    return render_template("systeem/landingpage.html")

@app.route('/studentdashboard')
def studentdashboard():
    if not session.get('gebruikers id'):
        return redirect('/login')
    
    return render_template(
        "pages/leerling/studentdashboard.html",
        name=session.get('gebruikersnaam'),
        student_id=session.get('gebruikers id'),
        user=session["user type"]
    )

@app.route('/api/student/voortgang')
def api_student_voortgang():
    student_id = session.get('gebruikers id')
    if not student_id:
        return jsonify({"error": "Niet ingelogd"}), 401
    try:
        db = GetStudentData()
        learning_goals = db.get_learning_goal_overview(int(student_id))
        db.close()
        return jsonify({"learningGoals": learning_goals})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
            return redirect("/studentdashboard")

    elif session["user type"] == "docent" :
        user_exists = search_user(session['gebruikersnaam'],session['gebruikers id']).search_docent()
        if user_exists:
            return redirect("docent/voorbeeld")
    

    return render_template("systeem/login.html", invalid_user=True, user=session["user type"])


# Deze flask route doet niks, het bestaat alleen om te testen of de login werkt
@app.route('/docent/voorbeeld')
def docent_voorbeeld():
    try:
        print(session["user type"])
    except:
        return redirect('/error_page')
        
    return render_template(
        "pages/docent/test.html",
        user=session["user type"],)


if __name__ == '__main__':
    app.run(debug=True)