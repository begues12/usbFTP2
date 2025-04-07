import subprocess

def connect_to_wifi(ssid, password):
    try:
        subprocess.run(["nmcli", "connection", "delete", ssid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        result = subprocess.run([
            "nmcli", "device", "wifi", "connect", ssid, "password", password
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            return True, "Conectado correctamente"
        else:
            return False, result.stderr.decode()

    except Exception as e:
        return False, str(e)
