from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  # session key

# Dummy credentials
USER_CREDENTIALS = {
    "admin": "password123"
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    # Fetch API data
    try:
        response = requests.get("https://fetcher-theta.vercel.app/")
        response.raise_for_status()
        api_data = response.json()
    except Exception as e:
        api_data = {"error": str(e)}

    sms_numbers = ["+1234567890", "+0987654321"]

    return render_template("dashboard.html", data=api_data, sms_numbers=sms_numbers)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# For Vercel serverless
def handler(environ, start_response):
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return app(environ, start_response)

if __name__ == "__main__":
    app.run(debug=True)
