import socket
import argparse
import time
from concurrent.futures import ThreadPoolExecutor

# Argparse
parser = argparse.ArgumentParser()

parser.add_argument("--host", required=True)
parser.add_argument("--ports", required=True)

args = parser.parse_args()

host = args.host
port_range = args.ports


if host == "localhost":
    host = "127.0.0.1"
elif host == "scanme":
    host = "scanme.nmap.org"


start_port, end_port = [
    int(x) for x in port_range.split("-")
]




# Port scan
print(f"Scanning {host} (ports {port_range}) with 50 threads...")

open_count = 0

def scan(port):
    global open_count
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    try:
        result = sock.connect_ex((host, port))

        if result == 0:
            open_count += 1
            try:
                service = socket.getservbyport(port, "tcp")
            except OSError:
                service = "unknown port"
                
            print(f"Port {port} ({service}): OPEN")

    except Exception as e:
        print(f"Error at port {port}: {e}")

    finally:
        sock.close()


# Thread 돌리기
start_time = time.time()

with ThreadPoolExecutor(max_workers=50) as executor:

    for port in range(start_port, end_port + 1):
        executor.submit(scan, port)
        
end_time = time.time()
total_time = end_time - start_time

total_ports = end_port - start_port + 1
closed_count = total_ports - open_count

print(
    f"Scan finished in {total_time:.1f}s "
    f"(open: {open_count}, closed: {closed_count})"
)