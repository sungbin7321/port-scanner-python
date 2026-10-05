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

### ThreadPoolExecutor 방식 구현과정
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


## 체크포인트 질문 답변

### 1. 이 스캐너가 포트 하나를 확인할 때 3-Way Handshake의 어느 단계까지 일어나는가?

`connect_ex()`는 실제로 TCP 연결을 시도하는 함수입니다. 그렇게 때문에 포트가 열려 있다면 **SYN → SYN-ACK → ACK**까지 진행되어 TCP 연결이 성립합니다.  
포트가 닫혀 있다면 보통 SYN 요청에 대해 RST 응답을 받아 연결에 실패합니다. **SYN → RST-ACK**
방화벽 등에 의해 패킷이 차단되면 응답 없이 timeout이 발생할 수도 있습니다. **SYN → (No response)**

### 2. `connect_ex()`와 `connect()`의 차이는 무엇이고 왜 스캐너에는 `connect_ex()`가 더 적합한가?

`connect()`는 연결에 실패하면 예외를 발생시키지만, `connect_ex()`는 연결 결과를 에러 코드로 반환합니다.
따라서 여러 포트를 반복해서 확인해야 하는 포트 스캐너에서는 매번 예외를 처리하는 것보다 반환값을 확인할 수 있는 `connect_ex()`가 더 편리합니다.

### 3. 스레드를 너무 많이 생성하면 어떤 문제가 생길 수 있는가?

스레드를 너무 많이 생성하면 CPU와 메모리 사용량이 증가하고, 동시에 너무 많은 소켓을 생성하여 **파일 디스크립터 제한**에 걸릴 수 있습니다.
여기서 파일 디스크립터 제한이란, (보통 리눅스/유닉스 시스템에서) 하나의 프로세스가 동시에 열 수 있는 파일과 소켓 등의 리소스 개수 최댓값입니다.
스레드를 너무 많이 생성하게 되면, Windows에서는 사용할 수 있는 버퍼/시스템 자원이 부족해서 소켓 작업을 계속할 수 없게 됩니다.

또한 대상 서버에 짧은 시간 동안 너무 많은 연결 요청을 보내면 방화벽이나 IDS/IPS에서 포트 스캔으로 판단하여 연결을 차단할 수도 있습니다.
여기서 IDS(Intrusion Detection System)란, 네트워크나 시스템의 트래픽을 모니터링하여 이상 징후나 해킹 시도를 탐지하고 관리자에게 경고하는 수동적 보안 시스템이고,
IPS(Intrusion Prevention System)란, 트래픽을 실시간으로 검사하여 위협을 탐지할 뿐만 아니라 악성 패킷을 즉시 차단하여 공격을 예방하는 능동적 보안 시스템입니다.

스레드를 너무 많이 쓰게 되면, 단시간에 많은 요청이 서버에 보내지게 되고, 서버의 IDS/IPS 시스템이 이를 감지하여 해당 IP packet DROP (timeout), 연결 속도 제한, 또는 일시적 IP 차단으로 이어질 수 있습니다.

따라서 적절한 수의 스레드를 제한하여 사용하는 것이 좋습니다.







