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
        return redirect('/error_page')
    
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
    return render_template("systeem/logout.html", user=session["user type"])

@app.route('/clear_session')
def clear_session():
    session.clear()
    return redirect('/')

@app.route('/error_page')
def error_page():
    return render_template("/systeem/error_page.html")

@app.route('/check_gebruiker', methods=['GET', 'POST'])
def check_gebruiker():
    email = request.form.get("email")
    # capitalize fisrt letter. I do this because the first letter needs to be capitalized for the DB
    email = email.capitalize()
    password = request.form.get("wachtwoord")
    session['email'] = email
    session['password'] = password
    try:
        if session["user type"] == "leerling":
            user_exists = search_user(session['email'],session['password']).search_leerling()
            session['gebruikersnaam'] = user_exists[0][1]
            session['gebruikers id'] = user_exists[0][0]
            if user_exists:
                return redirect("/studentdashboard")

        elif session["user type"] == "docent" :
            user_exists = search_user(session['email'],session['password']).search_docent()
            if user_exists:
                session['gebruikersnaam'] = user_exists[0][1]
                session['gebruikers id'] = user_exists[0][0]
                return redirect("/docentdashboard")
    except:
        return render_template("systeem/login.html", invalid_user=True, user=session["user type"])
    return render_template("systeem/login.html", invalid_user=True, user=session["user type"])

@app.route('/profiel')
def profiel():
    try:
        return render_template(
            "/pages/leerling/profiel.html",
            user=session["user type"],
            profiel=GetStudentData().profiel(session["user type"], session['gebruikersnaam'], session['gebruikers id']),
            email=session['email']
        )
    
    except:
        return redirect('/error_page')

@app.route('/leerdoelen')
def leerdoelen():
    learning_goals = GetStudentData().get_learning_goal_overview(session['gebruikers id'])
    return render_template(
        "/pages/leerling/leerdoelen.html",
        user=session["user type"],
        learning_goals=learning_goals)

@app.route('/docentdashboard')
def docent_voorbeeld():
    try:
        print(session["gebruikersnaam"])
    except:
        return redirect('/error_page')
        
    return render_template("/pages/docent/docentdashboard.html",
                           user=session["user type"],
                           name=session.get('gebruikersnaam'))

@app.route('/klas_analyse')
def klas_analyse():
    db = GetStudentData()
    data = db.get_class_analysis()
    db.close()
    return render_template("/pages/docent/klas_analyse.html",
                           user="docent",
                           data=data)

if __name__ == '__main__':
    app.run(debug=True)