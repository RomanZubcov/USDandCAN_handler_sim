import tkinter as tk
from tkinter import scrolledtext, filedialog
import random
import can

class UDSInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulator UDS")
        self.geometry("1680x600")  
        
        # Mărit dimensiunea terminalelor
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

        self.save_log_button = tk.Button(button_frame, text="Salvează Log", command=self.save_log)
        self.save_log_button.grid(row=1, column=2, sticky="ew", padx=5, pady=5)

    def log_message(self, message, color, hex_format=False):
        terminal = self.terminal_hex if hex_format else self.terminal_text
        terminal.config(state='normal')
        terminal.tag_config(color, foreground=color)
        terminal.insert(tk.END, message + "\n", color)
        terminal.config(state='disabled')
        terminal.see(tk.END)

    def send_request(self, service_id, service_name):
        command_data = [service_id] + [0x00] * 7  # DLC = 8 bytes
        message = can.Message(arbitration_id=0x7df, data=command_data, is_extended_id=False)
        try:
            self.bus.send(message)
            self.log_message(f"Trimis: {service_name} (ID={service_id})", 'black', hex_format=False)
            self.log_message(f"Mesaj CAN trimis: {message}", 'black', hex_format=True)
            self.simulate_ecu_response(service_id, service_name)  # Adăugat pentru a simula răspunsurile
        except can.CanError:
            self.log_message("Eroare la trimiterea mesajului CAN", 'red')

    def simulate_ecu_response(self, service_id, service_name):
        # Simularea răspunsurilor ECU aleatorii
        is_positive_response = random.choice([True, False])
        if is_positive_response:
            response_id = service_id + 0x40
            response_data = f"{response_id:02X}" + ' ' + ' '.join(['FF' for _ in range(7)])
            self.log_message(f"Răspuns pozitiv pentru {service_name}", 'green', hex_format=False)
            self.log_message(f"Răspuns Hex: {response_data}", 'green', hex_format=True)
        else:
            response_id = 0x7F
            response_data = f"{response_id:02X}" + ' ' + ' '.join(['00' for _ in range(7)])
            self.log_message(f"Răspuns negativ pentru {service_name}", 'red', hex_format=False)
            self.log_message(f"Răspuns Hex: {response_data}", 'red', hex_format=True)

    def save_log(self):
        log_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if log_file:
            with open(log_file, "w") as file:
                text_content = self.terminal_text.get("1.0", tk.END)
                hex_content = self.terminal_hex.get("1.0", tk.END)
                file.write("Terminal Text:\n" + text_content + "\nTerminal Hex:\n" + hex_content)

if __name__ == "__main__":
    app = UDSInterface()
    app.mainloop()
