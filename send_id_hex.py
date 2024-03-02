import tkinter as tk
from tkinter import scrolledtext
import can
import threading
import random
import time

class UDSInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulator UDS")
        self.geometry("800x600")  # Dimensiunea ferestrei poate fi ajustată după necesități

        self.configure_gui()
        self.configure_bus()

    def configure_gui(self):
        # Terminal pentru mesaje trimise și primite
        self.terminal = scrolledtext.ScrolledText(self, height=20, width=100)
        self.terminal.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        tk.Label(self, text="Message ID (hex):").grid(row=1, column=0)
        self.entry_message_id = tk.Entry(self)
        self.entry_message_id.grid(row=1, column=1)

        tk.Label(self, text="Data (hex):").grid(row=2, column=0)
        self.entry_data = tk.Entry(self)
        self.entry_data.grid(row=2, column=1)

        send_button = tk.Button(self, text="Trimite Mesaj", command=self.send_uds_message)
        send_button.grid(row=3, column=0, columnspan=2)

        send_random_button = tk.Button(self, text="Trimite Mesaj Aleatoriu", command=self.send_random_uds_message)
        send_random_button.grid(row=3, column=2, columnspan=2)

    def configure_bus(self):
        # Configurarea canalului CAN (ajustați parametrii în funcție de nevoile dvs.)
        self.bus = can.interface.Bus(bustype='socketcan', channel='vcan0', bitrate=500000)
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def log_message(self, message):
        self.terminal.insert(tk.END, message + "\n")
        self.terminal.see(tk.END)

    def send_uds_message(self):
        message_id = int(self.entry_message_id.get(), 16)
        data = bytes.fromhex(self.entry_data.get())
        if len(data) > 7:
            self.iso_tp_send(message_id, data)
        else:
            self.send_can_frame(message_id, data)
        self.log_message(f"Mesaj UDS trimis: ID={hex(message_id)}, Data={data.hex()}")

    def send_random_uds_message(self):
        random_id = random.randint(0x0, 0x7FF)
        random_data = bytes([random.randint(0, 255) for _ in range(random.randint(1, 20))])
        if len(random_data) > 7:
            self.iso_tp_send(random_id, random_data)
        else:
            self.send_can_frame(random_id, random_data)
        self.log_message(f"Mesaj UDS aleatoriu trimis: ID={hex(random_id)}, Data={random_data.hex()}")

    def receive_messages(self):
        while True:
            message = self.bus.recv()
            if message:
                self.log_message(f"Mesaj primit: {message}")

    def iso_tp_send(self, message_id, data):
        length = len(data)
        if length > 4095:
            self.log_message("Eroare: Datele depășesc dimensiunea maximă suportată de ISO-TP.")
            return
        ff_data = [0x10 | (length >> 8), length & 0xFF] + list(data[:6])
        self.send_can_frame(message_id, bytes(ff_data))
        self.wait_for_flow_control()
        index = 6
        sequence_number = 1
        while index < length:
            remaining = length - index
            frame_length = min(self.MAX_CF_LENGTH, remaining)
            cf_data = [0x20 | (sequence_number & 0x0F)] + list(data[index:index+frame_length])
            self.send_can_frame(message_id, bytes(cf_data))
            index += frame_length
            sequence_number = (sequence_number % 15) + 1
            time.sleep(self.STMIN)

    def wait_for_flow_control(self):
        # Implementarea simplificată, în practică ar trebui să verificați Flow Control Frame
        pass

    def send_can_frame(self, message_id, data):
        message = can.Message(arbitration_id=message_id, data=data, is_extended_id=False)
        self.bus.send(message)

if __name__ == "__main__":
    app = UDSInterface()
    app.mainloop()
