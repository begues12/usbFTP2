import logging
import os

def log_event(msg):
    with open("/var/log/wifi_setup.log", "a") as f:
        f.write(msg + "\n")
        
        

def initialize_usb_folder(usb_folder_path):
    """
    Verifica si la carpeta USB existe. Si no, la crea.
    """
    if not os.path.exists(usb_folder_path):
        os.makedirs(usb_folder_path)
        print(f"Carpeta USB creada en: {usb_folder_path}")
    else:
        print(f"Carpeta USB ya existe en: {usb_folder_path}")