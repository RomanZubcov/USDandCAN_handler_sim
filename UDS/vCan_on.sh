#!/bin/bash

# Deschide un nou terminal și execută comenzile următoare în el
gnome-terminal -- bash -c "
# Configurarea unui nou dispozitiv virtual CAN numit vcan0
sudo modprobe vcan;
sudo ip link add dev vcan0 type vcan;
sudo ip link set up vcan0;

echo 'Interfața Virtual CAN (vcan0) a fost creată și activată.';

# Folosește candump pentru a asculta pe interfața vcan0
echo 'Se așteaptă mesaje pe vcan0...';
candump vcan0;
"

