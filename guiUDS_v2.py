import tkinter as tk
from tkinter import scrolledtext
import random

class UDSInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulator UDS")
        self.geometry("900x500")  # Ajustez dimensiunea ferestrei pentru a se potrivi cu noile elemente

        # Terminal pentru text
        self.terminal_text = scrolledtext.ScrolledText(self, state='disabled', height=20, width=50)
        self.terminal_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Terminal pentru hex
        self.terminal_hex = scrolledtext.ScrolledText(self, state='disabled', height=20, width=50)
        self.terminal_hex.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Definirea serviciilor UDS
        services = [
            ("Diagnostic Session Control", 0x10),
            ("ECU Reset", 0x11),
            ("Read Data By Identifier", 0x22),  
            ("Security Access", 0x27),
            ("Read DTC Information", 0x19)
        ]

        # Frame pentru butoane
        button_frame = tk.Frame(self)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        # Adaugarea butoanelor într-o structură organizată
        for i, (name, id) in enumerate(services):
            row = i // 3  # Distribuim butoanele pe mai multe rânduri
            column = i % 3
            button = tk.Button(button_frame, text=name, command=lambda service_id=id, service_name=name: self.send_request(service_id, service_name))
            button.grid(row=row, column=column, sticky="ew", padx=5, pady=5)

    def log_message(self, message, color, hex_format=False):
        terminal = self.terminal_hex if hex_format else self.terminal_text
        terminal.config(state='normal')
        terminal.tag_config(color, foreground=color)
        terminal.insert(tk.END, message + "\n", color)
        terminal.config(state='disabled')
        terminal.see(tk.END)

    def simulate_ecu_response(self, service_id, service_name):
        is_positive_response = random.choice([True, False])
        if is_positive_response:
            response_id = service_id + 0x40
            response_data = f"{response_id:02X}" + ' ' + ' '.join(['FF' for _ in range(7)])
            self.log_message(f"Răspuns pozitiv pentru {service_name}", 'green', hex_format=False)
            self.log_message(f"Răspuns Hex: {response_data}", 'green', hex_format=True)
        else:
            response_id = 0x7E
            response_data = f"{response_id:02X}" + ' ' + ' '.join(['00' for _ in range(7)])
            self.log_message(f"Răspuns negativ pentru {service_name}", 'red', hex_format=False)
            self.log_message(f"Răspuns Hex: {response_data}", 'red', hex_format=True)

    def send_request(self, service_id, service_name):
        command_data = f"{service_id:02X}" + ' ' + ' '.join(['00' for _ in range(7)])  # DLC = 8 bytes
        self.log_message(f"Trimis: {service_name} (ID={service_id})", 'black', hex_format=False)
        self.log_message(f"Mesaj Hex trimis: {command_data}", 'black', hex_format=True)
        self.simulate_ecu_response(service_id, service_name)

if __name__ == "__main__":
    app = UDSInterface()
    app.mainloop()
