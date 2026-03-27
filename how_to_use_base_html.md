# How to use
To use base.html in your page you need to put: ```{% extends "base.html" %} {%block content%}``` in the beginning of the file
in the end of the file, add: ```{% endblock %}```
in studentendasboard.html you can see how it is succesfully is used

# How to change where the lnik in the navbar send you to
You need to adjust this in navbar.html

example and what to change if you want to use it:

```
{%if user == "leerling"%}
<div class="nav-item">
	<!--change the error_page in url_for('error_page') for the function name for the flask route you want to route to-->
	<a href="{{url_for('error_page')}}">
	<i class="fa fa-chart-bar"></i>
	<span>Voortgang</span>
	</a>
</div>
{% endif %}
```

```{%if user == "leerling"%}``` checks if the user="leerling". if the user is leerling it displays the rest of the code till the `{% endif %}`
so if for example you want only docenten to see a certain nav-item, write ```{%if user == "docent"%}``` instead
```<a href="{{url_for('error_page')}}">``` change 'error_page' to the name of the definition you want the link to go to

Let's say if you press a button you want to be send to:

```
@app.route('/')
def landlingpage():
    return render_template("systeem/landingpage.html")
```

you would change ```<a href="{{url_for('error_page')}}">``` to ```<a href="{{url_for('landingpage')}}">```

> [!WARNING]
> right now because the dasboard is in base.html DO NOT use base.html in files where you do not want the navbar (for example the landingpage)

Joris might know a way to fix this


I think that's about it ^^
feel free to ask if something is still unclear (I am not certain if i can help tho but i will try LoL)

Have a nice day,
Laurens
