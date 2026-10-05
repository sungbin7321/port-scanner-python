# Python TCP Port Scanner

Python의 `socket` 모듈을 이용하여 특정 IP 또는 도메인의 TCP 포트가 열려 있는지 확인하는 간단한 포트 스캐너입니다.

## Level 1 구현 과정
1. 각 포트마다 TCP 소켓을 생성합니다.

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```

- `AF_INET`: IPv4 사용
- `SOCK_STREAM`: TCP 통신 사용

2. `connect_ex()`를 이용하여 해당 포트에 연결을 시도합니다.

```python
result = sock.connect_ex((host, port))
```

반환값이 `0`이면 연결에 성공한 것이므로 **OPEN**, 그 외의 값이면 **CLOSED**로 출력합니다.

3. 모든 포트 검사가 끝날 때마다 `sock.close()`를 호출하여 생성한 소켓을 닫습니다.

## Level 1 실행 방법

Python 3가 설치된 환경에서 다음과 같이 실행합니다.

```bash
python3 scanner.py
```

Windows에서는 다음 명령어를 사용할 수도 있습니다.

```bash
python scanner.py
```

실행 후 대상 주소와 포트 범위를 입력합니다.

```text
대상 IP 또는 도메인: localhost
포트 범위 (예: 20-100): 20-100
```

실행 결과 예시:

```text
Scanning ports 20-100
Port 22: OPEN
Port 23: CLOSED, 10061
...
```


## Level 2 구현 과정

### scan함수 구현과정
Level 1에서 만든 대부분의 코드를 가져와서 scan 함수로 만들었습니다.

아래 부분은 Level 1과 달라진 부분입니다.
socket.getservbyport를 이용하여 서비스를 추정하는 방식입니다.
```python
if result == 0:
    try:
        service = socket.getservbyport(port, "tcp")
    except OSError:
        service = "unknown port"
                
    print(f"Port {port} ({service}): OPEN")
```

### Argparse 구현과정
`argparse`를 사용하여 실행 시 `--host`와 `--ports` 옵션을 입력받도록 구현했습니다.

```python
parser = argparse.ArgumentParser()

parser.add_argument("--host", required=True)
parser.add_argument("--ports", required=True)

args = parser.parse_args()

host = args.host
port_range = args.ports
```

```bash
python3 scanner.py --host localhost --ports 20-100
```

입력받은 `host`가 `localhost`이면 `127.0.0.1`로, `scanme`이면 `scanme.nmap.org`로 변환합니다.

포트 범위는 `20-100`과 같은 문자열을 `-` 기준으로 나눈 뒤 정수로 변환하여 시작 포트와 마지막 포트로 저장합니다.

### Threading 방식 구현과정
최대 50개의 Thread를 생성하여 동시에 포트를 스캔하도록 구현했습니다.

Thread가 50개가 되면 join()을 사용하여 현재 50개의 Thread가 모두 종료될 때까지 기다린 후 다음 Thread들을 생성합니다.
(join 함수는 threads list 안에 있는 thread를 소멸시키지 않습니다.)

즉, 먼저 끝난 Thread가 있더라도 같은 그룹의 다른 Thread들이 모두 끝날 때까지 기다려야 합니다.

### ThreadPoolExecutor 방식
ThreadPoolExecutor를 사용하여 최대 50개의 Thread가 동시에 작업하도록 구현했습니다.

executor.submit()을 사용하여 각 포트의 scan() 작업을 Thread Pool에 전달합니다.

최대 50개의 Thread가 실행되며, 하나의 Thread 작업이 끝나면 대기 중인 다음 작업이 바로 그 자리를 사용합니다.

따라서 50개의 Thread가 모두 끝날 때까지 기다리는 threading 방식보다 Thread를 효율적으로 사용할 수 있습니다.

### 두 방식의 차이
Threading 방식에서는 한 Thread가 먼저 끝나더라도 나머지 Thread가 모두 끝날 때까지 다음 작업을 시작하지 않습니다.
ThreadPoolExecutor 방식에서는 동시에 최대 50개의 작업을 유지하면서, 작업이 끝난 자리에 새로운 작업을 바로 실행합니다.

따라서 ThreadPoolExecutor 방식이 Thread 관리가 더 간단하고 효율적입니다.

따라서 ThreadPoolExecutor 방식이 Thread 관리가 더 간단하고 효율적입니다.

## 실행 시간 측정

Level 1의 방식 (scanner.py) 과 Level 2 (scanner2.py) 의 두 방식 모두 time.time()을 사용하여 실행 시간을 측정했습니다.

```python
start_time = time.time()

end_time = time.time()

total_time = end_time - start_time
print(f"Scan Time: {total_time}")
```

### Level 1 (scanner.py)







