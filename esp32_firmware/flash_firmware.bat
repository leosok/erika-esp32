@echo off

echo "Devices on COM" 
reg query HKLM\HARDWARE\DEVICEMAP\SERIALCOMM  
:: alternate method
:: rshell --list

:: Promt User for Com Port
set /p COM_PORT=COM Port: 

:: Set Firmware Path
set FIRMWARE_PATH="firmware_esp32_erika_ttgo_240.bin"
:: Set Baud Rate
set BAUD_RATE=921600


:: flash a firmware on a esp32 using esptool.py
::esptool.py --port %COM_PORT% --baud %BAUD_RATE% erase_flash
::esptool.py --port %COM_PORT% --baud %BAUD_RATE% write_flash -fm dio 0x1000 %FIRMWARE_PATH%

::wait for user to press enter
echo Wait for reboot
echo 
pause
echo 

cd ..
cd esp32

rshell -b %BAUD_RATE% -p  %COM_PORT%  "rsync -m . /pyboard" 