
#!/bin/bash
cp checkForUpdate.service /etc/systemd/system/checkForUpdate.service
cp checkForUpdate.timer /etc/systemd/system/checkForUpdate.timer
systemctl daemon-reload
systemctl enable checkForUpdate.service checkForUpdate.timer
systemctl start checkForUpdate.service checkForUpdate.timer
