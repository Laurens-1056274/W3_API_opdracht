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

    if result is not None:
      password_bytes = self.password.encode('utf-8')
      isSamePassword = bcrypt.checkpw(password_bytes, result[0])
      print(isSamePassword)
      # Code works till here
      if isSamePassword:
        cur.execute('SELECT password FROM STUDENTS WHERE e_mail = ? AND password = ? ',(self.e_mail,result[0]))
        result = cur.fetchall()
        print(result[0])
        if len(result[0]) > 0: 
          pass
        else: 
          result = False 
        cur.close()
        return result
      else:
        result = False
    else:
      result = False

    cur.close()
    return result
  

  # def search_docent(self):
  #   con = sqlite3.connect("database.db")
  #   cur = con.cursor()

  #   cur.execute(
  #     'SELECT password FROM TEACHERS WHERE e_mail = ? ',
  #     (self.e_mail,)
  #   )

  #   result = cur.fetchone()

  #   if result is not None:
  #     print(result[0])

  #     password_bytes = self.password.encode('utf-8')

  #     isSamePassword = bcrypt.checkpw(password_bytes, result[0])

  #     print(isSamePassword)

  #     if isSamePassword:
  #       pass
  #     else:
  #       result = False
  #   else:
  #     result = False

  #   cur.close()
  #   return result