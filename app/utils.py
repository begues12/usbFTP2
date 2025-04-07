import logging

def log_event(msg):
    with open("/var/log/wifi_setup.log", "a") as f:
        f.write(msg + "\n")
