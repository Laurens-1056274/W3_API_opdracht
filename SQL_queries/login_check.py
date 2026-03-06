import sqlite3

class search_user:
  def __init__(self, gebruikersnaam, ID):

    self.gebruikersnaam = gebruikersnaam
    self.ID = ID

  def search_leerling(self):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute('SELECT name,id FROM STUDENTS WHERE name = ? AND id = ?', (self.gebruikersnaam,self.ID))
    result = cur.fetchall()
    if len(result) == 1:
      result = True
    else:
      result = False
    cur.close()
    return result