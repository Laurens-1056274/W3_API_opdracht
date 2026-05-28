import sqlite3
import bcrypt

class search_user:
  def __init__(self, e_mail, password):

    self.e_mail = e_mail
    self.password = password
    self.result = None


  #only searches for studens atm
  def search_user(self, userType):
    print('ekjfoifwnoeggw')
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute(f'SELECT password FROM {userType} WHERE e_mail = ? ', (self.e_mail,))
    check_email = cur.fetchone()
    cur.close()

    if check_email is not None:
      password_bytes = self.password.encode('utf-8')
      isSamePassword = bcrypt.checkpw(password_bytes, check_email[0])
      print(isSamePassword)
      print(self.password)
      if isSamePassword == True:
        # If true, make a querie that grabs he username and the gebruikers id. result send sthat back
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute(f'SELECT id,name FROM {userType} WHERE e_mail = ? ', (self.e_mail,))
        self.result = cur.fetchall()
        cur.close()
        print(self.result)
        return self.result
      else:
        return self.result