<!-- LTex: language=nl -->

# Werkplaats 3 (2026), Rest, 1C4 - Lion

Gegevens:

- Team naam: 1C4 - Lion
- Teamleden:
  - Joris Oosterveld (1083819)
  - Maarten de Leeuw van Weenen (1044232)
  - Laurens Hill (1056274)
  - Aletta van der Star (1129629)
  - Shaemar Sardjo (1046782)

## Requirements

Python (versie 3.13.0) https://www.python.org/downloads/ (Wanneer je python installeert, klik het hokje "Add python.exe to PATH" aan) </br>
Git (versie 2.44.0) https://git-scm.com/downloads

Volg deze handleiding om de repository van GitHub te klonen. (clone met de HTTPS key):
https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository 

## Installatie
### Stap 1: Virtual Environment (VENV)

Om de applicatie te kunnen starten moet er eerst een VENV worden aangemaakt.

Na het installeren van de python versie, maak, activeer, en installeer de benodigde modules voor de python omgeving met de volgende commando's in de terminal:

Navigeer naar de root van het project:

```shell
cd .\wp3-2026-rest-1c4-lion
```

Maak de omgeving:

```shell
py -m venv .venv
```

Activeer de omgeving:

```shell
.\.venv\Scripts\activate
```

Installeer de modules:

```shell
pip install -r requirements.txt
```


### Stap 2: Maak de database

Na het opstarten van de omgeving, graag de database maken met de volgende commando. Deze zal dus volgens het diagram hierboven gemaakt worden:

```shell
py .\generate_database.py
```

### Stap 3: Start de app

De app wordt opgestart met het volgende commando:

```shell
py .\app.py
```

Dit brengt je naar de landing page waar je kan inloggen als student of docent

![Landing Page](landing-page.png)

Hiervoor dus de hebben we een aantal testusers:

| Type    | Email          | Password                              |
| ------- | -------------- | ------------------------------------- |
| Docent  | john@gmail.com | zie `teachers` tabel in `database.db` |
| Student | sam@gmail.com  | zie `students` tabel in `database.db` |

<!-- How to login

first make sure you have the updated database.md. If this is not the case you will not be able to login. To get the latest database.db, run generate
database.py. If you already have a database.py, delete this first.
After doing that you can login with:
    the email of the user: This is the name of user + @gmail.com
    The password of the user: This is a random password each time you run generate_database.py
both can be found in the database.db

The email and password shown in the database are examples.
If the database ever contains real login data, those values should be used instead of the generated ones. -->
