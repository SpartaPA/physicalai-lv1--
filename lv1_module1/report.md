# 모듈 ① 과제 보고서

## 문제 1 — 배달 로봇의 연산 분담과 실시간성 설계

### 계산에 사용한 조건

```text
v = 1.5m/s
a = 2m/s^2
v^2/2a = 0.56

encoder = 2kHz -> 0.5ms / 2 wheels x 4B counter x 2000Hz = 16kB/s
imu = 400Hz -> 2.5ms / ((xyz + vxvyvz) x 4B + 8B) = 32B/sample = 12.8kB/s
lidar = 15Hz -> 66.7ms / 360 points x (4B distance + 4B angle) = 2880B/scan = 43.2kB/s
cam = 60fps -> 16.7ms / 1280 x 720 x 3B = 2.7648MB/frame = 165.888MB/s
lte = 95~100Mbps -> 11.875~12.5MB/s, ping 1~5ms
```

1. **연산 분담 배치표** — 작업 / 위치 / 지연 예산 / 데이터량 / 근거

| 기능 | 분류 | 지연 예산 | 데이터량 | 사유 |
| --- | --- | --- | --- | --- |
| 모터 속도 제어  | 임베디드 | 0.5ms | 16kB/s | 2kHz의 짧은 주기이므로 통신 지연에 취약하기 때문 |
| 장애물 감지 | Edge AI | 66.7ms 이하 | 라이다 약 43.2kB/s | 라이다가 15Hz로 새 스캔을 생성하므로 한 스캔 주기인 66.7ms 이내에 현장에서 처리해야 하며, 클라우드 통신 지연이 추가되면 이동거리와 충돌 위험이 증가함 |
| 보행자 인식 | Edge AI | 0.1s | 카메라 원시 영상 약 165.888MB/s | 카메라 원시 영상은 LTE 업로드 대역폭보다 훨씬 크고 보행자 인식은 빠른 응답이 필요하므로 Edge AI가 적당해 보임 |
| 지도 기반 경로 계획 | 클라우드 | <10s | 수 kb | 지역 경로 계획처럼 매 순간 경로 계획하는 것이 아니며, 많은 자원이 필요한 단발적인 계산이므로 클라우드가 적절 |
| 배달 완료 사진 업로드 | 클라우드 | <10s | 약 2.7648MB/회 | 클라우드의 지연은 큰 영향이 없기 때문에 클라우드가 적절 |
| 운행 로그 집계 | 클라우드 | <10s | 수 kb | 배달 완료 사진 업로드와 같은 이유로 클라우드가 적절 |

2. **카메라 원시 영상 전송량**: `165.888` MB/s — LTE 대비 판단: 연속 전송 불가

원시 영상 데이터 크기: 1280 x 720 x 3B x 60fps = 165.888MB/s = 1327.104Mbps

원시 영상 데이터 크기인 1327.104Mbps가 LTE 업로드 대역폭 95~100Mbps보다 약 13배 이상 크므로, 원시 영상을 클라우드로 계속 전송하는 설계는 성립하지 않는다.

3. **인지·판단·제어 계층 매핑과 주기표**

| 기능 | 계층 | 갱신 주기 |
| --- | --- | --- |
| 모터 속도 제어  | 제어 | 0.5ms |
| 장애물 감지 | 인지 | 66.7ms 이하 |
| 보행자 인식 | 인지 | 0.1s |
| 지도 기반 경로 계획 | 판단 | <10s |
| 배달 완료 사진 업로드 | 판단 | <10s |
| 운행 로그 집계 | 판단 | <10s |

```text
인지
 ├─ 보행자 인식      : 0.1 s
 └─ 장애물 감지      : 66.7 ms 이하
          ↓
판단
 ├─ 지도 기반 경로 계획 : < 10 s
 ├─ 사진 업로드         : < 10 s
 └─ 운행 로그 집계      : < 10 s
          ↓
제어
 └─ 모터 속도 제어    : 0.5 ms
          ↓
        로봇 구동
```

