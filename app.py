from flask import Flask, render_template, redirect, session, request, jsonify
import funcs

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
        return redirect("/login")
    
    return redirect("/play")

@app.route("/register")
def register():
    return render_template("logreg.html", action="r")

@app.route("/register/process", methods=["POST"])
def register_processing():
    nick = request.form["nick"]
    pw = request.form["pw"]

    out = funcs.register(nick, pw)

    if out[0] == True:
        session["logged_in"] = True
        session["nick"] = nick
        session["cart"] = []
        return redirect("/play")
    else:
        return render_template("logreg.html", action="r", msg=out[1])

@app.route("/login/process", methods=["POST"])
def login_processing():
    nick = request.form["nick"]
    pw = request.form["pw"]

    out = funcs.login(nick, pw)

    if out[0] == True:
        session["logged_in"] = True
        session["nick"] = nick
        session["cart"] = []
        return redirect("/play")
    else:
        return render_template("logreg.html", action="l", msg=out[1])

@app.route("/login")
def login():
    return render_template("logreg.html", action="l")

@app.route("/play")
def play():
    if not check_login_status():
        return redirect("/register")
    
    products = funcs.get_products()

    nick = session["nick"]
    session["products"] = products

    data = {"nick": nick, "products": session["products"]}
    return render_template("index.html", data=data)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/api/to_cart/<name>/<price>")
def to_cart(name, price):
    product = {"name": name, "price": price}
    cart = session["cart"]
    cart.append(product)
    session["cart"] = cart
    session.update()

    # doesnt quite work yet, but prob useful :(
    # ps = session["products"]
    # for cat in ps:
    #     if product in cat[1]:
    #         ps[cat].remove(product)

    # session["products"] = ps
    # session.update()

    print(session["cart"])
    return jsonify(session["cart"])

@app.route("/api/clear_cart")
def clear_cart():
    session["cart"] = []
    session.update()

    return jsonify(session["cart"])

@app.route("/api/get_cart")
def get_cart():
    return jsonify(session["cart"])

if __name__ == "__main__":
    app.run(debug=True, port=4900)