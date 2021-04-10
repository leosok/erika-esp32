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


def scan_wlan(max=5):
    import network
    wlan = network.WLAN()
    do_connect()
    wlan.disconnect()
    networks_found = wlan.scan()[:max]
    for n in networks_found:
        print("ssid: {}; strength: {}".format(n[0], n[3]))
    print("-----")

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(WLAN_SSID, WLAN_PASSWORD)
        print('network config:', sta_if.ifconfig())
        while not sta_if.isconnected():
            pass
    return sta_if.ifconfig()[0]   

#import webrepl
#webrepl.start()



