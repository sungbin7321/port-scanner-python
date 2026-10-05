import socket
import time

host = input("대상 IP 또는 도메인: ")
port_range = input("포트 범위 (예: 20-100): ")

if host == "localhost":
    host = "127.0.0.1"
elif host == "scanme":
    host = "scanme.nmap.org"


start_port, end_port = [int(x) for x in port_range.split("-")]

print(f"Scanning ports {port_range}")

start_time = time.time()

for port in range(start_port, end_port+1):
    # 객체 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    
    try:
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print(f"Port {port}: OPEN")
        else:
            print(f"Port {port}: CLOSED, {result}")
        
    
    except Exception as e:
        print(f"Error at port {port}: {e}")
    
    finally:
        sock.close()
        
end_time = time.time()
total_time = end_time - start_time
print(f"Scan Time: {total_time}")