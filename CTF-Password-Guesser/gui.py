import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from tester import CTFTester

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class CTFGuesserApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CTF PASSWORD GUESSER")
        self.geometry("900x700")
        self.minsize(850, 650)

        self.tester = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=340, corner_radius=0, fg_color=("#1f1f1f", "#141414"))
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(13, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="[ CTF GUESSER ]", 
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color="#00FF66"
        )
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.lbl_ip = ctk.CTkLabel(self.sidebar_frame, text="Target IP Address (Private/Local):", font=ctk.CTkFont(size=12))
        self.lbl_ip.grid(row=1, column=0, padx=20, sticky="w")
        self.ent_ip = ctk.CTkEntry(self.sidebar_frame, width=290, placeholder_text="127.0.0.1")
        self.ent_ip.insert(0, "127.0.0.1")
        self.ent_ip.grid(row=2, column=0, padx=20, pady=(0, 10))

        self.lbl_port = ctk.CTkLabel(self.sidebar_frame, text="Target Port:", font=ctk.CTkFont(size=12))
        self.lbl_port.grid(row=3, column=0, padx=20, sticky="w")
        self.ent_port = ctk.CTkEntry(self.sidebar_frame, width=290, placeholder_text="5000")
        self.ent_port.insert(0, "5000")
        self.ent_port.grid(row=4, column=0, padx=20, pady=(0, 10))

        self.lbl_path = ctk.CTkLabel(self.sidebar_frame, text="Login Endpoint Path:", font=ctk.CTkFont(size=12))
        self.lbl_path.grid(row=5, column=0, padx=20, sticky="w")
        self.ent_path = ctk.CTkEntry(self.sidebar_frame, width=290, placeholder_text="/login")
        self.ent_path.insert(0, "/login")
        self.ent_path.grid(row=6, column=0, padx=20, pady=(0, 10))

        self.lbl_user = ctk.CTkLabel(self.sidebar_frame, text="Target Username:", font=ctk.CTkFont(size=12))
        self.lbl_user.grid(row=7, column=0, padx=20, sticky="w")
        self.ent_user = ctk.CTkEntry(self.sidebar_frame, width=290, placeholder_text="admin")
        self.ent_user.insert(0, "admin")
        self.ent_user.grid(row=8, column=0, padx=20, pady=(0, 10))

        self.lbl_wordlist = ctk.CTkLabel(self.sidebar_frame, text="Password Wordlist (.txt):", font=ctk.CTkFont(size=12))
        self.lbl_wordlist.grid(row=9, column=0, padx=20, sticky="w")
        
        self.wordlist_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.wordlist_frame.grid(row=10, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.ent_wordlist = ctk.CTkEntry(self.wordlist_frame, width=205, placeholder_text="Select .txt wordlist")
        self.ent_wordlist.pack(side="left", padx=(0, 5))
        
        self.btn_browse = ctk.CTkButton(self.wordlist_frame, width=80, text="Browse", command=self.browse_wordlist)
        self.btn_browse.pack(side="right")

        self.lbl_delay = ctk.CTkLabel(self.sidebar_frame, text="Delay Between Requests (s):", font=ctk.CTkFont(size=12))
        self.lbl_delay.grid(row=11, column=0, padx=20, sticky="w")
        self.ent_delay = ctk.CTkEntry(self.sidebar_frame, width=290, placeholder_text="0.2")
        self.ent_delay.insert(0, "0.2")
        self.ent_delay.grid(row=12, column=0, padx=20, pady=(0, 20))

        self.btn_start = ctk.CTkButton(self.sidebar_frame, text="START TEST", fg_color="#00aa44", hover_color="#008833", font=ctk.CTkFont(weight="bold"), command=self.start_test)
        self.btn_start.grid(row=14, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.btn_stop = ctk.CTkButton(self.sidebar_frame, text="STOP TEST", fg_color="#aa2222", hover_color="#881111", font=ctk.CTkFont(weight="bold"), state="disabled", command=self.stop_test)
        self.btn_stop.grid(row=15, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.main_frame = ctk.CTkFrame(self, fg_color=("#2b2b2b", "#1a1a1a"))
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.metrics_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.metrics_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        self.metrics_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_status = self.create_metric_card(self.metrics_frame, 0, "STATUS", "IDLE", "#00FF66")
        self.card_attempts = self.create_metric_card(self.metrics_frame, 1, "ATTEMPTS", "0 / 0", "#FFFFFF")
        self.card_candidate = self.create_metric_card(self.metrics_frame, 2, "CURRENT CANDIDATE", "None", "#FFCC00")

        self.progress_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.progress_frame.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        
        self.progressbar = ctk.CTkProgressBar(self.progress_frame, progress_color="#00FF66")
        self.progressbar.pack(fill="x", pady=(0, 5))
        self.progressbar.set(0.0)

        self.log_textbox = ctk.CTkTextbox(
            self.main_frame, 
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#00FF66",
            fg_color="#0d0d0d"
        )
        self.log_textbox.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="nsew")
        self.log_textbox.insert("0.1", "[*] CTF Password Guesser Initialized.\n[*] Ready for authorized lab testing against local environment.\n")
        self.log_textbox.configure(state="disabled")

        self.btn_clear = ctk.CTkButton(self.main_frame, text="Clear Logs", width=120, fg_color="#444444", hover_color="#333333", command=self.clear_logs)
        self.btn_clear.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="e")

    def create_metric_card(self, parent, col, title, initial_value, val_color):
        card = ctk.CTkFrame(parent, fg_color=("#333333", "#222222"), corner_radius=6)
        card.grid(row=0, column=col, padx=5, sticky="ew")
        
        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaaaaa")
        lbl_title.pack(padx=10, pady=(8, 2))
        
        lbl_val = ctk.CTkLabel(card, text=initial_value, font=ctk.CTkFont(size=13, weight="bold"), text_color=val_color)
        lbl_val.pack(padx=10, pady=(2, 8))
        card.value_label = lbl_val
        return card

    def browse_wordlist(self):
        filename = filedialog.askopenfilename(title="Select Password Wordlist", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            self.ent_wordlist.delete(0, tk.END)
            self.ent_wordlist.insert(0, filename)

    def log_message(self, message):
        self.after(0, lambda: self._append_log(message))

    def _append_log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def update_progress(self, current, total, candidate):
        self.after(0, lambda: self._apply_progress(current, total, candidate))

    def _apply_progress(self, current, total, candidate):
        fraction = current / total if total > 0 else 0.0
        self.progressbar.set(fraction)
        self.card_attempts.value_label.configure(text=f"{current} / {total}")
        self.card_candidate.value_label.configure(text=candidate)
        self.card_status.value_label.configure(text="TESTING", text_color="#FFCC00")

    def test_complete(self, success, status_text):
        self.after(0, lambda: self._finalize_test(success, status_text))

    def _finalize_test(self, success, status_text):
        color = "#00FF66" if success else "#FF5555"
        self.card_status.value_label.configure(text=status_text, text_color=color)
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        if success:
            messagebox.showinfo("CTF Success", "Valid credentials successfully discovered and logged!")
        else:
            messagebox.showinfo("Test Completed", f"Testing finished: {status_text}")

    def clear_logs(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("0.1", "end")
        self.log_textbox.configure(state="disabled")

    def start_test(self):
        ip = self.ent_ip.get().strip()
        port_str = self.ent_port.get().strip()
        path = self.ent_path.get().strip()
        username = self.ent_user.get().strip()
        wordlist = self.ent_wordlist.get().strip()
        delay_str = self.ent_delay.get().strip()

        if not ip or not port_str or not wordlist:
            messagebox.showerror("Validation Error", "Target IP, Port, and Wordlist are required fields.")
            return

        if not CTFTester.validate_target_ip(ip):
            messagebox.showerror("Safety Violation", f"Target IP '{ip}' is not permitted.\n\nSafety restrictions require localhost or private RFC1918 networks.")
            return

        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Validation Error", "Port must be a valid integer.")
            return

        try:
            delay = float(delay_str)
        except ValueError:
            delay = 0.2

        if not os.path.isfile(wordlist):
            messagebox.showerror("File Error", f"Wordlist file not found:\n{wordlist}")
            return

        confirm = messagebox.askyesno(
            "Confirm Authorization",
            f"You are about to run a password test against:\nTarget: http://{ip}:{port}{path}\nUser: {username}\n\nDo you confirm that this is your authorized local CTF lab?"
        )
        if not confirm:
            return

        self.progressbar.set(0.0)
        self.card_attempts.value_label.configure(text="0 / 0")
        self.card_candidate.value_label.configure(text="Initializing...")
        self.card_status.value_label.configure(text="STARTING", text_color="#00D2FF")

        config = {
            "ip": ip,
            "port": port,
            "path": path,
            "username": username,
            "wordlist": wordlist,
            "delay": delay,
            "max_attempts": 5000
        }

        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")

        self.tester = CTFTester(
            config=config,
            log_callback=self.log_message,
            progress_callback=self.update_progress,
            complete_callback=self.test_complete
        )
        self.tester.start()

    def stop_test(self):
        if self.tester:
            self.tester.stop()
            self.log_message("[*] Stop signal sent to background tester thread.")
        self.btn_stop.configure(state="disabled")
        self.card_status.value_label.configure(text="STOPPING", text_color="#FF5555")
