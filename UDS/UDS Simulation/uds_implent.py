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
        self.current_session = "default"
        self.current_security_seed = None
        self.title("Client UDS")
        self.geometry("1680x600")
        self.bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
        self.init_ui()

    def init_ui(self):
        self.terminal_text = scrolledtext.ScrolledText(self, state='disabled', height=25, width=80)
        self.terminal_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.terminal_hex = scrolledtext.ScrolledText(self, state='disabled', height=25, width=120)
        self.terminal_hex.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        button_frame = tk.Frame(self)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        services = [
            ("Diagnostic Session Control", lambda: self.set_session("default")),
            ("Extended Session", lambda: self.set_session("extended")),
            ("ECU Reset", self.send_ecu_reset),
            ("Read Data By Identifier", lambda: self.send_request(0x22, "Read Data By Identifier")),
            ("Security Access", lambda: self.send_request(0x27, "Security Access")),
            ("Read DTC Information", lambda: self.send_request(0x19, "Read DTC Information")),
            ("Save Log to File", self.save_log),
            ("Clear Log", self.clear_terminals),
        ]

        for i, (name, action) in enumerate(services):
            button = tk.Button(button_frame, text=name, command=action)
            button.grid(row=i//3, column=i%3, sticky="ew", padx=5, pady=5)

        self.send_seed_button = tk.Button(button_frame, text="Send Security Seed", command=self.send_security_seed)
        self.send_seed_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

    def log_message(self, message, color, hex_format=False):
        terminal = self.terminal_hex if hex_format else self.terminal_text
        terminal.config(state='normal')
        terminal.tag_config(color, foreground=color)
        terminal.insert(tk.END, message + "\n", color)
        terminal.config(state='disabled')
        terminal.see(tk.END)

    def send_request(self, service_id, service_name):
    # Handling the Security Access request in the extended session
        if service_id == 0x27 and self.current_session == "extended":
            self.current_security_seed = random.randint(0, 0xFFFF)
            seed_hex = f'{self.current_security_seed:04X}'
            # Simulating receiving the security seed
            self.log_message(f"27 01 - Requesting security access", 'blue', hex_format=True)
            self.log_message(f"67 01 {seed_hex} - Received security seed", 'green', hex_format=True)
            self.server.log_message(f"Security access seed provided: {seed_hex}", 'green')
            # Simulating sending the request with '27 01' and receiving the seed
            command_data = [0x27, 0x01] + [0x00] * 6
            message = can.Message(arbitration_id=0x7df, data=command_data, is_extended_id=False)
            try:
                self.bus.send(message)
                self.log_message(f"Sent security access request: {' '.join([f'{byte:02X}' for byte in command_data])}", 'black', hex_format=True)
            except can.CanError:
                self.log_message("Error sending security access request", 'red')
            return  # Return after handling the security access to prevent further execution

    # Handling the Read Data By Identifier service outside of the default session
        if service_id == 0x22 and self.current_session != "default":
            self.simulate_negative_response(service_name)
            return

    # Handling other requests
        else:
            command_data = [service_id] + [0x00] * 7 if service_id != 0x22 else [0x22, 0xF1, 0x90] + [0x00] * 5
            message = can.Message(arbitration_id=0x7df, data=command_data, is_extended_id=False)
        try:
            self.bus.send(message)
            self.log_message(f"Sent: {service_name} (ID={service_id})", 'black', hex_format=False)
            self.log_message(f"CAN message sent: {' '.join([f'{byte:02X}' for byte in command_data])}", 'black', hex_format=True)
            self.simulate_ecu_response(service_id, service_name, command_data)
        except can.CanError:
            self.log_message("Error sending CAN message", 'red')


    def send_security_seed(self):
        if self.current_security_seed is not None:
        # Preparing to send back the security seed with '27 02' + seed
            command_data = [0x27, 0x02] + [self.current_security_seed >> 8, self.current_security_seed & 0xFF] + [0x00] * 4
            message = can.Message(arbitration_id=0x7df, data=command_data, is_extended_id=False)
        try:
            self.bus.send(message)
            seed_hex = f'{self.current_security_seed:04X}'
            self.log_message(f"Sent security seed back to ECU: 27 02 {seed_hex}", 'black', hex_format=True)
            self.server.log_message("Security access granted", 'green')
        except can.CanError:
            self.log_message("Send 67 02", 'red')
        else:
            self.log_message("Send seed and Positive Response", 'green')






    def send_ecu_reset(self):
        command_data = [0x11, 0x01] + [0x00] * 6
        message = can.Message(arbitration_id=0x7df, data=command_data, is_extended_id=False)
        try:
            self.bus.send(message)
            self.log_message("ECU Reset command sent", 'black')
            self.log_message(f"CAN message sent: {' '.join([f'{byte:02X}' for byte in command_data])}", 'black', hex_format=True)
            # After sending the reset command, ensure the session is set to default
            self.set_session("default")
        except can.CanError:
            self.log_message("Error sending ECU Reset CAN message", 'red')

    def set_session(self, session_type):
        command_data = [0x10, 0x01] + [0x00] * 6 if session_type == "default" else [0x10, 0x03] + [0x00] * 6
        self.current_session = session_type
        message = can.Message(arbitration_id=0x7df, data=command_data, is_extended_id=False)
        try:
            self.bus.send(message)
            self.log_message(f"Set to {session_type} session", 'black')
            self.log_message(f"Session control command sent: {' '.join([f'{byte:02X}' for byte in command_data])}", 'black', hex_format=True)
        except can.CanError:
            self.log_message("Error sending session control CAN message", 'red')

    def simulate_ecu_response(self, service_id, service_name, command_data):
        if service_id == 0x22:
            if self.current_session == "extended":
                vin_code = "1P8ZA1279SZ215470"
                vin_hex = ' '.join([f'{ord(c):02X}' for c in vin_code])
                response_data = f"62 F1 90 " + vin_hex
                self.server.log_message(f"Positive response for {service_name}: {response_data}", 'green')
            else:
                self.simulate_negative_response(service_name)
        else:
            is_positive_response = random.choice([True, False])
            if is_positive_response:
                response_data = "Positive response simulation for other services"
                self.server.log_message(f"Positive response for {service_name}: {response_data}", 'green')
            else:
                response_data = "Negative response simulation"
                self.server.log_message(f"Negative response for {service_name}: {response_data}", 'red')

    def simulate_negative_response(self, service_name):
        negative_response_data = "7F 22 31 00 00 00 00 00"   # 7F 22 - Negative response code, 31 - request out of range
        self.server.log_message(f"Negative response for {service_name}: {negative_response_data}", 'red')

    def save_log(self):
        log_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if log_file:
            with open(log_file, "w") as file:
                text_content = self.terminal_text.get("1.0", tk.END)
                hex_content = self.terminal_hex.get("1.0", tk.END)
                file.write("Terminal Text:\n" + text_content + "\nTerminal Hex:\n" + hex_content)
            self.log_message("Log saved successfully", 'green')

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