4. **Hard / Firm / Soft 분류표** — Hard 항목의 마감 초과 결과

| 기능 | 분류 | 마감 초과 결과 |
| --- | --- | --- |
| 모터 속도 제어  | Hard | 제동 또는 속도 제어가 늦어져 정지거리가 증가하고 장애물과 충돌할 수 있음 |
| 장애물 감지 | Hard | 로봇이 장애물과 충돌할 수 있음 |
| 보행자 인식 | Firm |  |
| 지도 기반 경로 계획 | Firm |  |
| 배달 완료 사진 업로드 | Soft |  |
| 운행 로그 집계 | Soft |  |

5. **주기 · 지연 · 지터 구분** — 각 한 문장

- 주기: 엔코더가 2kHz로 동작할 때 0.5ms마다 반복해서 제어 명령을 계산하고 출력하는 간격
- 지연: 입력 발생부터 처리 결과나 제어 출력이 나올 때까지 걸린 시간
- 지터: 센서 처리가 일정한 간격이 아니라 1.0 ms, 1.2 ms, 0.9 ms처럼 들쭉날쭉 변하는 정도

## 문제 2 — 원격 접속(SSH)과 센서 장치 경로 고정

1. **고른 접속 대상**: `localhost / 가상머신` 중 `localhost` — 무비밀번호 접속 로그와 `who`·`echo $SSH_CONNECTION` 출력


```bash
ssh pa19@localhost
```

출력:

```text
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 6.8.0-138-generic x86_64)
Last login: Tue Aug 25 10:42:19 2026 from 127.0.0.1
```

SSH 서버 상태와 22번 포트 수신 상태를 확인했다.

```bash
systemctl status ssh
ss -tlnp | grep :22
```

출력:

```text
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled)
     Active: active (running) since Wed 2026-09-02 09:02:44 KST
   Main PID: 1115 (sshd)

LISTEN 0 128 0.0.0.0:22 0.0.0.0:*
LISTEN 0 128 [::]:22    [::]:*
```

2. **개인키·공개키 중 서버에 등록하는 것**: 서버에 등록하는 것은 공개키이다. 공개키만으로는 개인키를 알아내거나 사용자로 위장할 수 없고, 인증에 필요한 개인키는 클라이언트 컴퓨터에만 보관하기 때문에 안전하다. — 안전한 이유
```bash
ssh-keygen
```

출력:

```text
Your identification has been saved in /home/pa19/.ssh/id_rsa
Your public key has been saved in /home/pa19/.ssh/id_rsa.pub
The key fingerprint is:
SHA256:qfcEGe5rV5cw78Janu347fc/e3Dvn9J1firqIOYzfg8 pa19@pa19-Legion-Pro-5-16IAX10
```

생성한 공개키를 SSH 서버에 등록했다.

```bash
ssh-copy-id pa19@localhost
```

출력:

```text
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed

/usr/bin/ssh-copy-id: WARNING: All keys were skipped because they already exist on the remote system.
		(if you think this is a mistake, you may want to use -f option)
```

비밀번호 입력을 허용하지 않는 `BatchMode=yes`로 공개키 인증과 원격 세션을 확인했다.

```bash
ssh -o BatchMode=yes -o PreferredAuthentications=publickey pa19@localhost 'echo "PASSWORDLESS_SSH_OK"; who; echo "$SSH_CONNECTION"'
```

출력:

```text
PASSWORDLESS_SSH_OK
pa19     tty2         2026-09-04 08:54 (tty2)
pa19     pts/6        2026-09-04 12:24 (127.0.0.1)
127.0.0.1 41078 127.0.0.1 22
```

`BatchMode=yes`는 비밀번호 입력을 허용하지 않으므로 공개키 인증으로 접속됐음을 증명한다. `pts/6`은 SSH로 생성된 가상 터미널이며, `SSH_CONNECTION`은 localhost의 22번 포트로 연결됐음을 보여준다.

3. **원격 단일 명령 실행과 `scp` 전송 출력**

```bash
ssh pa19@localhost 'uname -a'
```

