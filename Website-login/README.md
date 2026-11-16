# CTF Login Challenge Lab

A small, deliberately vulnerable Flask login page built for **authorized**
cybersecurity education — practicing brute-force login testing with
**THC Hydra on Kali Linux** against a target you control, on your own local
network.

> ⚠️ **Scope reminder.** Only run Hydra (or any brute-force tool) against
> this application on a machine/network you own or have explicit written
> permission to test. Never point these tools at systems you don't control.

---

## What this project is

- A single-user login form (`admin` / a password stored in `config.py`).
- A Flask backend with one `POST /login` endpoint that takes standard form
  fields `username` and `password`.
- Consistent, predictable responses:
  - **Failure:** HTTP `401`, page always contains the text
    `Invalid username or password`.
  - **Success:** HTTP `302` redirect to `/success`, which renders a
    "CTF Challenge Completed" page.
- No rate limiting, lockouts, or CAPTCHAs — intentionally, so the lab target
  is crackable with Hydra in a reasonable time. This is a **training target**,
  not a production app.
- No brute-forcing or Hydra code inside the app itself. You run Hydra
  separately from Kali; this app only serves and validates logins.

## Project structure

```
CTF-Login-Lab/
│
├── app.py                # Flask app: routes, login validation
├── config.py             # Challenge username/password (edit here)
├── requirements.txt      # Python dependencies
├── README.md
│
├── templates/
│   ├── index.html        # Login page (+ error display)
│   └── success.html      # "CTF Challenge Completed" page
│
└── static/
    └── style.css          # Dark terminal / neon-green theme
```

---

## 1. Windows setup

### 1.1 Install Python

Install Python 3.10+ from https://www.python.org/downloads/windows/ if you
don't already have it. During install, check **"Add python.exe to PATH"**.

Verify in PowerShell or Command Prompt:

```powershell
python --version
```

### 1.2 Create and activate a virtual environment

From the project folder (`CTF-Login-Lab`):

```powershell
cd path\to\CTF-Login-Lab
python -m venv venv
venv\Scripts\activate
```

Your prompt should now show `(venv)` at the start of the line.

### 1.3 Install dependencies

```powershell
pip install -r requirements.txt
```

### 1.4 Run the Flask app

```powershell
python app.py
```

You should see output similar to:

```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://<your-LAN-ip>:5000
```

Leave this window open — it's your running server.

### 1.5 Open the website in a browser

On the same Windows machine, open:

```
http://127.0.0.1:5000
```

You should see the **CTF LOGIN CHALLENGE** page with the dark/neon terminal
theme.

### 1.6 Test login functionality manually

- Correct credentials (as set in `config.py`, default `admin` / `letmein123`):
  redirects to the **ACCESS GRANTED / CTF Challenge Completed** page.
- Incorrect credentials: page reloads with a red
  `[ERROR] Invalid username or password` message.

### 1.7 Check the raw HTTP request/response (optional but useful)

With the server running, open a **second** PowerShell window and use
`curl` (built into modern Windows) to see exactly what Hydra will see:

```powershell
curl -i -X POST http://127.0.0.1:5000/login -d "username=admin&password=wrongpass"
curl -i -X POST http://127.0.0.1:5000/login -d "username=admin&password=letmein123"
```

- The first call should return `HTTP/1.1 401 UNAUTHORIZED` and the body
  should contain `Invalid username or password`.
- The second call should return `HTTP/1.1 302 FOUND` with
  `Location: /success`.

These two distinguishable responses are exactly what Hydra's
`http-post-form` module uses to tell success from failure.

### 1.8 Prepare the environment for testing from Kali Linux

1. Find your Windows machine's local IP address:
   ```powershell
   ipconfig
   ```
   Look for the `IPv4 Address` under your active adapter (e.g.
   `192.168.56.10` for a host-only/NAT lab network).

2. Make sure both your Windows host and Kali VM are on the **same virtual
   network** (e.g. VirtualBox/VMware Host-Only or an isolated NAT network —
   not your home/production Wi-Fi).

3. Allow the app through Windows Firewall if prompted when you first ran
   `python app.py` (choose "Private networks" only — do not expose this to
   public networks).

4. Confirm reachability from Kali:
   ```bash
   curl -i http://<windows-ip>:5000/
   ```
   You should get the login page HTML back.

---

## 2. Testing with THC Hydra (run on Kali Linux — not part of this app)

This app does not include Hydra or any brute-force logic. You run Hydra
separately, from your Kali box, against the Flask server above.

Example command (adjust `<windows-ip>` and wordlists to your lab):

```bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt \
  <windows-ip> http-post-form \
  "/login:username=^USER^&password=^PASS^:F=Invalid username or password" \
  -s 5000 -V
```

Breaking that down:

- `-l admin` — fixed username (matches `config.py`).
- `-P <wordlist>` — password list to try (put the real password in it for a
  quick training run, e.g. a small custom `.txt` file).
- `http-post-form` — Hydra module for HTML form logins.
- `"/login:username=^USER^&password=^PASS^:F=Invalid username or password"`
  — the path, the POST body template, and the **failure condition** string
  that matches this app's consistent error message.
- `-s 5000` — the port Flask is listening on.
- `-V` — verbose, shows each attempt.

When Hydra finds the correct password, it will report a valid pair; you can
confirm it manually by logging in through the browser and seeing the
**CTF Challenge Completed** page.

---

## 3. Changing the challenge credentials

Edit `config.py`:

```python
CHALLENGE_USERNAME = "admin"
CHALLENGE_PASSWORD = "letmein123"
```

Restart `python app.py` after any change for it to take effect.

---

## 4. Notes on design choices

- **No rate limiting / lockouts / CAPTCHA**: intentional, so the lab target
  is actually testable with brute-force tools. Do not deploy this pattern
  outside an isolated lab.
- **Plaintext password in `config.py`**: intentional, for a simple, readable
  training target. Never do this in a real application — use salted password
  hashing (e.g. `werkzeug.security.generate_password_hash`) in production.
- **`debug=False`** in `app.py`: keeps HTTP responses simple and consistent,
  which makes Hydra's failure-string matching reliable, and avoids leaking a
  Werkzeug debugger on a lab network.
