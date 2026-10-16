Datos
hostname:argos
WiFi Ip: [configurar]
USB Ip: [configurar]
login: [configurar]
Argos


Comandos:

*------------------------------------------------------------*
servicio argos hace que el programa arranque con el sistema


#Activa arranque automatico de argos
sudo systemctl enable argos.service

#Desactiva el arranque automatico de argos
sudo systemctl disable argos.service

#Reinicia el servicio de argos
sudo systemctl restart argos.service

#ver status de servicio argos:
sudo systemctl status argos.service

#Ver diario de systemd de servicio argos:
sudo journalctl -u argos.service -f

#Reiniciar servicios despues de modificar
sudo systemctl daemon-reload
sudo systemctl enable --now argos.service


#editar servicio
sudo nano /etc/systemd/system/argos.service


*------------------------------------------------------------*
Bluetooth

#Entrar al Bluetooth
bluetoothctl

*------------------------------------------------------------*