출력:

```text
Linux pa19-Legion-Pro-5-16IAX10 6.8.0-138-generic #138~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Aug 7 13:43:15 UTC 2026 x86_64 GNU/Linux
```

```bash
scp map.pgm pa19@localhost:~/
```

출력:

```text
map.pgm  100%  14KB  11.3MB/s  00:00
```



```bash
ls -l /dev/tty*
```

출력 중 대표 항목:

```text
crw-rw-rw- 1 root tty      5,  0 Sep 2 13:40 /dev/tty
crw--w---- 1 pa19 tty      4,  2 Sep 2 09:04 /dev/tty2
crw-rw---- 1 root dialout  4, 64 Sep 2 09:02 /dev/ttyS0
```

첫 문자 c는 문자 장치 파일이라는 뜻이다. /dev/tty\*의 대표 소유 그룹은 tty이며, 시리얼 포트인 /dev/ttyS\*는 dialout 그룹에 속한다. 권한은 소유자, 소유 그룹, 기타 사용자 순서로 읽기(r)와 쓰기(w) 가능 여부를 나타낸다.

```bash
mkdir -p ~/fake_sensors && cd ~/fake_sensors
truncate -s 16M lidar.img
truncate -s 24M imu.img
sudo losetup -f --show lidar.img
sudo losetup -f --show imu.img
```

출력:

```text
/dev/loop21
/dev/loop22
```

4. **두 장치를 구분한 속성**

가상 센서를 연결한 뒤 각 loop 장치의 속성을 조사했다.

```bash
udevadm info --attribute-walk /dev/loop21
udevadm info --attribute-walk /dev/loop22
```

출력:

