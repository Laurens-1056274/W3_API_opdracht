from get_student_data import GetStudentData
from flask import Flask, jsonify, redirect, render_template, session, request
from login_check import search_user

app = Flask(__name__)

# secrect key is needed to run sessions, so you can't just remove this line (It also cant be empty)
app.secret_key = "_"
invalid_user = False

@app.route('/')
def landlingpage():
    return render_template("landingpage.html")

@app.route('/studentdashboard')
def studentdashboard():
    if not session.get('gebruikers id'):
        return redirect('/login')
    return render_template(
        "pages/leerling/studentdashboard.html",
        name=session.get('gebruikersnaam'),
        student_id=session.get('gebruikers id'),
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

@app.route('/login')
def login():
    return render_template("systeem/login.html", invalid_user=invalid_user)

@app.route('/check_gebruiker', methods=['GET', 'POST'])
def check_gebruiker():
    gebruikersnaam = request.form.get("gebruikersnaam")
    ID = request.form.get("ID")
    session['gebruikersnaam'] = gebruikersnaam
    session['gebruikers id'] = ID
    user_exists = search_user(session['gebruikersnaam'],session['gebruikers id']).search_leerling()
    if user_exists:
        # If user_exist send to the page listed beneath
        return redirect("/studentdashboard")
    # user does noet exist, make user redo the login
    invalid_user = True
    return render_template("systeem/login.html", invalid_user=invalid_user)

if __name__ == '__main__':
    app.run(debug=True)