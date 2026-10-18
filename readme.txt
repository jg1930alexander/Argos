Datos
hostname:argos
WiFi: [configurar]
USB: [configurar]
Usuario: [configurar]
Argos


Comandos:

*------------------------------------------------------------*
servicio argos hace que el programa arranque con el sistema

Al abrir argos.py se muestra si el arranque automático está activado o desactivado.
En el menú:
1. Inicia ARGOS en la terminal.
2. Activa el arranque automático con sudo systemctl enable argos.service.
3. Desactiva el arranque automático con sudo systemctl disable argos.service.
4. Muestra los logs con sudo journalctl -u argos.service -f. Ctrl+C vuelve al menú.
5. Cierra el menú.


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
Git Hub

git status --short --branch
git diff
git add archivo1.py archivo2.py
git diff --cached --check
git commit -m "Descripción de los cambios"
git push origin pruebas
git status --short --branch

*------------------------------------------------------------*