```text
Udevadm info starts with the device specified by the devpath and then
walks up the chain of parent devices. It prints for every device
found, all possible attributes in the udev rules key format.
A rule to match, can be composed by the attributes of the device
and the attributes from one single parent device.

  looking at device '/devices/virtual/block/loop21':
    KERNEL=="loop21"
    SUBSYSTEM=="block"
    DRIVER==""
    ATTR{alignment_offset}=="0"
    ATTR{capability}=="0"
    ATTR{discard_alignment}=="0"
    ATTR{diskseq}=="47"
    ATTR{events}=="media_change"
    ATTR{events_async}==""
    ATTR{events_poll_msecs}=="-1"
    ATTR{ext_range}=="256"
    ATTR{hidden}=="0"
    ATTR{inflight}=="       0        0"
    ATTR{integrity/device_is_integrity_capable}=="0"
    ATTR{integrity/format}=="none"
    ATTR{integrity/protection_interval_bytes}=="0"
    ATTR{integrity/read_verify}=="0"
    ATTR{integrity/tag_size}=="0"
    ATTR{integrity/write_generate}=="0"
    ATTR{loop/autoclear}=="0"
    ATTR{loop/dio}=="0"
    ATTR{loop/offset}=="0"
    ATTR{loop/partscan}=="0"
    ATTR{loop/sizelimit}=="0"
    ATTR{mq/0/cpu_list}=="0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23"
    ATTR{mq/0/nr_reserved_tags}=="0"
    ATTR{mq/0/nr_tags}=="128"
    ATTR{partscan}=="0"
    ATTR{power/async}=="disabled"
    ATTR{power/control}=="auto"
    ATTR{power/runtime_active_kids}=="0"
    ATTR{power/runtime_active_time}=="0"
    ATTR{power/runtime_enabled}=="disabled"
    ATTR{power/runtime_status}=="unsupported"
    ATTR{power/runtime_suspended_time}=="0"
    ATTR{power/runtime_usage}=="0"
    ATTR{queue/add_random}=="0"
    ATTR{queue/chunk_sectors}=="0"
    ATTR{queue/dax}=="0"
    ATTR{queue/discard_granularity}=="4096"
    ATTR{queue/discard_max_bytes}=="4294966784"
    ATTR{queue/discard_max_hw_bytes}=="4294966784"
    ATTR{queue/discard_zeroes_data}=="0"
    ATTR{queue/dma_alignment}=="511"
    ATTR{queue/fua}=="0"
    ATTR{queue/hw_sector_size}=="512"
    ATTR{queue/io_poll}=="0"
    ATTR{queue/io_poll_delay}=="-1"
    ATTR{queue/iostats}=="1"
    ATTR{queue/logical_block_size}=="512"
    ATTR{queue/max_discard_segments}=="1"
    ATTR{queue/max_hw_sectors_kb}=="1280"
    ATTR{queue/max_integrity_segments}=="0"
    ATTR{queue/max_sectors_kb}=="1280"
    ATTR{queue/max_segment_size}=="65536"
    ATTR{queue/max_segments}=="128"
    ATTR{queue/minimum_io_size}=="512"
    ATTR{queue/nomerges}=="0"
    ATTR{queue/nr_requests}=="128"
    ATTR{queue/nr_zones}=="0"
    ATTR{queue/optimal_io_size}=="0"
    ATTR{queue/physical_block_size}=="512"
    ATTR{queue/read_ahead_kb}=="128"
    ATTR{queue/rotational}=="0"
    ATTR{queue/rq_affinity}=="1"
    ATTR{queue/scheduler}=="[none] mq-deadline "
    ATTR{queue/stable_writes}=="0"
    ATTR{queue/virt_boundary_mask}=="0"
    ATTR{queue/wbt_lat_usec}=="75000"
    ATTR{queue/write_cache}=="write back"
    ATTR{queue/write_same_max_bytes}=="0"
    ATTR{queue/write_zeroes_max_bytes}=="4294966784"
    ATTR{queue/zone_append_max_bytes}=="0"
    ATTR{queue/zone_write_granularity}=="0"
    ATTR{queue/zoned}=="none"
    ATTR{range}=="1"
    ATTR{removable}=="0"
    ATTR{ro}=="0"
    ATTR{size}=="32768"
    ATTR{stat}=="      79        0     1372        1        0        0        0        0        0        1        1        0        0        0        0        0        0"
    ATTR{trace/act_mask}=="disabled"
    ATTR{trace/enable}=="0"
    ATTR{trace/end_lba}=="disabled"
    ATTR{trace/pid}=="disabled"
    ATTR{trace/start_lba}=="disabled"


Udevadm info starts with the device specified by the devpath and then
walks up the chain of parent devices. It prints for every device
found, all possible attributes in the udev rules key format.
A rule to match, can be composed by the attributes of the device
and the attributes from one single parent device.

  looking at device '/devices/virtual/block/loop22':
    KERNEL=="loop22"
    SUBSYSTEM=="block"
    DRIVER==""
    ATTR{alignment_offset}=="0"
    ATTR{capability}=="0"
    ATTR{discard_alignment}=="0"
    ATTR{diskseq}=="49"
    ATTR{events}=="media_change"
    ATTR{events_async}==""
    ATTR{events_poll_msecs}=="-1"
    ATTR{ext_range}=="256"
    ATTR{hidden}=="0"
    ATTR{inflight}=="       0        0"
    ATTR{integrity/device_is_integrity_capable}=="0"
    ATTR{integrity/format}=="none"
    ATTR{integrity/protection_interval_bytes}=="0"
    ATTR{integrity/read_verify}=="0"
    ATTR{integrity/tag_size}=="0"
    ATTR{integrity/write_generate}=="0"
    ATTR{loop/autoclear}=="0"
    ATTR{loop/dio}=="0"
    ATTR{loop/offset}=="0"
    ATTR{loop/partscan}=="0"
    ATTR{loop/sizelimit}=="0"
    ATTR{mq/0/cpu_list}=="0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23"
    ATTR{mq/0/nr_reserved_tags}=="0"
    ATTR{mq/0/nr_tags}=="128"
    ATTR{partscan}=="0"
    ATTR{power/async}=="disabled"
    ATTR{power/control}=="auto"
    ATTR{power/runtime_active_kids}=="0"
    ATTR{power/runtime_active_time}=="0"
    ATTR{power/runtime_enabled}=="disabled"
    ATTR{power/runtime_status}=="unsupported"
    ATTR{power/runtime_suspended_time}=="0"
    ATTR{power/runtime_usage}=="0"
    ATTR{queue/add_random}=="0"
    ATTR{queue/chunk_sectors}=="0"
    ATTR{queue/dax}=="0"
    ATTR{queue/discard_granularity}=="4096"
    ATTR{queue/discard_max_bytes}=="4294966784"
    ATTR{queue/discard_max_hw_bytes}=="4294966784"
    ATTR{queue/discard_zeroes_data}=="0"
    ATTR{queue/dma_alignment}=="511"
    ATTR{queue/fua}=="0"
    ATTR{queue/hw_sector_size}=="512"
    ATTR{queue/io_poll}=="0"
    ATTR{queue/io_poll_delay}=="-1"
    ATTR{queue/iostats}=="1"
    ATTR{queue/logical_block_size}=="512"
    ATTR{queue/max_discard_segments}=="1"
    ATTR{queue/max_hw_sectors_kb}=="1280"
    ATTR{queue/max_integrity_segments}=="0"
    ATTR{queue/max_sectors_kb}=="1280"
    ATTR{queue/max_segment_size}=="65536"
    ATTR{queue/max_segments}=="128"
    ATTR{queue/minimum_io_size}=="512"
    ATTR{queue/nomerges}=="0"
    ATTR{queue/nr_requests}=="128"
    ATTR{queue/nr_zones}=="0"
    ATTR{queue/optimal_io_size}=="0"
    ATTR{queue/physical_block_size}=="512"
    ATTR{queue/read_ahead_kb}=="128"
    ATTR{queue/rotational}=="0"
    ATTR{queue/rq_affinity}=="1"
    ATTR{queue/scheduler}=="[none] mq-deadline "
    ATTR{queue/stable_writes}=="0"
    ATTR{queue/virt_boundary_mask}=="0"
    ATTR{queue/wbt_lat_usec}=="75000"
    ATTR{queue/write_cache}=="write back"
    ATTR{queue/write_same_max_bytes}=="0"
    ATTR{queue/write_zeroes_max_bytes}=="4294966784"
    ATTR{queue/zone_append_max_bytes}=="0"
    ATTR{queue/zone_write_granularity}=="0"
    ATTR{queue/zoned}=="none"
    ATTR{range}=="1"
    ATTR{removable}=="0"
    ATTR{ro}=="0"
    ATTR{size}=="49152"
    ATTR{stat}=="      68        0     1344        0        0        0        0        0        0        1        0        0        0        0        0        0        0"
    ATTR{trace/act_mask}=="disabled"
    ATTR{trace/enable}=="0"
    ATTR{trace/end_lba}=="disabled"
    ATTR{trace/pid}=="disabled"
    ATTR{trace/start_lba}=="disabled"

```

