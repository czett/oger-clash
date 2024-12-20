from flask import Flask, render_template, redirect, session

app = Flask(__name__)
app.secret_key = "lieufhqlerguhöqerughöqerough"

def check_login_status():
    if session.get("logged_in"):
        if session["logged_in"]:
            return True
    else:
        session["logged_in"] = False
        return False
    
    return True

@app.route("/")
def start():
    if not check_login_status():
        return redirect("/register")
    
    return redirect("/play")

@app.route("/register")
def register():
    return render_template("logreg.html", action="r")

@app.route("/login")
def login():
    return render_template("logreg.html", action="l")

@app.route("/play")
def play():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=4900)