# config.py
# ---------------------------------------------------------------------------
# CTF Login Challenge - Configuration
#
# The challenge credentials live here, separate from the application logic,
# so the lab operator can change the password without touching app.py.
#
# LAB NOTE: This password is INTENTIONALLY weak and stored in plaintext.
# That is the point of the exercise -- it gives THC Hydra (or any other
# brute-force tool run separately on Kali Linux) something crackable in a
# controlled, authorized environment. Never reuse this pattern in a real
# application.
# ---------------------------------------------------------------------------

CHALLENGE_USERNAME = "admin"
CHALLENGE_PASSWORD = "letmein123"

# Flask secret key, used only for flashing messages / session cookies.
# Fine to leave as-is for a local lab; rotate if you expose this beyond
# localhost (you shouldn't).
SECRET_KEY = "ctf-lab-secret-key-change-if-exposed"
