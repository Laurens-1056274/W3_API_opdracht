import sqlite3

class search_user:
  def __init__(self, e_mail, password):

    self.e_mail = e_mail
    self.password = password

  def search_leerling(self):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute('SELECT id,name FROM STUDENTS WHERE e_mail = ? AND password = ?', (self.e_mail,self.password))
    result = cur.fetchall()
    print(result)
    if len(result) == 1:
      pass
    else:
      result = False
    cur.close()
    return result
  
  def search_docent(self):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute('SELECT id,name FROM TEACHERS WHERE e_mail = ? AND password = ?', (self.e_mail,self.password))
    result = cur.fetchall()
    print(result)
    if len(result) == 1:
      pass
    else:
      result = False
    cur.close()
    return result