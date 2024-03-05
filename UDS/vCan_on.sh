#!/bin/bash

# Deschide un nou terminal si executa comenzile urmatoare în el
gnome-terminal -- bash -c "
# Configurarea unui nou dispozitiv virtual CAN numit vcan0
sudo modprobe vcan;
sudo ip link add dev vcan0 type vcan;
sudo ip link set up vcan0;

echo 'Interfata Virtual CAN (vcan0) a fost creata si activata.';

# Foloseste candump pentru a asculta pe interfata vcan0
echo 'Se asteaptă mesaje pe vcan0...';
candump vcan0;
"

