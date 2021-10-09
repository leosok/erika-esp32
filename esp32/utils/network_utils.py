import network
import utime as time

def scan_wlan(max=5):
    """
    Scans Wlans
    Returns: Array of Tuples (ssid, strength)
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    networks_found = wlan.scan()[:max]
    networks_array = []
    for n in networks_found:
        ssid_byte_str = n[0]
        ssid_str = ssid_byte_str.decode('utf-8').strip("'")
        strength = n[3]
        networks_array.append((ssid_str, strength))
    print(networks_array)
    return networks_array

def do_connect(wlan_ssid, wlan_password, timeout_sec=5):
    """
    Connects to a Wlan using credentials

    Returns: ip_adresse(str) if successful or False
    """
    sta_if = network.WLAN(network.STA_IF)
    ip_adress = sta_if.ifconfig()[0]
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(wlan_ssid, wlan_password)
        print('network config:', sta_if.ifconfig())
        t = time.ticks_ms()
        while not sta_if.isconnected() and time.ticks_diff(time.ticks_ms(), t) < timeout_sec * 1000:
            # wait for 5 seconds
            time.sleep_ms(500)
        ip_adress = sta_if.ifconfig()[0]
        if not ip_adress == '0.0.0.0':
            print("OK: connected to network '{}' with password '{}'".format(wlan_ssid, wlan_password))
            return ip_adress
        else:
            print("ERROR: connecting to network '{}' with password '{}'".format(wlan_ssid, wlan_password))
            return False 
    else:
        return ip_adress
    


def get_wlan_strength(strength):
    """
    Returns Wlan-Strength from 1 to 3 (strongest)
    """
    # print("strength: {}".format(strength))
    strength = int(strength)
    if strength >= -60:
        return 3
    elif strength >= -67:
        return 2
    else:
        return 1