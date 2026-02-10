# 📑 [2026-02-10] System Call & Mode Switch 실습

## 🎯 학습 목표
1. 유저 프로그램이 운영체제와 소통하는 방식인 **System Call**과 **Trap**의 메커니즘을 이해한다.
2. 실행 로그 분석을 통해 **User Mode**와 **Kernel Mode**의 전환 과정을 확인한다.
3. I/O 처리 방식(`endl` vs `\n`)에 따른 시스템 성능 차이의 원리를 파악한다.

## 💻 실습 코드
```cpp
#include <iostream>

int main() {
    std::cout << "Hello, OS!" << std::endl;
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
```

## 🔍 관찰 및 분석

### 1. 프로세스 실행 로그 분석
`strace`를 통해 확인한 프로그램의 일생은 다음과 같았습니다.

```plaintext
$ strace ./system_call_hands-on
--- Process 14164 created
--- Process 14164 loaded C:\Windows\System32\ntdll.dll at 00007ffbce690000
--- Process 14164 loaded C:\Windows\System32\kernel32.dll at 00007ffbcce50000
--- Process 14164 loaded C:\Windows\System32\KernelBase.dll at 00007ffbcbe40000
--- Process 14164 loaded C:\Windows\System32\msvcrt.dll at 00007ffbce400000
--- Process 14164 thread 5944 created
Hello, OS!
Hello, World!
--- Process 14164 thread 5944 exited with status 0x0
--- Process 14164 exited with status 0x0
```
- `Process 14164 created` : 커널이 메모리에 PCB 생성. PID, 상태, 사용가능한 메모리 범위 등의 정보를 정리.

- `loaded ntdll.dll` : 유저 모드에서 실행에 필요한 라이브러리를 메모리에 올리는 과정. 커널로 넘어가는 특수 명령어인 `syscall`과 다른 dll을 load할 수 있는 Ldr 기능을 포함.

- `loaded kernel32.dll` : 윈도우 애플리케이션이 사용하는 가장 대중적인 Win32 API의 진입점. 메모리 관리, 프로세스 제어, I/O등의 핵심 기능 제공

- `loaded KernelBase.dll` : `kernel32.dll` 등에 흩어져 있던 핵심 기능들을 하나로 모은 중간 관리 레이어. `kernel32.dll`에서 함수를 호출하면 실제 파라미터 검증이나 로직 처리를 함.

- `loaded msvcrt.dll` : C/C++ 표준함수(cout, printf 등)가 정의된 런타임 라이브러리 

- `thread 5944 created` : 실제로 코드를 한 줄씩 읽어나가는 '실행 단위'인 스레드 생성. stack을 할당 받고 PCB에 그 위치가 등록됨.

- `Hello, OS!`
    1. **System Call 요청** : thread(5944)가 `ntdll.dll`에 있는 `NtWriteFile`로 화면에 "Hello, OS!"를 출력하라고 요청

    2. **Trap 발생** : `NtWriteFile` 내부의 `syscall` 명령어를 실행 $\rightarrow$ 하드웨어적으로 Trap이 걸림

    3. **모드 전환** : Trap이 걸리는 순간 CPU는 하던 일을 멈추고 모드 비트를 1(유저)에서 0(커널)으로 바꿈

    4. **커널 작업** : 권한을 얻은 OS 커널이 하드웨어(모니터)에 접근해 글자를 출력

    5. **복귀** : 작업이 끝나면 다시 모드 비트를 1로 바꾸고 유저 프로그램으로 제어권을 돌려줌

- `Hello, World!` : 같은 작업 반복

- `thread 5944 exited with status 0x0` : thread에 할당한 자원 회수 (0x0은 성공적으로 끝났다는 의미)

- `Process 14164 exited with status 0x0` : Process에 할당한 자원 회수 및 PCB 제거



