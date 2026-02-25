from flask import Flask,redirect,render_template,session,request
from SQL_queries.login_check import search_user
from SQL_queries.get_student_data import *

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
    # Check if user is logged in, else go to error page
    try:
        session["typeUser"] = session["typeUser"]
    except:
        return redirect('/error_page')
    
    student_data = GetStudentData()

    list_all_learning_goal_id = []
    list_all_snapshot_id = []
    list_all_snapshot_taxonomy = []
    list_all_learning_goal_title = []
    entries = student_data.collect_entries(session['gebruikers id'])

    for entry in entries:
        entry_id = entry[0]

        learning_goal_id_list = student_data.learning_goal_id(entry_id)

        for learning_goal in learning_goal_id_list:
            learning_goal_id = learning_goal[0]
            list_all_learning_goal_id.append(learning_goal_id)

            learning_goal_title_list = student_data.learning_goal_title(learning_goal_id)

            for title in learning_goal_title_list:
                learning_goal_title = title[0]
                list_all_learning_goal_title.append(learning_goal_title)

                snapshot_id_list = student_data.snapshot_id(learning_goal_id)

                for snapshot in snapshot_id_list:
                    snapshot_id = snapshot[0]
                    list_all_snapshot_id.append(snapshot_id)

                    taxonomy_data = student_data.snapshot_taxonomy(snapshot_id)
                    for taxonomy_row in taxonomy_data:
                        list_all_snapshot_taxonomy.append(taxonomy_row)

    return render_template('leerling/kernwoord_en_onderwerp.html',user_type=session["typeUser"], name=session['gebruikersnaam'], data=list_all_learning_goal_title)

if __name__ == '__main__':
    app.run(debug=True)