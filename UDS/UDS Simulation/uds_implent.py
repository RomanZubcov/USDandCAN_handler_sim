import tkinter as tk
from tkinter import scrolledtext, filedialog
import random
import can

class ServerInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Server UDS")
        self.geometry("950x500")
        self.terminal_hex = scrolledtext.ScrolledText(self, state='disabled', height=25, width=110)
        self.terminal_hex.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def log_message(self, message, color):
        self.terminal_hex.config(state='normal')
        self.terminal_hex.tag_config(color, foreground=color)
        self.terminal_hex.insert(tk.END, message + "\n", color)
        self.terminal_hex.config(state='disabled')
        self.terminal_hex.see(tk.END)

class UDSInterface(tk.Tk):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.current_session = "default"  # 'default' or 'extended'
        self.title("Client UDS")
        self.geometry("1680x600")

        self.terminal_text = scrolledtext.ScrolledText(self, state='disabled', height=25, width=80)
        self.terminal_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.terminal_hex = scrolledtext.ScrolledText(self, state='disabled', height=25, width=120)
        self.terminal_hex.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.bus = can.interface.Bus(channel='vcan0', bustype='socketcan')

        services = [
            ("Diagnostic Session Control", 0x10),
            ("ECU Reset", 0x11),
            ("Read Data By Identifier", 0x22),
            ("Security Access", 0x27),
            ("Read DTC Information", 0x19)
        ]

        button_frame = tk.Frame(self)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        for i, (name, id) in enumerate(services):
            row = i // 3
            column = i % 3
            button = tk.Button(button_frame, text=name, command=lambda service_id=id, service_name=name: self.send_request(service_id, service_name))
            button.grid(row=row, column=column, sticky="ew", padx=5, pady=5)

        extended_session_button = tk.Button(button_frame, text="Extended Session", command=lambda: self.set_session("extended"))
        extended_session_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        self.save_log_button = tk.Button(button_frame, text="Salveaza Log", command=self.save_log)
        self.save_log_button.grid(row=2, column=2, sticky="ew", padx=5, pady=5)

        
        clear_button = tk.Button(button_frame, text="Clear log", command=self.clear_terminals)
        clear_button.grid(row=1, column=2, sticky="ew", padx=5, pady=5)

    def log_message(self, message, color, hex_format=False):
        terminal = self.terminal_hex if hex_format else self.terminal_text
        terminal.config(state='normal')
        terminal.tag_config(color, foreground=color)
        terminal.insert(tk.END, message + "\n", color)
        terminal.config(state='disabled')
        terminal.see(tk.END)

    def send_request(self, service_id, service_name):
        if service_id == 0x22 and self.current_session != "extended":
            self.log_message("Comanda 'Read Data By Identifier' necesită sesiunea extended.", 'red')
            return
        
        command_data = [service_id] + [0x00] * 7
        if service_id == 0x10:  # Handle session control commands specifically
            command_data[1] = 0x01 if self.current_session == "default" else 0x03

        message = can.Message(arbitration_id=0x7df, data=command_data, is_extended_id=False)
        try:
            self.bus.send(message)
            self.log_message(f"Trimis: {service_name} (ID={service_id})", 'black')
            self.log_message(f"Mesaj CAN trimis: {message}", 'black', hex_format=True)
            self.simulate_ecu_response(service_id, service_name, command_data)
        except can.CanError:
            self.log_message("Eroare la trimiterea mesajului CAN", 'red')

    def simulate_ecu_response(self, service_id, service_name, command_data):
         
        if service_id == 0x22 and self.current_session == "extended":
            # Specific pentru "Read Data By Identifier" în sesiunea extended
            vin_code = "1P8ZA1279SZ215470"
            vin_hex = ' '.join([f'{ord(c):02X}' for c in vin_code])
            response_data = f"62 F1 90 " + vin_hex
            self.server.log_message(f"Raspuns pozitiv pentru {service_name}: {response_data}", 'green')
        else:
            is_positive_response = random.choice([True, False])
            if is_positive_response:
                response_data = "Positive response simulation for other services"
                self.server.log_message(f"Raspuns pozitiv pentru {service_name}: {response_data}", 'green')
            else:
                response_data = "Negative response simulation"
                self.server.log_message(f"Raspuns negativ pentru {service_name}: {response_data}", 'red')

    def set_session(self, session_type):
        self.current_session = session_type
        session_id = 0x01 if session_type == "default" else 0x03
        self.send_request(0x10, f"Set {session_type.capitalize()} Session")

    def save_log(self):
        log_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if log_file:
            with open(log_file, "w") as file:
                text_content = self.terminal_text.get("1.0", tk.END)
                hex_content = self.terminal_hex.get("1.0", tk.END)
                file.write("Terminal Text:\n" + text_content + "\nTerminal Hex:\n" + hex_content)

    def clear_terminals(self):
        self.terminal_text.config(state='normal')
        self.terminal_hex.config(state='normal')
        self.terminal_text.delete('1.0', tk.END)
        self.terminal_hex.delete('1.0', tk.END)
        self.terminal_text.config(state='disabled')
        self.terminal_hex.config(state='disabled')

if __name__ == "__main__":
    server_app = ServerInterface()
    client_app = UDSInterface(server=server_app)
    server_app.mainloop()
    client_app.mainloop()