### 2. 이중 모드(Dual-mode) 연산의 핵심
프로그램이 화면에 글자를 찍는 과정에서 일어나는 핵심 메커니즘을 정리했습니다.
- **System Call**: 프로세스가 커널에 "화면 출력" 서비스를 요청하는 공식 창구입니다.
- **Trap**: 시스템 콜을 실행하기 위해 CPU에 신호를 보내 모드 비트(Mode Bit)를 **1(User)** 에서 **0(Kernel)** 으로 바꾸는 소프트웨어 인터럽트입니다.
- **Privileged Instruction**: 시스템의 전체적인 안전을 위해, 하드웨어를 직접 건드리거나 시스템 설정을 바꾸는 위험한 명령어들을 커널 모드에서만 실행 가능하도록 격리해 둔 것입니다.
    ```
    위와 같은 이유로 syscall 명령어는 커널 모드로 전환하는 명령어가 아님을 알 수 있습니다. ntdll.dll은 유저 모드에 속해있어 해당 권한이 없기 때문입니다.
    syscall 명령어는 커널 모드로 바꾸기 위해 소프트웨어 인터럽트(Trap)를 발생시키고, 그 즉시 CPU가 내부 회로에 의해 모드 비트를 커널로 변경합니다.

    cf) 후에 복귀 주소를 저장하고 커널로 점프한 뒤 인터럽트 핸들러가 작동하는데, 추후에 알아보면 될 것 같습니다.
    ```



### 3. I/O 효율성 비교
- `std::endl`을 통해 여러줄을 입력하면 trap이 여러번 발생해 모드 전환이 수시로 일어남을 확인했습니다. 따라서 버퍼를 활용하면 I/O 효율성을 높일 수 있습니다.

    | 구분 | `std::endl` | `\n` (Buffer 활용) |
    | :--- | :--- | :--- |
    | **동작** | 줄바꿈 + 즉시 버퍼 비우기(Flush) | 줄바꿈만 수행 (버퍼가 찰 때까지 대기) |
    | **Trap 발생** | 출력마다 즉시 발생 | 버퍼가 가득 찼을 때만 발생 |
    | **성능** | 상대적으로 느림 (오버헤드 발생) | 매우 효율적 (Trap 횟수 최소화) |

---

## 🧬 의공학 연구 및 AI 실험 연결 포인트
- **GGO 데이터 로딩 최적화**: 수만 장의 CT 슬라이스 데이터를 한 픽셀씩 요청하는 것은 비효율적입니다. OS의 **버퍼링(Buffering)** 원리를 이용해 데이터를 뭉치로 읽어오는 것이 데이터 로드 병목을 줄이는 핵심입니다.
- **DataLoader Batching**: PyTorch의 `batch_size` 전략은 결국 OS 입장에서 **System Call의 빈도를 낮추고 효율을 극대화**하는 공학적 접근임을 이해했습니다.



## 🔎 Findings
- Trap을 최소화하기 위해 Buffer를 활용해 적재 후 한번에 출력하는 방식을 사용하는 것이 효율적임을 확인했습니다. 이때 요청한 텍스트의 용량이 Buffer의 크기를 넘어설 경우 어떻게 되는지 궁금했는데, Buffer가 가득 차면 trap을 발생시켜 비우고 다시 적재하는 방식으로 동작함을 알게되었습니다.

- ntdll.dll이 가장 먼저 load되는 이유가, 적재되는 곳이 stack 구조여서 가장 마지막 명령어(syscall)를 수행하기 위해 가장 아래 적재되도록 하기 위함으로 추측했으나 사실과 달랐습니다. ntdll.dll이 가장 먼저 load 되는 이유는 다른 dll들을 불러올 수 있는 기능을 가지고 있기 때문이었습니다. 적재되는 공간은 stack 구조도 아니고 일반적으로는 stack과 heap 사이의 공간으로 ntdll.dll이 다양한 기능을 가지고 있기 때문에 수시로 상호작용함을 확인했습니다.

- NtWriteFile 함수는 세 단계로 구성됨을 확인했습니다.

    1. System Call Number: CPU의 특정 레지스터(EAX 또는 RAX)에 요청할 서비스의 번호를 넣습니다. 이 번호는 후에 인터럽트 핸들러가 확인합니다.

    2. Syscall : SYSCALL(또는 SYSENTER)라는 특수한 CPU 명령어를 실행합니다.

    3. 결과 확인 : 커널이 작업을 마치고 돌아오면, 성공했는지 여부를 확인하고 유저 프로그램으로 돌아갑니다.



## 🌙 다음 단계
- **2026-02-11 (목)**: **Chapter 3. 프로세스** 학습 예정. 오늘 생성된 PID 14164가 커널 내부에서 어떻게 PCB로 관리되고 문맥 교환(Context Switch)이 일어나는지 심화 학습할 계획입니다.