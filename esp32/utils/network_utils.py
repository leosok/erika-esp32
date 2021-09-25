import network
import utime as time

def scan_wlan(max=5):
    """
    Scans Wlans
    Returns: Array of Tuples (ssid, strength)
    """
    wlan = network.WLAN()
    wlan.disconnect()
    networks_found = wlan.scan()[:max]
    networks_array = []
    for n in networks_found:
        ssid = n[0]
        strength = n[3]
        networks_array.append((ssid, strength))
    print(networks_array)
    return networks_array

def do_connect(wlan_ssid, wlan_password, timeout_sec=5):
    """
    Connects to a Wlan using credentials

    Returns: ip_adresse(str) if successful or False
    """
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(wlan_ssid, wlan_password)
        print('network config:', sta_if.ifconfig())
        t = time.ticks_ms()
        while not sta_if.isconnected() and time.ticks_diff(time.ticks_ms(), t) < timeout_sec * 1000:
            # wait for 5 seconds
            pass
    ip_adress = sta_if.ifconfig()[0]
    if not ip_adress == '0.0.0.0':
        return ip_adress
    else:
        return False 


def get_wlan_strength(strength):
    """
    Returns Wlan-Strength from 1 to 3 (strongest)
    """
    if strength >= -60:
        return 3
    if strength >= -67:
        return 2
    if strength >= -70:
        return 1