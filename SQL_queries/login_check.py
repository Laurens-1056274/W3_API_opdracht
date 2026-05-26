import sqlite3
import bcrypt

class search_user:
  def __init__(self, e_mail, password):

    self.e_mail = e_mail
    self.password = password

  def search_leerling(self):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute('SELECT password FROM STUDENTS WHERE e_mail = ? ', (self.e_mail,))
    result = cur.fetchone()
    cur.close()

    if result is not None:
      password_bytes = self.password.encode('utf-8')
      isSamePassword = bcrypt.checkpw(password_bytes, result[0])
      print(isSamePassword)
      print(self.password)
      if isSamePassword == True:
        return result
      else:
        result = False
        return result