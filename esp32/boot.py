# boot.py

# Before using please create secrets.py with your credentials:

# MQQT_SERVER = "",
# MQQT_USERNAME = ""
# MQQT_PASSWORD = ""

# WLAN_SSID = ""
# WLAN_PASSWORD = "''"

from secrets import WLAN_SSID, WLAN_PASSWORD

# print("sys loading...")
# import sys
# sys.path.reverse()


def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(WLAN_SSID, WLAN_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    return sta_if.ifconfig()[0]   

#import webrepl
#webrepl.start()