각 loop 장치의 `backing_file`을 직접 확인했다.

```bash
cat /sys/class/block/loop21/loop/backing_file
cat /sys/class/block/loop22/loop/backing_file
```

출력:

```text
/home/pa19/fake_sensors/lidar.img
/home/pa19/fake_sensors/imu.img

```

두 장치를 구분한 속성:

- 라이다: `ATTR{loop/backing_file}=="/home/pa19/fake_sensors/lidar.img"`
- IMU: `ATTR{loop/backing_file}=="/home/pa19/fake_sensors/imu.img"`


5. **작성한 udev 규칙 2개** + **규칙 키 설명표**

```udev
SUBSYSTEM=="block", KERNEL=="loop*", ATTR{loop/backing_file}=="/home/pa19/fake_sensors/lidar.img", SYMLINK+="robot_lidar", MODE="0660", GROUP="dialout"
SUBSYSTEM=="block", KERNEL=="loop*", ATTR{loop/backing_file}=="/home/pa19/fake_sensors/imu.img", SYMLINK+="robot_imu", MODE="0660", GROUP="dialout"
```

규칙 파일을 시스템에 복사하고 udev 규칙을 다시 불러온다. 아래 명령은 제출 저장소의 최상위 디렉터리에서 실행한다.

```bash
sudo cp lv1_module1/rules/99-robot-sensor.rules /etc/udev/rules.d/99-robot-sensor.rules
sudo udevadm control --reload-rules
```

