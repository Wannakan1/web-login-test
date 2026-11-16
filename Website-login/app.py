# app.py
# ---------------------------------------------------------------------------
# CTF Login Challenge - Flask Backend
#
# Purpose: A deliberately simple, Hydra-compatible login endpoint for use in
# an authorized, local cybersecurity training lab (e.g. Kali Linux + THC
# Hydra brute-force practice). This app performs NO attack/testing logic of
# its own -- it only serves the login form and validates credentials.
# ---------------------------------------------------------------------------

from flask import Flask, render_template, request, redirect, url_for, session
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY


@app.route("/", methods=["GET"])
def index():
    """Render the login page."""
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    """
    Validate login credentials submitted via POST.

    Hydra / automation compatibility notes:
    - Accepts standard HTML form POST data (application/x-www-form-urlencoded),
      which is what Hydra's http-post-form module sends.
    - Expects fields named exactly 'username' and 'password'.
    - Failure always returns the SAME response text/status so Hydra's
      "failure condition" string matching works reliably.
    - Success returns a clearly different response/status so Hydra can
      detect the hit.
    """
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if username == config.CHALLENGE_USERNAME and password == config.CHALLENGE_PASSWORD:
        # Successful login -> mark session and redirect to the success page.
        session["authenticated"] = True
        session["username"] = username
        return redirect(url_for("success"))

    # Failed login -> re-render the login page with a clear, CONSISTENT
    # error message/status. The exact string "Invalid username or password"
    # is used every time so it can be set as Hydra's failure string.
    return render_template(
        "index.html",
        error="Invalid username or password"
    ), 401


@app.route("/success", methods=["GET"])
def success():
    """Render the CTF Challenge Completed page, but only for authenticated sessions."""
    if not session.get("authenticated"):
        return redirect(url_for("index"))
    return render_template("success.html", username=session.get("username", "admin"))


@app.route("/logout", methods=["GET"])
def logout():
    """Clear the session and return to the login page."""
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Bind to all interfaces so the app is reachable from a Kali VM on the
    # same local network/host-only adapter. Debug is off by default for a
    # cleaner, more predictable HTTP response set (important for Hydra).
    app.run(host="0.0.0.0", port=5000, debug=False)
