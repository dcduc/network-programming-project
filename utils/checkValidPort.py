import subprocess


def get_listening_ports_server():
    result = subprocess.run(["netstat", "-an"], capture_output=True, text=True)

    output = result.stdout
    lines = output.splitlines()
    listening_ports = []

    for line in lines:
        if "LISTEN" in line:
            parts = line.split()
            address_port = parts[1]
            if ":" in address_port:
                port = address_port.split(":")[-1]
                listening_ports.append(port)

    return listening_ports

def get_listening_ports_vps():
    pem_file = "C:\\Users\\duyng\\Downloads\\duynv.pem"
    ssh_user = "nvm"
    ssh_host = "172.207.92.76"
    ssh_command = [
        "ssh",
        "-i", pem_file,
        f"{ssh_user}@{ssh_host}",
        "netstat -tuln"
    ]

    result = subprocess.run(ssh_command, capture_output=True, text=True)

    output = result.stdout

    lines = output.splitlines()

    listening_ports = []

    for line in lines:
        if 'LISTEN' in line:
            parts = line.split()
            address_port = parts[3]
            if ':' in address_port:
                port = address_port.split(':')[-1]
                listening_ports.append(port)

    return listening_ports

def get_listening_ports():
    listening_ports_server = get_listening_ports_server()
    listening_ports_vps = get_listening_ports_vps()

    ans = listening_ports_server + listening_ports_vps

    return list(set(ans))
