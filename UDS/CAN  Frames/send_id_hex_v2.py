import tkinter as tk
from tkinter import scrolledtext
import can
import threading
import random
import time

# Configurarea canalului CAN
bus = can.interface.Bus(bustype='socketcan', channel='vcan0', bitrate=500000)

# Setări ISO-TP
MAX_CF_LENGTH = 7  # Lungimea maximă a datelor pentru un Consecutive Frame
STMIN = 0.02  # Timpul minim de așteptare între cadre consecutive, în secunde

def send_uds_message():
    message_id = int(entry_message_id.get(), 16)
    data = bytes.fromhex(entry_data.get())
    # Verifică dimensiunea datelor pentru a decide dacă să utilizeze ISO-TP
    if len(data) > 7:
        iso_tp_send(message_id, data)
    else:
        send_can_frame(message_id, data)
    terminal.insert(tk.END, f"Mesaj UDS trimis: ID={hex(message_id)}, Data={data.hex()}\n")
    terminal.see(tk.END)

def send_random_uds_message():
    # Generează un ID și date aleatorii pentru mesaj
    random_id = random.randint(0x0, 0x7FF)  # ID standard CAN
    random_data = bytes([random.randint(0, 255) for _ in range(random.randint(1, 20))])  # Date de 1-20 bytes
    if len(random_data) > 7:
        iso_tp_send(random_id, random_data)
    else:
        send_can_frame(random_id, random_data)
    terminal.insert(tk.END, f"Mesaj UDS aleatoriu trimis: ID={hex(random_id)}, Data={random_data.hex()}\n")
    terminal.see(tk.END)

def receive_messages():
    while True:
        message = bus.recv()
        if message:
            terminal.insert(tk.END, f"Mesaj primit: {message}\n")
            terminal.see(tk.END)

def iso_tp_send(message_id, data):
    length = len(data)
    if length > 4095:
        terminal.insert(tk.END, "Eroare: Datele depășesc dimensiunea maximă suportată de ISO-TP.\n")
        return

    # Trimiterea First Frame-ului
    ff_data = [0x10 | (length >> 8), length & 0xFF] + list(data[:6])
    send_can_frame(message_id, bytes(ff_data))
    wait_for_flow_control()

    # Trimiterea Consecutive Frames (CF)
    index = 6
    sequence_number = 1
    while index < length:
        remaining = length - index
        frame_length = min(MAX_CF_LENGTH, remaining)
        cf_data = [0x20 | (sequence_number & 0x0F)] + list(data[index:index+frame_length])
        send_can_frame(message_id, bytes(cf_data))
        index += frame_length
        sequence_number = (sequence_number % 15) + 1
        time.sleep(STMIN)  # Respectă STmin pentru controlul fluxului

def wait_for_flow_control():
    # Aici ar trebui să adăugați logica de așteptare și verificare a unui Flow Control Frame
    # Această implementare este simplificată și nu include această logică
    pass

def send_can_frame(message_id, data):
    uds_request = can.Message(arbitration_id=message_id, data=data, is_extended_id=False)
    bus.send(uds_request)

# Interfața grafică
window = tk.Tk()
window.title("Simulator UDS")

# Terminal
terminal = scrolledtext.ScrolledText(window, height=10)
terminal.grid(row=0, column=0, columnspan=3)

# Câmp de intrare pentru ID-ul mesajului
tk.Label(window, text="Message ID (hex):").grid(row=1, column=0)
entry_message_id = tk.Entry(window)
entry_message_id.grid(row=1, column=1)

# Câmp de intrare pentru date
tk.Label(window, text="Data (hex):").grid(row=2, column=0)
entry_data = tk.Entry(window)
entry_data.grid(row=2, column=1)

# Buton pentru trimiterea mesajului
send_button = tk.Button(window, text="Trimite Mesaj", command=send_uds_message)
send_button.grid(row=3, column=0, columnspan=2)

# Buton pentru trimiterea unui mesaj aleatoriu
send_random_button = tk.Button(window, text="Trimite Mesaj Aleatoriu", command=send_random_uds_message)
send_random_button.grid(row=3, column=2, columnspan=2)

# Pornește thread-ul de recepție în fundal
threading.Thread(target=receive_messages, daemon=True).start()

window.mainloop()