출력:

```text
출력 없음
```

| 키 | 의미 |
| --- | --- |
| SUBSYSTEM=="block" | 블록 장치만 규칙과 비교한다. |
| KERNEL=="loop\*" | 커널 장치 이름이 loop로 시작하는 장치와 비교한다. |
| ATTR{loop/backing\_file}=="..." | loop 장치에 연결된 원본 이미지 경로와 비교한다. |
| SYMLINK+="..." | 기존 장치 이름을 유지하면서 /dev에 심볼릭 링크를 추가한다. |
| MODE="0660" | 장치 파일의 소유자와 그룹에 읽기·쓰기 권한을 부여하고 기타 사용자의 접근은 막는다. |
| GROUP="dialout" | 장치 파일의 소유 그룹을 지정한다. |
| == | 값을 지정하지 않고 매칭 조건을 비교한다. |
| = | 값을 새로 지정한다. |
| += | 기존 값에 새 값을 추가한다. |

6. **순서를 바꿔 재연결한 뒤 `ls -l /dev/robot_*` 결과**

```bash
sudo udevadm control --reload-rules
sudo losetup -d /dev/loop21
sudo losetup -d /dev/loop22
sudo losetup -f --show ~/fake_sensors/imu.img
sudo losetup -f --show ~/fake_sensors/lidar.img
losetup -l -O NAME,BACK-FILE | grep fake_sensors
ls -l /dev/robot_lidar /dev/robot_imu
readlink -f /dev/robot_lidar
readlink -f /dev/robot_imu
```

출력:

```text
/dev/loop21 /home/pa19/fake_sensors/imu.img
/dev/loop22 /home/pa19/fake_sensors/lidar.img
lrwxrwxrwx 1 root root 6 Sep 2 14:15 /dev/robot_imu -> loop21
lrwxrwxrwx 1 root root 6 Sep 2 14:15 /dev/robot_lidar -> loop22
/dev/loop22
/dev/loop21
```

연결 순서를 바꿔 loop 번호가 서로 달라졌지만, backing\_file을 기준으로 만든 /dev/robot\_lidar와 /dev/robot\_imu는 계속 올바른 이미지 파일을 가리켰다.

7. **실제 USB 센서용 규칙 초안과 구분 근거**

```udev
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="robot_lidar", MODE="0660", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea70", SYMLINK+="robot_imu", MODE="0660", GROUP="dialout"
```

두 장치는 idVendor가 10c4로 같으므로 제조사 ID만으로는 구분할 수 없다. 라이다의 idProduct=ea60과 IMU의 idProduct=ea70을 함께 비교하면 서로 다른 제품으로 구분할 수 있다.

## 문제 3 — 팀 저장소 협업 이력

`branch-a`와 `branch-b`에서 `README.md`의 첫 줄을 서로 다르게 수정했다. `branch-a`를 먼저 병합한 뒤 `branch-b`를 병합하면서 같은 줄에 충돌을 발생시켰고, 원래 제목을 최종 내용으로 선택해 해결했다.

충돌 표식에서 `<<<<<<< HEAD` 아래는 현재 브랜치의 내용, `=======`는 양쪽 내용의 경계, `>>>>>>> branch-b` 위는 병합하려는 브랜치의 내용이다.

이력 그래프 확인 명령은 다음과 같다.

```bash
git --no-pager log --oneline --graph --decorate --all
```

공유 브랜치의 병합 이력을 보존해야 할 때는 merge를 사용하고, 아직 공유하지 않은 개인 작업 브랜치를 최신 `main` 위에 정리할 때는 rebase를 사용한다. 이미 공유한 커밋은 rebase로 다시 쓰지 않는다.
