import sqlite3
import bcrypt
# check if password is the same: isSamePassword = bcrypt.hashpw(new_password, stored_hash)
# source https://stackoverflow.com/questions/41857055/can-i-decrypt-a-bcrypt-hashed-password-with-werkzeug-securitys-check-password-h

class search_user:
  def __init__(self, e_mail, password):

    self.e_mail = e_mail
    self.password = password
    # If you want to check password easier, comment out row 10-13 (this will make it so the db displays the actual passwords)
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    self.password = hash
    print(self.password)



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