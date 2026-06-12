from SQL_queries.get_student_data import GetStudentData
from SQL_queries.get_class_data import GetClassData
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
    try:
        if session["user type"] == "leerling":
            pass
        else:
            return redirect('/')
    except:
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
    
    subject = request.args.get('subject', '').strip()
    
    try:
        db = GetStudentData()
        learning_goals = db.get_learning_goal_overview(int(student_id), subject if subject else None)
        db.close()
        return jsonify({"learningGoals": learning_goals, "subject": subject if subject else "AlleVakken"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/student/keywords')
def api_student_keywords():
    student_id = session.get('gebruikers id')
    if not student_id:
        return jsonify({"error": "Niet ingelogd"}), 401
    try:
        db = GetStudentData()
        keywords = db.get_keyword_analysis(int(student_id))
        db.close()
        return jsonify({"keywords": keywords})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/classes')
def api_classes():
    if not session.get('gebruikers id'):
        return jsonify({"error": "Niet ingelogd"}), 401

    try:
        db = GetClassData()
        classes = db.get_classes()
        db.close()
        return jsonify({"classes": classes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/class/voortgang')
def api_class_voortgang():
    if not session.get('gebruikers id'):
        return jsonify({"error": "Niet ingelogd"}), 401

    klas = request.args.get('klas', '').strip()
    if not klas:
        return jsonify({"error": "Query parameter 'klas' is verplicht"}), 400

    try:
        db = GetClassData()
        learning_goals = db.get_learning_goal_overview_for_class(klas)
        db.close()
        return jsonify({"class": klas, "learningGoals": learning_goals})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/class/leerlingen')
def api_class_leerlingen():
    if not session.get('gebruikers id'):
        return jsonify({"error": "Niet ingelogd"}), 401

    klas = request.args.get('klas', '').strip()
    if not klas:
        return jsonify({"error": "Query parameter 'klas' is verplicht"}), 400

    try:
        db = GetClassData()
        students = db.get_students_overview_for_class(klas)
        db.close()
        return jsonify({"class": klas, "students": students})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/class/analyse')
def api_class_analyse():
    if not session.get('gebruikers id'):
        return jsonify({"error": "Niet ingelogd"}), 401

    klas = request.args.get('klas', '').strip()
    
    try:
        db = GetStudentData()
        data = db.get_class_analysis(klas if klas else None)
        db.close()
        return jsonify({
            "class": klas if klas else "Alle klassen",
            "data": {
                "goals": [dict(row) for row in data['goals']],
                "taxonomy": [dict(row) for row in data['taxonomy']],
                "keywords": [dict(row) for row in data['keywords']]
            }
        })
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
            user_exists = search_user(
                session['email'], session['password']).search_user('students')
            session['gebruikersnaam'] = user_exists[0][1]
            session['gebruikers id'] = user_exists[0][0]
            if user_exists:
                return redirect("/studentdashboard")

        elif session["user type"] == "docent":
            user_exists = search_user(
                session['email'], session['password']).search_user('teachers')
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
            profiel=GetStudentData().profiel(
                session["user type"], session['gebruikersnaam'], session['gebruikers id']),
            email=session['email']
        )

    except:
        return redirect('/error_page')


@app.route('/leerdoelen')
def leerdoelen():
    learning_goals = GetStudentData().get_learning_goal_overview(
        session['gebruikers id'])
    return render_template(
        "/pages/leerling/leerdoelen.html",
        user=session["user type"],
        learning_goals=learning_goals)


@app.route('/kernwoorden')
def kernwoorden():
    try:
        if session["user type"] == "leerling":
            pass
        else:
            return redirect('/')
    except:
        return redirect('/error_page')
    
    return render_template(
        "/pages/leerling/kernwoorden.html",
        user=session["user type"],
        name=session.get('gebruikersnaam'),
        student_id=session.get('gebruikers id')
    )


@app.route('/docentdashboard')
def docent_voorbeeld():
    try:
        if session["user type"] == "docent":
            pass
        else:
            return redirect('/')

    except:
        return redirect('/error_page')

    classes = []
    try:
        db = GetClassData()
        classes = db.get_classes()
        db.close()
    except:
        classes = []

    return render_template("/pages/docent/docentdashboard.html",
                           user=session["user type"],
                           name=session.get('gebruikersnaam'),
                           classes=classes)

@app.route('/klas_analyse')
def klas_analyse():
    try:
        if session["user type"] == "docent":
            pass
        else:
            return redirect('/')

    except:
        return redirect('/error_page')

    return render_template("/pages/docent/klas_analyse.html",
                           user=session["user type"],
                           name=session.get('gebruikersnaam'))

if __name__ == '__main__':
    app.run(debug=True)
