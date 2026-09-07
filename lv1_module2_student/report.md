# 모듈 ② 과제 보고서

## 문제 1 — C++ 빌드 체계

### 제동거리 프로그램 — 선행 구현

명령어

```bash
g++ -Wall -std=c++17 stop_distance.cpp
./a.out
```

출력

```text
Enter speed (m/s): 5
Enter friction coefficient: 0.4
Stopping distance: 3.186 m
```

1. **수동 2단계 빌드 명령** (터미널 입력)

명령어
```bash
g++ -Wall -std=c++17 -c motor.cpp -o motor.o
g++ -Wall -std=c++17 -c main.cpp -o main.o
g++ main.o motor.o -o motor_demo
./motor_demo
```

출력

```text
left motor speed: 1.5 m/s
right motor speed: 1.5 m/s
Motors stopped.
left motor speed: 0 m/s
right motor speed: 0 m/s
```

2. **`undefined reference` 에러 메시지** (출력) — 컴파일 에러와의 차이


```bash
g++ main.o -o motor_demo_broken
```

출력

```text
/usr/bin/ld: main.o: in function `main':
main.cpp:(.text+0x5a): undefined reference to `Motor::Motor(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >)'
main.cpp:(.text+0xf0): undefined reference to `Motor::set_speed(double)'
main.cpp:(.text+0x114): undefined reference to `Motor::print_status() const'
main.cpp:(.text+0x12c): undefined reference to `Motor::stop()'
collect2: error: ld returned 1 exit status
```

컴파일 에러는 각 소스 파일의 문법이나 타입 에러에 의해 .o파일을 만들지 못한 경우에 발생한다. undefined reference는 선언을 찾았기 때문에 컴파일은 통과했지만, 링크할 때 실제 메서드 구현이 들어 있는 motor.o를 찾지 못해서 발생한 링크 에러다.

3. **CMake 빌드 출력** (터미널 출력)

```bash
mkdir -p build
cd build
cmake ..
make
```

출력

```text
-- The CXX compiler identification is GNU 11.4.0
-- Configuring done
-- Generating done
-- Build files have been written to: .../lv1_module2/cpp_basics/build
[ 20%] Building CXX object CMakeFiles/stop_distance.dir/stop_distance.cpp.o
[ 40%] Linking CXX executable stop_distance
[ 40%] Built target stop_distance
[ 60%] Building CXX object CMakeFiles/motor_demo.dir/main.cpp.o
[ 80%] Building CXX object CMakeFiles/motor_demo.dir/motor.cpp.o
[100%] Linking CXX executable motor_demo
[100%] Built target motor_demo
```

4. **증분 빌드 시 재컴파일된 파일**: `motor.cpp` — 판단 근거


```text
Consolidate compiler generated dependencies of target stop_distance
[ 40%] Built target stop_distance
Consolidate compiler generated dependencies of target motor_demo
[ 60%] Building CXX object CMakeFiles/motor_demo.dir/motor.cpp.o
[ 80%] Linking CXX executable motor_demo
[100%] Built target motor_demo
```

증분 빌드 시 재컴파일된 파일은 motor.cpp
motor.cpp만 변경된 것으로 판단했기 때문이다. motor\_demo 실행 파일은 다시 링크됐지만 변경되지 않은 main.cpp와 stop\_distance.cpp는 재컴파일되지 않았다.

## 문제 2 — 현대 C++ 센서 계층

1. **다형성 루프 출력**

Sensor에 순수 가상 함수 read()와 가상 소멸자를 선언하고 Lidar와 Imu가 상속하게끔 했다.

```bash
cd cpp_basics/sensors
mkdir -p build
cd build
cmake ..
make
./sensor_demo
```

출력

```text
-- The CXX compiler identification is GNU 11.4.0
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++ - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Configuring done
-- Generating done
-- Build files have been written to: /home/pa19/physicalai-lv1-assignments/hw/physicalai-lv1-assignments/lv1_module2_student/cpp_basics/sensors/build
[ 14%] Building CXX object CMakeFiles/sensor_demo.dir/main.cpp.o
[ 28%] Building CXX object CMakeFiles/sensor_demo.dir/sensor.cpp.o
[ 42%] Linking CXX executable sensor_demo
[ 42%] Built target sensor_demo
[ 57%] Building CXX object CMakeFiles/no_virtual_destructor.dir/no_virtual_destructor.cpp.o
[ 71%] Linking CXX executable no_virtual_destructor
[ 71%] Built target no_virtual_destructor
[ 85%] Building CXX object CMakeFiles/leak_demo.dir/leak_demo.cpp.o
[100%] Linking CXX executable leak_demo
[100%] Built target leak_demo
[Stack lifetime]
Construct Sensor: stack_lidar
Construct Lidar
stack_lidar read: 2.4
Destroy Lidar
Destroy Sensor: stack_lidar
Stack scope ended

[Polymorphic heap sensors]
Construct Sensor: front_lidar
Construct Lidar
Construct Sensor: body_imu
Construct Imu
front_lidar read: 2.4
body_imu read: 0.15
Latest front_lidar: 2.4
Records within 0.35: 3
Clamped speed: 2
Clamped pixel: 255
Leaving main
Destroy Lidar
Destroy Sensor: front_lidar
Destroy Imu
Destroy Sensor: body_imu
```

함수 템플릿 clamp 결과는 double 속도 3.2 → 2.0, int 픽셀값 300 → 255

2. **스택 객체와 힙 객체의 소멸 시점** — 관찰 로그와 설명

```text
[Stack lifetime]
Construct Sensor: stack_lidar
Construct Lidar
stack_lidar read: 2.4
Destroy Lidar
Destroy Sensor: stack_lidar
Stack scope ended
```

스택 객체는 선언된 블록을 벗어나는 즉시 자동으로 소멸한다. 힙 객체는
`std::unique_ptr` 가 소유하므로 `sensors` 컨테이너가 소멸할 때 함께 해제된다.
두 경우 모두 파생 클래스 소멸자(`Destroy Lidar/Imu`)가 먼저 호출되고 기반
클래스 소멸자(`Destroy Sensor`)가 이어서 호출됐다.


3. **가상 소멸자를 뺐을 때의 차이**
```bash
g++ -Wall -Wextra -std=c++17 -fsanitize=address \
  no_virtual_destructor.cpp -o no_virtual_asan
./no_virtual_asan
```

출력

```text
ERROR: AddressSanitizer: new-delete-type-mismatch
object passed to delete has wrong type:
size of the allocated type:   1032 bytes;
size of the deallocated type: 8 bytes.
SUMMARY: AddressSanitizer: new-delete-type-mismatch
```

가상 소멸자가 없으면 Sensor 포인터를 통해 삭제할 때 파생 클래스 소멸자가 호출된다는 보장이 없으며 동작이 정의되지 않는다. 실제 실행에서도 할당 타입과 해제 타입이 다르다는 오류가 검출됐다. 가상 소멸자를 사용한 최종 구현에서는 파생 클래스 소멸자 다음 기본 클래스 소멸자가 정상적으로 호출됐다.

4. **`count_if` 결과**: 0.35 이내 기록 `3`개

실제 출력은 1번의 `Records within 0.35: 3`에서 확인한다.

5. **누수 검출 결과** → **수정 후 결과** (검출 도구 출력 비교)

```bash
valgrind --leak-check=full ./leak_demo leak
```

출력

```text
HEAP SUMMARY:
    in use at exit: 24,576 bytes in 3 blocks
24,576 bytes in 3 blocks are definitely lost
LEAK SUMMARY:
   definitely lost: 24,576 bytes in 3 blocks
ERROR SUMMARY: 1 errors from 1 contexts
```

std::make\_unique<double[]>로 변경한 모드를 검사했다.

```bash
valgrind --leak-check=full ./leak_demo fixed
```

출력

```text
HEAP SUMMARY:
    in use at exit: 0 bytes in 0 blocks
All heap blocks were freed -- no leaks are possible
ERROR SUMMARY: 0 errors from 0 contexts
```

new로 직접 할당한 메모리는 해제하지 않아 24576 바이트가 누수됐다. make\_unique로 바꾼 뒤에는 누수가 사라졌다.

## 문제 3 — rclpy 노드

1. **`/turtle1/pose` 필드 구성**

```text
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

2. **`ros2 topic hz /turtle_distance` 출력**

```bash
ros2 topic hz /turtle_distance --window 20
```

```text
average rate: 10.000
  min: 0.100s max: 0.100s std dev: 0.00011s window: 20
```

3. **구독자 경고 로그** (터미널 출력)

```bash
ros2 run turtle_py distance_subscriber
```

출력:

```text
[WARN] [1788504783.689678938] [distance_subscriber]: distance 7.841 exceeds 2.500
[WARN] [1788504783.781691412] [distance_subscriber]: distance 7.841 exceeds 2.500
[WARN] [1788504783.879240471] [distance_subscriber]: distance 7.841 exceeds 2.500
[WARN] [1788504783.981310418] [distance_subscriber]: distance 7.841 exceeds 2.500
[WARN] [1788504784.079441705] [distance_subscriber]: distance 7.841 exceeds 2.500
[WARN] [1788504784.181823457] [distance_subscriber]: distance 7.841 exceeds 2.500
[WARN] [1788504784.279069885] [distance_subscriber]: distance 7.841 exceeds 2.500
...

```

4. **구독자 2개 동시 수신 확인** (양쪽 로그)

```bash
ros2 run turtle_py distance_subscriber
ros2 run turtle_py distance_subscriber --ros-args -r __node:=distance_subscriber_2
```

출력:

```text
[WARN] [1788504816.917346896] [distance_subscriber]: distance 7.841 exceeds 2.500
[WARN] [1788504817.017243911] [distance_subscriber]: distance 7.841 exceeds 2.500
[WARN] [1788504817.120171169] [distance_subscriber]: distance 7.841 exceeds 2.500
[WARN] [1788504817.217218701] [distance_subscriber]: distance 7.841 exceeds 2.500
...


[WARN] [1788504816.917557567] [distance_subscriber_2]: distance 7.841 exceeds 2.500
[WARN] [1788504817.017273515] [distance_subscriber_2]: distance 7.841 exceeds 2.500
[WARN] [1788504817.120171693] [distance_subscriber_2]: distance 7.841 exceeds 2.500
[WARN] [1788504817.217380798] [distance_subscriber_2]: distance 7.841 exceeds 2.500
...
```

5. **정사각형 주행 캡처** (turtlesim 화면)

```bash
ros2 run turtle_py square_driver
ros2 param set /distance_publisher publish_rate 5.0
ros2 param set /distance_subscriber warn_distance 0.8
```

Ctrl+C 종료 시 traceback 없이 프로세스가 종료하며 finally에서 정지 Twist, destroy_node(), shutdown() 실행
 정사각형 궤적 캡처는 `screenshots/square_driving.png`

6. **Ctrl+C 정상 종료 화면** (출력)

```text
^C
```

종료 시 Python traceback이나 오류 메시지가 출력되지 않았고 쉘 프롬프트로
정상 복귀했다.

## 문제 4 — rclcpp 노드

1. **`colcon build` 성공 출력**

```text
Starting >>> turtle_cpp
Finished <<< turtle_cpp [30.0s]
Summary: 1 package finished [30.3s]
```

CMakeLists 일부

```cmake
find_package(rclcpp REQUIRED)
find_package(turtlesim REQUIRED)
find_package(std_msgs REQUIRED)
add_executable(distance_publisher src/distance_publisher.cpp)
ament_target_dependencies(distance_publisher rclcpp turtlesim std_msgs)
add_executable(distance_subscriber src/distance_subscriber.cpp)
ament_target_dependencies(distance_subscriber rclcpp std_msgs)
install(TARGETS distance_publisher distance_subscriber DESTINATION lib/${PROJECT_NAME})
```

2. **rclpy 발행에서 rclcpp 구독으로 이어진 로그**

```bash
ros2 run turtle_py distance_publisher
ros2 run turtle_cpp distance_subscriber
```

```text
[INFO] [cpp_distance_subscriber]: distance: 3.050
```

3. **rclpy와 rclcpp 대응 관계표** — 노드 생성 / 타이머 / 콜백 / 종료

| 기능 | rclpy | rclcpp |
|---|---|---|
| 노드 생성 | Node.__init__() | rclcpp::Node 생성자 |
| 타이머 | create_timer() | create_wall_timer() |
| 콜백 | Python callable | lambda/function callback |
| 종료 | destroy 후 rclpy.shutdown() | rclcpp::shutdown() |

## 문제 5 — Service와 Action

문제 5~9의 모든 새 터미널에서는 먼저 다음 명령으로 워크스페이스와 ROS 2 환경을 설정한다.

```bash
cd /home/pa19/physicalai-lv1-assignments/hw/physicalai-lv1-assignments/lv1_module2_student/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
```

1. **호출한 내장 서비스와 타입** — 서비스 / 타입 / 요청 값 / 결과

서비스 목록과 각 서비스의 타입을 먼저 확인한다.

```bash
ros2 service list
ros2 service type /turtle1/teleport_absolute
ros2 service type /turtle1/set_pen
ros2 service type /spawn
ros2 service type /clear
```

출력:

```text
'ros2 service list'
/clear
/kill
/reset
/spawn
/turtle1/set_pen
/turtle1/teleport_absolute
/turtle1/teleport_relative
/turtlesim/describe_parameters
/turtlesim/get_parameter_types
/turtlesim/get_parameters
/turtlesim/list_parameters
/turtlesim/set_parameters
/turtlesim/set_parameters_atomically


'ros2 service type /turtle1/teleport_absolute'
turtlesim/srv/TeleportAbsolute


'ros2 service type /turtle1/set_pen'
turtlesim/srv/SetPen


'ros2 service type /spawn'
turtlesim/srv/Spawn


'ros2 service type /clear'
std_srvs/srv/Empty

```

| 서비스 | 타입 | 요청 요약 | 결과 |
|---|---|---|---|
| /turtle1/teleport_absolute | turtlesim/srv/TeleportAbsolute | x=2, y=2, theta=0 | 성공 |
| /turtle1/set_pen | turtlesim/srv/SetPen | RGB=(255,80,30), width=3 | 성공 |
| /spawn | turtlesim/srv/Spawn | (8,8), turtle2 | name='turtle2' |
| /clear | std_srvs/srv/Empty | 빈 요청 | 성공 |


2. **Service 요청·응답 로그**

내장 서비스 호출

```bash
ros2 run turtle_py service_client
```

출력:

```text
[INFO] [1788505058.555789751] [turtlesim]: Starting turtlesim with node name /turtlesim
[INFO] [1788505058.562336276] [turtlesim]: Spawning turtle [turtle1] at x=[5.544445], y=[5.544445], theta=[0.000000]
[INFO] [1788505129.162176184] [turtlesim]: Spawning turtle [turtle2] at x=[8.000000], y=[8.000000], theta=[0.000000]
[INFO] [1788505129.176695458] [turtlesim]: Clearing turtlesim.

```

자체 서비스 검증

```bash
# square_driver를 실행한 상태에서 다른 터미널에서 호출
ros2 service call /set_driving std_srvs/srv/SetBool "{data: false}"
ros2 service call /save_home std_srvs/srv/Trigger "{}"
ros2 service call /set_driving std_srvs/srv/SetBool "{data: true}"
```

출력:

```text
'ros2 service call /set_driving std_srvs/srv/SetBool "{data: false}"'
requester: making request: std_srvs.srv.SetBool_Request(data=False)

response:
std_srvs.srv.SetBool_Response(success=True, message='driving stopped')


'ros2 service call /save_home std_srvs/srv/Trigger "{}"'
requester: making request: std_srvs.srv.Trigger_Request()

response:
std_srvs.srv.Trigger_Response(success=True, message='home saved at (1.87828528881073, 2.077993154525757)')


'ros2 service call /set_driving std_srvs/srv/SetBool "{data: true}"'
requester: making request: std_srvs.srv.SetBool_Request(data=True)

response:
std_srvs.srv.SetBool_Response(success=True, message='driving enabled')

```

3. **데드락이 생기는 이유** — executor 관점

콜백이 실행스레드 점유하면 응답 콜백을 수행하지 못해서 데드락에 빠진다.
요청은 call_async로 보내고 콜백 반환하거나 MultiThreadedExecutor써야함

4. **`rotate_absolute` 피드백 수신 로그** — remaining이 줄어드는 흐름

```bash
ros2 run turtle_py rotate_action_client --ros-args -p target_angle:=3.0
```

출력:

```text
[INFO] [1788505282.064532574] [rotate_action_client]: remaining: 3.075
[INFO] [1788505282.075054742] [rotate_action_client]: remaining: 3.059
[INFO] [1788505282.092359254] [rotate_action_client]: remaining: 3.043
[INFO] [1788505282.105996528] [rotate_action_client]: remaining: 3.027
[INFO] [1788505282.123526096] [rotate_action_client]: remaining: 3.011
[INFO] [1788505282.141199923] [rotate_action_client]: remaining: 2.995
[INFO] [1788505282.153891058] [rotate_action_client]: remaining: 2.979
[INFO] [1788505282.171414492] [rotate_action_client]: remaining: 2.963
[INFO] [1788505282.185031762] [rotate_action_client]: remaining: 2.947
[INFO] [1788505282.202329531] [rotate_action_client]: remaining: 2.931
[INFO] [1788505282.217399342] [rotate_action_client]: remaining: 2.915
[INFO] [1788505282.237506967] [rotate_action_client]: remaining: 2.899
[INFO] [1788505282.249997657] [rotate_action_client]: remaining: 2.883
[INFO] [1788505282.265630476] [rotate_action_client]: remaining: 2.867
[INFO] [1788505282.281258435] [rotate_action_client]: remaining: 2.851
[INFO] [1788505282.298005149] [rotate_action_client]: remaining: 2.835
[INFO] [1788505282.313903584] [rotate_action_client]: remaining: 2.819
[INFO] [1788505282.330114225] [rotate_action_client]: remaining: 2.803
[INFO] [1788505282.345787678] [rotate_action_client]: remaining: 2.787
[INFO] [1788505282.361708248] [rotate_action_client]: remaining: 2.771
[INFO] [1788505282.378307182] [rotate_action_client]: remaining: 2.755
[INFO] [1788505282.394643830] [rotate_action_client]: remaining: 2.739
[INFO] [1788505282.410487849] [rotate_action_client]: remaining: 2.723
[INFO] [1788505282.426417059] [rotate_action_client]: remaining: 2.707
[INFO] [1788505282.441388611] [rotate_action_client]: remaining: 2.691
[INFO] [1788505282.457446757] [rotate_action_client]: remaining: 2.675
[INFO] [1788505282.475640213] [rotate_action_client]: remaining: 2.659
[INFO] [1788505282.492909903] [rotate_action_client]: remaining: 2.643
[INFO] [1788505282.505887019] [rotate_action_client]: remaining: 2.627
[INFO] [1788505282.523731608] [rotate_action_client]: remaining: 2.611
[INFO] [1788505282.540743165] [rotate_action_client]: remaining: 2.595
[INFO] [1788505282.553789396] [rotate_action_client]: remaining: 2.579
[INFO] [1788505282.572525450] [rotate_action_client]: remaining: 2.563
[INFO] [1788505282.589128246] [rotate_action_client]: remaining: 2.547
[INFO] [1788505282.601744032] [rotate_action_client]: remaining: 2.531
[INFO] [1788505282.617214267] [rotate_action_client]: remaining: 2.515
[INFO] [1788505282.633196070] [rotate_action_client]: remaining: 2.499
[INFO] [1788505282.649804426] [rotate_action_client]: remaining: 2.483
[INFO] [1788505282.665894148] [rotate_action_client]: remaining: 2.467
[INFO] [1788505282.681911619] [rotate_action_client]: remaining: 2.451
[INFO] [1788505282.699384731] [rotate_action_client]: remaining: 2.435
[INFO] [1788505282.714302919] [rotate_action_client]: remaining: 2.419
[INFO] [1788505282.729998180] [rotate_action_client]: remaining: 2.403
[INFO] [1788505282.745991556] [rotate_action_client]: remaining: 2.387
[INFO] [1788505282.761809056] [rotate_action_client]: remaining: 2.371
[INFO] [1788505282.778900324] [rotate_action_client]: remaining: 2.355
[INFO] [1788505282.793694806] [rotate_action_client]: remaining: 2.339
[INFO] [1788505282.810146017] [rotate_action_client]: remaining: 2.323
[INFO] [1788505282.826964375] [rotate_action_client]: remaining: 2.307
[INFO] [1788505282.841076410] [rotate_action_client]: remaining: 2.291
[INFO] [1788505282.857828145] [rotate_action_client]: remaining: 2.275
[INFO] [1788505282.874532603] [rotate_action_client]: remaining: 2.259
[INFO] [1788505282.893293168] [rotate_action_client]: remaining: 2.243
[INFO] [1788505282.905334292] [rotate_action_client]: remaining: 2.227
[INFO] [1788505282.923165794] [rotate_action_client]: remaining: 2.211
[INFO] [1788505282.941944388] [rotate_action_client]: remaining: 2.195
[INFO] [1788505282.953624350] [rotate_action_client]: remaining: 2.179
[INFO] [1788505282.972433210] [rotate_action_client]: remaining: 2.163
[INFO] [1788505282.989162127] [rotate_action_client]: remaining: 2.147
[INFO] [1788505283.001357289] [rotate_action_client]: remaining: 2.131
[INFO] [1788505283.018052158] [rotate_action_client]: remaining: 2.115
[INFO] [1788505283.033803959] [rotate_action_client]: remaining: 2.099
[INFO] [1788505283.049647714] [rotate_action_client]: remaining: 2.083
[INFO] [1788505283.065266023] [rotate_action_client]: remaining: 2.067
[INFO] [1788505283.081934996] [rotate_action_client]: remaining: 2.051
[INFO] [1788505283.097756099] [rotate_action_client]: remaining: 2.035
[INFO] [1788505283.113684881] [rotate_action_client]: remaining: 2.019
[INFO] [1788505283.129552767] [rotate_action_client]: remaining: 2.003
[INFO] [1788505283.146587896] [rotate_action_client]: remaining: 1.987
[INFO] [1788505283.161882904] [rotate_action_client]: remaining: 1.971
[INFO] [1788505283.178113621] [rotate_action_client]: remaining: 1.955
[INFO] [1788505283.193670053] [rotate_action_client]: remaining: 1.939
[INFO] [1788505283.209162670] [rotate_action_client]: remaining: 1.923
[INFO] [1788505283.226022909] [rotate_action_client]: remaining: 1.907
[INFO] [1788505283.241823757] [rotate_action_client]: remaining: 1.891
[INFO] [1788505283.261319943] [rotate_action_client]: remaining: 1.875
[INFO] [1788505283.274966991] [rotate_action_client]: remaining: 1.859
[INFO] [1788505283.292572906] [rotate_action_client]: remaining: 1.843
[INFO] [1788505283.305317099] [rotate_action_client]: remaining: 1.827
[INFO] [1788505283.323348361] [rotate_action_client]: remaining: 1.811
[INFO] [1788505283.341643798] [rotate_action_client]: remaining: 1.795
[INFO] [1788505283.353179468] [rotate_action_client]: remaining: 1.779
[INFO] [1788505283.372393767] [rotate_action_client]: remaining: 1.763
[INFO] [1788505283.386209681] [rotate_action_client]: remaining: 1.747
[INFO] [1788505283.402218904] [rotate_action_client]: remaining: 1.731
[INFO] [1788505283.417915575] [rotate_action_client]: remaining: 1.715
[INFO] [1788505283.433809198] [rotate_action_client]: remaining: 1.699
[INFO] [1788505283.449566888] [rotate_action_client]: remaining: 1.683
[INFO] [1788505283.465260255] [rotate_action_client]: remaining: 1.667
[INFO] [1788505283.481218742] [rotate_action_client]: remaining: 1.651
[INFO] [1788505283.497934023] [rotate_action_client]: remaining: 1.635
[INFO] [1788505283.513582728] [rotate_action_client]: remaining: 1.619
[INFO] [1788505283.529041855] [rotate_action_client]: remaining: 1.603
[INFO] [1788505283.545902365] [rotate_action_client]: remaining: 1.587
[INFO] [1788505283.561767214] [rotate_action_client]: remaining: 1.571
[INFO] [1788505283.577908006] [rotate_action_client]: remaining: 1.555
[INFO] [1788505283.593658649] [rotate_action_client]: remaining: 1.539
[INFO] [1788505283.609237924] [rotate_action_client]: remaining: 1.523
[INFO] [1788505283.626113087] [rotate_action_client]: remaining: 1.507
[INFO] [1788505283.642047034] [rotate_action_client]: remaining: 1.491
[INFO] [1788505283.657773313] [rotate_action_client]: remaining: 1.475
[INFO] [1788505283.675201651] [rotate_action_client]: remaining: 1.459
[INFO] [1788505283.693643250] [rotate_action_client]: remaining: 1.443
[INFO] [1788505283.706142600] [rotate_action_client]: remaining: 1.427
[INFO] [1788505283.722920879] [rotate_action_client]: remaining: 1.411
[INFO] [1788505283.741018311] [rotate_action_client]: remaining: 1.395
[INFO] [1788505283.753730929] [rotate_action_client]: remaining: 1.379
[INFO] [1788505283.771736202] [rotate_action_client]: remaining: 1.363
[INFO] [1788505283.789024465] [rotate_action_client]: remaining: 1.347
[INFO] [1788505283.801759294] [rotate_action_client]: remaining: 1.331
[INFO] [1788505283.817458950] [rotate_action_client]: remaining: 1.315
[INFO] [1788505283.837430657] [rotate_action_client]: remaining: 1.299
[INFO] [1788505283.849802323] [rotate_action_client]: remaining: 1.283
[INFO] [1788505283.865889642] [rotate_action_client]: remaining: 1.267
[INFO] [1788505283.881346271] [rotate_action_client]: remaining: 1.251
[INFO] [1788505283.898038991] [rotate_action_client]: remaining: 1.235
[INFO] [1788505283.915723458] [rotate_action_client]: remaining: 1.219
[INFO] [1788505283.929683559] [rotate_action_client]: remaining: 1.203
[INFO] [1788505283.945573470] [rotate_action_client]: remaining: 1.187
[INFO] [1788505283.961948310] [rotate_action_client]: remaining: 1.171
[INFO] [1788505283.977742826] [rotate_action_client]: remaining: 1.155
[INFO] [1788505283.993833301] [rotate_action_client]: remaining: 1.139
[INFO] [1788505284.009307721] [rotate_action_client]: remaining: 1.123
[INFO] [1788505284.026652340] [rotate_action_client]: remaining: 1.107
[INFO] [1788505284.041380328] [rotate_action_client]: remaining: 1.091
[INFO] [1788505284.057922875] [rotate_action_client]: remaining: 1.075
[INFO] [1788505284.075061814] [rotate_action_client]: remaining: 1.059
[INFO] [1788505284.092605567] [rotate_action_client]: remaining: 1.043
[INFO] [1788505284.105179104] [rotate_action_client]: remaining: 1.027
[INFO] [1788505284.123030875] [rotate_action_client]: remaining: 1.011
[INFO] [1788505284.140875804] [rotate_action_client]: remaining: 0.995
[INFO] [1788505284.153526437] [rotate_action_client]: remaining: 0.979
[INFO] [1788505284.171869756] [rotate_action_client]: remaining: 0.963
[INFO] [1788505284.190036085] [rotate_action_client]: remaining: 0.947
[INFO] [1788505284.201137857] [rotate_action_client]: remaining: 0.931
[INFO] [1788505284.217367631] [rotate_action_client]: remaining: 0.915
[INFO] [1788505284.237943100] [rotate_action_client]: remaining: 0.899
[INFO] [1788505284.249580600] [rotate_action_client]: remaining: 0.883
[INFO] [1788505284.265900994] [rotate_action_client]: remaining: 0.867
[INFO] [1788505284.281585261] [rotate_action_client]: remaining: 0.851
[INFO] [1788505284.297544608] [rotate_action_client]: remaining: 0.835
[INFO] [1788505284.313617151] [rotate_action_client]: remaining: 0.819
[INFO] [1788505284.329883293] [rotate_action_client]: remaining: 0.803
[INFO] [1788505284.346046388] [rotate_action_client]: remaining: 0.787
[INFO] [1788505284.361535450] [rotate_action_client]: remaining: 0.771
[INFO] [1788505284.377327490] [rotate_action_client]: remaining: 0.755
[INFO] [1788505284.394065341] [rotate_action_client]: remaining: 0.739
[INFO] [1788505284.409665884] [rotate_action_client]: remaining: 0.723
[INFO] [1788505284.426275205] [rotate_action_client]: remaining: 0.707
[INFO] [1788505284.442085154] [rotate_action_client]: remaining: 0.691
[INFO] [1788505284.457849642] [rotate_action_client]: remaining: 0.675
[INFO] [1788505284.474910187] [rotate_action_client]: remaining: 0.659
[INFO] [1788505284.492877535] [rotate_action_client]: remaining: 0.643
[INFO] [1788505284.505369645] [rotate_action_client]: remaining: 0.627
[INFO] [1788505284.523775244] [rotate_action_client]: remaining: 0.611
[INFO] [1788505284.537876450] [rotate_action_client]: remaining: 0.595
[INFO] [1788505284.553969064] [rotate_action_client]: remaining: 0.579
[INFO] [1788505284.571659873] [rotate_action_client]: remaining: 0.563
[INFO] [1788505284.585223145] [rotate_action_client]: remaining: 0.547
[INFO] [1788505284.602053161] [rotate_action_client]: remaining: 0.531
[INFO] [1788505284.617797218] [rotate_action_client]: remaining: 0.515
[INFO] [1788505284.633661419] [rotate_action_client]: remaining: 0.499
[INFO] [1788505284.649562295] [rotate_action_client]: remaining: 0.483
[INFO] [1788505284.668542525] [rotate_action_client]: remaining: 0.467
[INFO] [1788505284.682062096] [rotate_action_client]: remaining: 0.451
[INFO] [1788505284.697957517] [rotate_action_client]: remaining: 0.435
[INFO] [1788505284.713658740] [rotate_action_client]: remaining: 0.419
[INFO] [1788505284.729567829] [rotate_action_client]: remaining: 0.403
[INFO] [1788505284.745370333] [rotate_action_client]: remaining: 0.387
[INFO] [1788505284.763634911] [rotate_action_client]: remaining: 0.371
[INFO] [1788505284.777281619] [rotate_action_client]: remaining: 0.355
[INFO] [1788505284.794183080] [rotate_action_client]: remaining: 0.339
[INFO] [1788505284.811920104] [rotate_action_client]: remaining: 0.323
[INFO] [1788505284.827137563] [rotate_action_client]: remaining: 0.307
[INFO] [1788505284.842027833] [rotate_action_client]: remaining: 0.291
[INFO] [1788505284.857901319] [rotate_action_client]: remaining: 0.275
[INFO] [1788505284.873603794] [rotate_action_client]: remaining: 0.259
[INFO] [1788505284.892968374] [rotate_action_client]: remaining: 0.243
[INFO] [1788505284.906122183] [rotate_action_client]: remaining: 0.227
[INFO] [1788505284.925367910] [rotate_action_client]: remaining: 0.211
[INFO] [1788505284.937857008] [rotate_action_client]: remaining: 0.195
[INFO] [1788505284.953935635] [rotate_action_client]: remaining: 0.179
[INFO] [1788505284.974083984] [rotate_action_client]: remaining: 0.163
[INFO] [1788505284.985425693] [rotate_action_client]: remaining: 0.147
[INFO] [1788505285.002586259] [rotate_action_client]: remaining: 0.131
[INFO] [1788505285.018199375] [rotate_action_client]: remaining: 0.115
[INFO] [1788505285.033661346] [rotate_action_client]: remaining: 0.099
[INFO] [1788505285.049266190] [rotate_action_client]: remaining: 0.083
[INFO] [1788505285.068031943] [rotate_action_client]: remaining: 0.067
[INFO] [1788505285.081788338] [rotate_action_client]: remaining: 0.051
[INFO] [1788505285.097535399] [rotate_action_client]: remaining: 0.035
[INFO] [1788505285.113192103] [rotate_action_client]: remaining: 0.019
[INFO] [1788505285.113767708] [rotate_action_client]: action status: 4

```

5. **취소 요청 처리 로그** — 취소 시점 각도

```bash
ros2 run turtle_py rotate_action_client --ros-args -p target_angle:=3.0 -p cancel_after:=1.0
```

출력:

```text
[INFO] [1788505385.200481159] [rotate_action_client]: remaining: 3.000
[INFO] [1788505385.206869239] [rotate_action_client]: remaining: 2.984
[INFO] [1788505385.224886053] [rotate_action_client]: remaining: 2.968
[INFO] [1788505385.240042131] [rotate_action_client]: remaining: 2.952
[INFO] [1788505385.255020270] [rotate_action_client]: remaining: 2.936
[INFO] [1788505385.274053908] [rotate_action_client]: remaining: 2.920
[INFO] [1788505385.290787282] [rotate_action_client]: remaining: 2.904
[INFO] [1788505385.303467020] [rotate_action_client]: remaining: 2.888
[INFO] [1788505385.319339818] [rotate_action_client]: remaining: 2.872
[INFO] [1788505385.339831272] [rotate_action_client]: remaining: 2.856
[INFO] [1788505385.350631118] [rotate_action_client]: remaining: 2.840
[INFO] [1788505385.369963577] [rotate_action_client]: remaining: 2.824
[INFO] [1788505385.382647357] [rotate_action_client]: remaining: 2.808
[INFO] [1788505385.398761401] [rotate_action_client]: remaining: 2.792
[INFO] [1788505385.415199493] [rotate_action_client]: remaining: 2.776
[INFO] [1788505385.431186547] [rotate_action_client]: remaining: 2.760
[INFO] [1788505385.448975085] [rotate_action_client]: remaining: 2.744
[INFO] [1788505385.462948480] [rotate_action_client]: remaining: 2.728
[INFO] [1788505385.478667967] [rotate_action_client]: remaining: 2.712
[INFO] [1788505385.495602534] [rotate_action_client]: remaining: 2.696
[INFO] [1788505385.515111556] [rotate_action_client]: remaining: 2.680
[INFO] [1788505385.526878403] [rotate_action_client]: remaining: 2.664
[INFO] [1788505385.543024799] [rotate_action_client]: remaining: 2.648
[INFO] [1788505385.558807405] [rotate_action_client]: remaining: 2.632
[INFO] [1788505385.579311863] [rotate_action_client]: remaining: 2.616
[INFO] [1788505385.594115864] [rotate_action_client]: remaining: 2.600
[INFO] [1788505385.607175527] [rotate_action_client]: remaining: 2.584
[INFO] [1788505385.624102475] [rotate_action_client]: remaining: 2.568
[INFO] [1788505385.638943797] [rotate_action_client]: remaining: 2.552
[INFO] [1788505385.655498223] [rotate_action_client]: remaining: 2.536
[INFO] [1788505385.672171888] [rotate_action_client]: remaining: 2.520
[INFO] [1788505385.690996494] [rotate_action_client]: remaining: 2.504
[INFO] [1788505385.703352584] [rotate_action_client]: remaining: 2.488
[INFO] [1788505385.719552190] [rotate_action_client]: remaining: 2.472
[INFO] [1788505385.738688921] [rotate_action_client]: remaining: 2.456
[INFO] [1788505385.751185463] [rotate_action_client]: remaining: 2.440
[INFO] [1788505385.769346358] [rotate_action_client]: remaining: 2.424
[INFO] [1788505385.783074684] [rotate_action_client]: remaining: 2.408
[INFO] [1788505385.799198419] [rotate_action_client]: remaining: 2.392
[INFO] [1788505385.814864937] [rotate_action_client]: remaining: 2.376
[INFO] [1788505385.830799259] [rotate_action_client]: remaining: 2.360
[INFO] [1788505385.846974572] [rotate_action_client]: remaining: 2.344
[INFO] [1788505385.862924990] [rotate_action_client]: remaining: 2.328
[INFO] [1788505385.879224368] [rotate_action_client]: remaining: 2.312
[INFO] [1788505385.895228265] [rotate_action_client]: remaining: 2.296
[INFO] [1788505385.914933634] [rotate_action_client]: remaining: 2.280
[INFO] [1788505385.927147034] [rotate_action_client]: remaining: 2.264
[INFO] [1788505385.943504069] [rotate_action_client]: remaining: 2.248
[INFO] [1788505385.959338035] [rotate_action_client]: remaining: 2.232
[INFO] [1788505385.975204536] [rotate_action_client]: remaining: 2.216
[INFO] [1788505385.993992751] [rotate_action_client]: remaining: 2.200
[INFO] [1788505386.006682253] [rotate_action_client]: remaining: 2.184
[INFO] [1788505386.024576295] [rotate_action_client]: remaining: 2.168
[INFO] [1788505386.039740800] [rotate_action_client]: remaining: 2.152
[INFO] [1788505386.055124044] [rotate_action_client]: remaining: 2.136
[INFO] [1788505386.071621935] [rotate_action_client]: remaining: 2.120
[INFO] [1788505386.090281399] [rotate_action_client]: remaining: 2.104
[INFO] [1788505386.103560363] [rotate_action_client]: remaining: 2.088
[INFO] [1788505386.119345913] [rotate_action_client]: remaining: 2.072
[INFO] [1788505386.139425099] [rotate_action_client]: remaining: 2.056
[INFO] [1788505386.151262859] [rotate_action_client]: remaining: 2.040
[INFO] [1788505386.170724846] [rotate_action_client]: remaining: 2.024
[INFO] [1788505386.174883730] [rotate_action_client]: requesting cancellation
[INFO] [1788505386.183670849] [rotate_action_client]: action status: 5

```

취소 시점 각도: 3 - 2.024 = 0.976

6. **통신 패턴 설계표** — 기능 / 선택한 모델 / 근거

| 기능 | 모델 | 근거 |
|---|---|---|
| 자세 스트리밍 | Topic | 연속 데이터이며 다수 구독 가능 |
| 순간이동 | Service | 짧은 요청-응답 |
| 목표 각도 회전 | Action | 시간이 걸리고 피드백·취소 필요 |
| 펜 색 설정 | Service | 한 번의 설정 요청과 성공 확인 |
| 거북이 추가 | Service | 생성 요청에 새 이름을 응답 |

## 문제 6 — 커스텀 인터페이스

### 인터페이스 정의 — 선행 구현

### Waypoint.msg 정의

경유점의 좌표 x, y, 도달 허용 오차 tolerance, 경유점 이름 label을 정의했다.

```text
float64 x
float64 y
float32 tolerance
string label
```

### WaypointList.msg 정의

메시지의 생성 시각과 기준 좌표계를 담는 Header와 여러 개의 Waypoint를 전달하기 위한 배열을 정의했다.

```text
std_msgs/Header header
turtle_interfaces/Waypoint[] waypoints
```

### SetGain.srv 정의

요청에는 PID 회전 게인 kp, ki, kd를 넣고 응답에는 적용 성공 여부와 메시지를 넣었다.

```text
float64 kp
float64 ki
float64 kd
---
bool success
string message
```

### DrawPolygon.action 정의

목표에는 변의 개수와 길이, 결과에는 총 이동 거리, 피드백에는 완료한 변의 수와 진행률을 정의했다.

```text
int32 sides
float64 side_length
---
float64 total_distance
---
int32 completed_sides
float32 progress
```

1. **`ros2 interface show turtle_interfaces/msg/WaypointList` 출력**

CMakeLists.txt의 `rosidl_generate_interfaces`에 네 인터페이스를 등록하고 빌드한 뒤 모두 확인한다.

```bash
cd lv1_module2_student/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select turtle_interfaces
source install/setup.bash
ros2 interface show turtle_interfaces/msg/Waypoint
ros2 interface show turtle_interfaces/msg/WaypointList
ros2 interface show turtle_interfaces/srv/SetGain
ros2 interface show turtle_interfaces/action/DrawPolygon
```

출력:

```text
'ros2 interface show turtle_interfaces/msg/Waypoint'
float64 x
float64 y
float32 tolerance
string label


'ros2 interface show turtle_interfaces/msg/WaypointList'
std_msgs/Header header
	builtin_interfaces/Time stamp
		int32 sec
		uint32 nanosec
	string frame_id
turtle_interfaces/Waypoint[] waypoints
	float64 x
	float64 y
	float32 tolerance
	string label


'ros2 interface show turtle_interfaces/srv/SetGain'
float64 kp
float64 ki
float64 kd
---
bool success
string message


'ros2 interface show turtle_interfaces/action/DrawPolygon'
int32 sides
float64 side_length
---
float64 total_distance
---
int32 completed_sides
float32 progress

```

2. **`ros2 topic echo /waypoints` 출력** — 중첩 필드 확인

/waypoints 토픽에 경유점 4개를 발행하고 중첩 필드와 배열을 확인한다.

```bash
# 터미널 1
ros2 run turtle_py waypoint_publisher

# 터미널 2
ros2 topic echo /waypoints turtle_interfaces/msg/WaypointList \
  --qos-durability transient_local --qos-reliability reliable --once
```

출력:

```text
header:
  stamp:
    sec: 1788505638
    nanosec: 746948836
  frame_id: world
waypoints:
- x: 2.0
  y: 2.0
  tolerance: 0.20000000298023224
  label: A
- x: 8.0
  y: 2.0
  tolerance: 0.20000000298023224
  label: B
- x: 8.0
  y: 8.0
  tolerance: 0.20000000298023224
  label: C
- x: 2.0
  y: 8.0
  tolerance: 0.20000000298023224
  label: D
---

```

3. **`DrawPolygon` 피드백 로그** — 총 이동 거리

삼각형 목표를 보내 변이 끝날 때마다 completed_sides와 progress 피드백을 확인한다.

```bash
# 터미널 1
ros2 run turtle_py polygon_action_server

# 터미널 2
ros2 run turtle_py polygon_action_client --ros-args -p sides:=3 -p side_length:=1.0
```

출력:

```text
[INFO] [1788505687.609232239] [polygon_action_client]: sides=1, progress=0.33
[INFO] [1788505690.726057707] [polygon_action_client]: sides=2, progress=0.67
[INFO] [1788505693.848794025] [polygon_action_client]: sides=3, progress=1.00
[INFO] [1788505693.849314420] [polygon_action_client]: status=4, total_distance=3.000

```

서버는 ReentrantCallbackGroup과 MultiThreadedExecutor를 사용하여 실행 도중 취소 콜백을 받을 수 있고, 취소 즉시 영속도 Twist를 발행한다. 삼각형·오각형·팔각형을 각각 실행한다.

```bash
ros2 run turtle_py polygon_action_client --ros-args -p sides:=3 -p side_length:=1.0
ros2 run turtle_py polygon_action_client --ros-args -p sides:=5 -p side_length:=1.0
ros2 run turtle_py polygon_action_client --ros-args -p sides:=8 -p side_length:=1.0
```

4. **삼각형·오각형·팔각형 궤적 캡처** (이미지 3장)

각 명령이 완료된 후 turtlesim 창의 전체 궤적이 보이게 캡처한다.

- 삼각형: `screenshots/problem6_triangle.png`
- 오각형: `screenshots/problem6_pentagon.png`
- 팔각형: `screenshots/problem6_octagon.png`

5. **액션 취소 처리 결과**

실행 중 취소를 요청해 즉시 정지하는지 확인한다.

```bash
ros2 run turtle_py polygon_action_client --ros-args \
  -p sides:=8 -p side_length:=1.0 -p cancel_after:=1.0
```

출력:

```text
[INFO] [1788505978.457807986] [polygon_action_client]: cancel requested
[INFO] [1788505978.509793962] [polygon_action_client]: status=5, total_distance=1.000

```

6. **인터페이스를 별도 패키지로 분리하는 이유**

메시지 정의를 노드 구현과 분리하면 인터페이스만 필요한 패키지가 rclpy, GUI, 제어 코드에 의존하지 않는다. 따라서 의존성 방향이 단순해지고 Python과 C++ 패키지에서 같은 인터페이스를 재사용할 수 있다.

## 문제 7 — QoS

1. **QoS 비호환 시 `topic info --verbose` 출력** — 양쪽 비교

Best-Effort 발행과 Reliable 구독 비호환을 다음과 같이 재현했다.

```bash
ros2 run turtle_py distance_publisher --ros-args -p use_sensor_qos:=true
ros2 run turtle_py distance_subscriber
ros2 topic info /turtle_distance --verbose
```

```text
Type: std_msgs/msg/Float32

Publisher count: 1

Node name: distance_publisher
Node namespace: /
Topic type: std_msgs/msg/Float32
Endpoint type: PUBLISHER
GID: 01.0f.84.6f.a5.a2.33.df.00.00.00.00.00.00.12.03.00.00.00.00.00.00.00.00
QoS profile:
  Reliability: BEST_EFFORT
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 1

Node name: distance_subscriber
Node namespace: /
Topic type: std_msgs/msg/Float32
Endpoint type: SUBSCRIPTION
GID: 01.0f.84.6f.b2.a2.28.15.00.00.00.00.00.00.11.04.00.00.00.00.00.00.00.00
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

```

`ros2 topic info /turtle_distance --verbose` 양쪽 endpoint 비교

| Endpoint | Node | Reliability | Durability | 호환 여부 |
|---|---|---|---|---|
| Publisher | `/distance_publisher` | BEST_EFFORT | VOLATILE | 불일치 |
| Subscription | `/distance_subscriber` | RELIABLE | VOLATILE | 불일치 |

2. **연결되지 않은 원인과 수정한 설정**

Best-Effort 보다 Reliable이 상위라서 호환되지 않았다. 구독자를 -p best_effort:=true로 실행해 Reliability를 Best-Effort로 수정했다.

```bash
ros2 run turtle_py distance_subscriber --ros-args -p best_effort:=true
```

출력:

```text
[WARN] [1788506195.541838498] [distance_subscriber]: distance 7.841 exceeds 2.500
[WARN] [1788506195.642078297] [distance_subscriber]: distance 7.841 exceeds 2.500
[WARN] [1788506195.741944754] [distance_subscriber]: distance 7.841 exceeds 2.500
[WARN] [1788506195.841965726] [distance_subscriber]: distance 7.841 exceeds 2.500
```
반복된 WARN은 연결 오류가 아니라 수신한 거리 값이 warn_distance=2.5를 초과했기 때문이다

3. **Transient Local과 Volatile 수신 결과 비교**

Transient Local과 Volatile 발행자를 각각 먼저 실행한 뒤 구독자를 나중에 실행해 과거 메시지 수신 여부를 비교한다.

```bash
# Transient Local 발행자를 먼저 실행
ros2 run turtle_py waypoint_publisher
ros2 topic echo /waypoints turtle_interfaces/msg/WaypointList \
  --qos-durability transient_local --qos-reliability reliable --once

# Volatile 발행자를 먼저 실행한 후, 늦게 구독
ros2 run turtle_py waypoint_publisher --ros-args -p transient_local:=false
timeout 5 ros2 topic echo /waypoints turtle_interfaces/msg/WaypointList \
  --qos-durability volatile --qos-reliability reliable
```

출력:

```text
Transient Local 실험:
header:
  stamp:
    sec: 1788506348
    nanosec: 645652106
  frame_id: world
waypoints:
- x: 2.0
  y: 2.0
  tolerance: 0.20000000298023224
  label: A
- x: 8.0
  y: 2.0
  tolerance: 0.20000000298023224
  label: B
- x: 8.0
  y: 8.0
  tolerance: 0.20000000298023224
  label: C
- x: 2.0
  y: 8.0
  tolerance: 0.20000000298023224
  label: D
---
Volatile 실험:
출력x
```
Volatile 구독자는 실행 전에 이미 발행된 메시지를 보관하거나 재전송받지 못했으므로, 5초 동안 메시지가 출력되지 않았다. 경유점은 한 번 발행한 후에도 계속 유효한 계획 데이터이므로 늦게 참여한 구독자에게 마지막 값을 전달하는 Transient Local이 적합하다.

4. **History depth 1에서의 메시지 누락 관찰**

10Hz 발행자를 실행한 상태에서 depth 1과 depth 10을 동일한 0.3초 콜백 지연으로 비교한다. 각 실험에서는 `qos_probe`를 먼저 실행한 뒤 발행자를 실행하며, 발행자는 2초 후 자동으로 종료한다.

```bash
# 터미널 1: 두 실험 동안 계속 실행
ros2 run turtlesim turtlesim_node

# 터미널 2: 첫 번째 실험
ros2 run turtle_py qos_probe --ros-args -p depth:=1 -p delay:=0.3

# 터미널 3: Probe가 실행된 것을 확인한 뒤 입력 — 2초 후 SIGINT로 종료
timeout --signal=INT 2s ros2 run turtle_py distance_publisher --ros-args -p use_sensor_qos:=true

# 터미널 2: 첫 번째 Probe를 종료한 뒤 두 번째 실험
ros2 run turtle_py qos_probe --ros-args -p depth:=10 -p delay:=0.3

# 터미널 3: 두 번째 Probe가 실행된 것을 확인한 뒤 다시 입력
timeout --signal=INT 2s ros2 run turtle_py distance_publisher --ros-args -p use_sensor_qos:=true
```

출력:

```text
'ros2 run turtle_py distance_publisher --ros-args -p use_sensor_qos:=true'

'ros2 run turtle_py qos_probe --ros-args -p depth:=1 -p delay:=0.3'
[INFO] [1788507874.564358493] [qos_probe]: received #1: 7.841
[INFO] [1788507874.865317163] [qos_probe]: received #2: 7.841
[INFO] [1788507875.166262463] [qos_probe]: received #3: 7.841
[INFO] [1788507875.467091725] [qos_probe]: received #4: 7.841
[INFO] [1788507875.767888946] [qos_probe]: received #5: 7.841
[INFO] [1788507876.068644585] [qos_probe]: received #6: 7.841
[INFO] [1788507876.369584360] [qos_probe]: received #7: 7.841


'ros2 run turtle_py qos_probe --ros-args -p depth:=10 -p delay:=0.3'
[INFO] [1788507922.431110508] [qos_probe]: received #1: 7.841
[INFO] [1788507922.732135553] [qos_probe]: received #2: 7.841
[INFO] [1788507923.033032998] [qos_probe]: received #3: 7.841
[INFO] [1788507923.333846430] [qos_probe]: received #4: 7.841
[INFO] [1788507923.634568538] [qos_probe]: received #5: 7.841
[INFO] [1788507923.935490124] [qos_probe]: received #6: 7.841
[INFO] [1788507924.236422899] [qos_probe]: received #7: 7.841
[INFO] [1788507924.537514081] [qos_probe]: received #8: 7.841
[INFO] [1788507924.838533200] [qos_probe]: received #9: 7.841
[INFO] [1788507925.139398849] [qos_probe]: received #10: 7.841
[INFO] [1788507925.440212138] [qos_probe]: received #11: 7.841
[INFO] [1788507925.741275709] [qos_probe]: received #12: 7.841
[INFO] [1788507926.042229087] [qos_probe]: received #13: 7.841
[INFO] [1788507926.343296673] [qos_probe]: received #14: 7.841
[INFO] [1788507926.644096066] [qos_probe]: received #15: 7.841
[INFO] [1788507926.944938386] [qos_probe]: received #16: 7.841

```
depth가 10으로 늘어남에 따라 subscriber가 저장하던 메시지 9개가 추가로 처리됨을 보았다.

5. **토픽 5종 QoS 설계표** — 토픽 / Reliability / Durability / 근거

| 토픽 | Reliability | Durability | 근거 |
|---|---|---|---|
| /turtle1/pose | Best Effort | Volatile | 최신 센서 상태가 중요 |
| /turtle1/cmd_vel | Reliable | Volatile | 제어 명령 유실 방지, 과거 명령 재사용 금지 |
| /waypoints | Reliable | Transient Local | 늦게 참가한 노드도 현재 계획 필요 |
| /turtle_distance | Best Effort | Volatile | 고주기 파생 센서 데이터 |
| /diagnostics | Reliable | Transient Local | 상태 유실 방지 및 늦은 진단 도구 지원 |

## 문제 8 — colcon 워크스페이스

1. **`colcon build` 빌드 순서 로그** — 인터페이스가 먼저인 이유


```text
Starting >>> turtle_interfaces
Starting >>> turtle_cpp
Finished <<< turtle_cpp [0.12s]
Finished <<< turtle_interfaces [0.87s]
Starting >>> turtle_examples
Starting >>> turtle_py
Finished <<< turtle_examples [0.73s]
Finished <<< turtle_py [0.74s]

Summary: 4 packages finished [1.72s]

```

colcon은 각 package.xml의 의존성 그래프를 위상 정렬한다. 독립 패키지는 병렬 빌드할 수 있지만 생성된 Python 인터페이스가 필요한 turtle_py는 turtle_interfaces 완료 후 빌드한다.

2. **`package.xml` 의존성 선언 부분** (발췌)


```xml
<depend>rclpy</depend>
<depend>turtlesim</depend>
<depend>std_msgs</depend>
<depend>geometry_msgs</depend>
<depend>turtle_interfaces</depend>
<depend>std_srvs</depend>
<depend>tf2_ros_py</depend>
<depend>visualization_msgs</depend>
```

3. **`setup.py` entry_points** (발췌) — 등록한 노드 목록

entry_points에 등록한 Python 파일

```text
distance_publisher, distance_subscriber, square_driver, service_client,
rotate_action_client, polygon_action_server, polygon_action_client,
waypoint_publisher, tf_marker_publisher, qos_probe
```

4. **source 전 실행 결과와 source 후 실행 결과** (두 출력 비교)

새 터미널에서 source하기 전에는 다음처럼 패키지를 못 찾는다.

```text
Package 'turtle_py' not found

```

source install/setup.bash 후에는 ros2 pkg executables turtle_py에 모든 실행 파일이 나타난다. source가 AMENT_PREFIX_PATH에 install prefix를, PYTHONPATH에 설치된 Python 모듈 경로를 추가하기 때문이다.

```text
bash-5.1$ source install/setup.bash
bash-5.1$ ros2 pkg executables turtle_py
turtle_py distance_publisher
turtle_py distance_subscriber
turtle_py polygon_action_client
turtle_py polygon_action_server
turtle_py qos_probe
turtle_py rotate_action_client
turtle_py service_client
turtle_py square_driver
turtle_py tf_marker_publisher
turtle_py waypoint_publisher
```

아래 명령어를 실행해서 새 쉘을 만들고 실행했기 때문에 사용자명이 다르게 보인다
```text
env -i \
  HOME="$HOME" \
  USER="$USER" \
  TERM="$TERM" \
  PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
  bash --noprofile --norc
```

5. **`src` / `build` / `install` / `log`의 역할**

| 디렉터리 | 역할 |
|---|---|
| src | 직접 작성하고 제출하는 패키지 원본 |
| build | 패키지별 임시 컴파일·빌드 파일 |
| install | 실행 가능한 프로그램, 인터페이스, 환경 스크립트 |
| log | colcon 빌드·테스트 실행 로그 |

## 문제 9 — launch와 파라미터

1. **`ros2 launch` 실행 출력**

turtle_system.launch.py는 turtlesim, 거리 발행자, 경고 구독자, DrawPolygon 액션 서버를 한 번에 실행한다. 기존 turtlesim과 함께 검증할 때만 start_turtlesim:=false를 사용했다.

```bash
ros2 launch turtle_py turtle_system.launch.py
```

출력:

```text
[INFO] [launch]: All log files can be found below /home/pa19/.ros/log/2026-09-04-17-01-31-376387-pa19-Legion-Pro-5-16IAX10-44613
[INFO] [launch]: Default logging verbosity is set to INFO
[INFO] [turtlesim_node-1]: process started with pid [44614]
[INFO] [distance_publisher-2]: process started with pid [44616]
[INFO] [distance_subscriber-3]: process started with pid [44618]
[INFO] [polygon_action_server-4]: process started with pid [44620]
[turtlesim_node-1] Warning: Ignoring XDG_SESSION_TYPE=wayland on Gnome. Use QT_QPA_PLATFORM=wayland to run on Wayland anyway.

```

2. **`ros2 node list` 결과** — 동시 실행된 노드

ros2 node list로 네 개의 노드가 동시에 실행되는지 확인한다.

```bash
ros2 node list
```

출력:

```text
/distance_publisher
/distance_subscriber
/polygon_action_server
/turtlesim

```

3. **`ros2 param get`으로 확인한 주입 값**

ros2 param get으로 YAML에서 주입한 publish_rate와 warn_distance를 확인했다.

```bash
ros2 param get /distance_publisher publish_rate
ros2 param get /distance_subscriber warn_distance
```

출력:

```text
Double value is: 10.0
Double value is: 2.5

```

4. **YAML 값 변경 전후 동작 차이**

config/params.yaml의 warn_distance를 2.5에서 0.8로 바꾸고 재빌드 없이 launch만 다시 실행해 경고 빈도를 비교한다. 실험 후 제출할 YAML은 기본값 2.5로 되돌린다.

```bash
ros2 param get /distance_subscriber warn_distance
# config/params.yaml에서 warn_distance: 0.8로 임시 변경 후 launch 재실행
ros2 param get /distance_subscriber warn_distance
```

출력:

```text
'변경 전'
Double value is: 2.5

'변경 후'
Double value is: 0.8
```

5. **네임스페이스 적용 후 `topic list`** (출력)

/spawn으로 turtle2를 만든 뒤 두 번째 발행자를 활성화했다.

```bash
ros2 launch turtle_py turtle_system.launch.py start_turtle2_status:=true
ros2 topic list
```

출력:

```text
/parameter_events
/rosout
/turtle1/cmd_vel
/turtle1/color_sensor
/turtle1/pose
/turtle2/pose
/turtle2/turtle_distance
/turtle_distance

```

## 문제 10 — 시각화·기록·테스트

1. **`rqt_graph` 캡처** — 데이터 미수신 진단 절차

캡처: `screenshots/problem10_rqt_graph.png`

turtlesim을 종료한 뒤 다음 명령으로 발행률 변화를 관찰한다.

```bash
ros2 topic hz /turtle_distance
```

출력:

```text
average rate: 10.002
	min: 0.100s max: 0.100s std dev: 0.00014s window: 12
average rate: 10.001
	min: 0.100s max: 0.100s std dev: 0.00012s window: 23
average rate: 10.001
	min: 0.100s max: 0.100s std dev: 0.00012s window: 34
average rate: 10.000
	min: 0.100s max: 0.100s std dev: 0.00012s window: 44
average rate: 10.000
	min: 0.100s max: 0.100s std dev: 0.00012s window: 55
average rate: 10.000
	min: 0.100s max: 0.100s std dev: 0.00012s window: 66
(미수신)
```
발행이 멈춰서 subscriber에도 변화가 없음


미수신 진단 순서는 다음과 같다.

1. ros2 node list, ros2 topic list로 프로세스와 토픽 존재 확인
2. ros2 topic info 토픽명 --verbose로 타입, publisher/subscriber 수, QoS 비교
3. ros2 topic echo /turtle1/pose로 upstream 입력 확인
4. ros2 topic hz /turtle_distance로 발행률 확인
5. ros2 node info 노드명과 ros2 param list/get으로 remap·parameter 확인
6. 로그의 QoS incompatible 경고와 ROS domain/network 설정 확인

2. **RViz2 TF + 경유점 마커 캡처**

TF·Marker 노드를 실행하고 RViz2에서 Fixed Frame을 world로 설정한 뒤 TF와 /waypoint_markers를 표시한다.

```bash
ros2 run turtle_py waypoint_publisher
ros2 run turtle_py tf_marker_publisher
rviz2
```

출력:

```text
[INFO] [1788509594.614209953] [waypoint_publisher]: published 4 durable waypoints

```

캡처: `screenshots/problem10_waypoint_markers.png`

3. **`ros2 bag play` 재생 중 구독자 로그** — 기록된 토픽과 메시지 수

두 토픽을 약 30초간 기록한다. 기존 3.65초 bag은 새 기록으로 교체해야 한다.

```bash
# lv1_module2_student 디렉터리에서 실행
cd /home/pa19/physicalai-lv1-assignments/hw/physicalai-lv1-assignments/lv1_module2_student
timeout --signal=INT 30s ros2 bag record -o problem10 /turtle1/pose /turtle_distance
mv problem10/metadata.yaml problem10/problem10_0.db3 bags/
rmdir problem10
ros2 bag info bags
```

출력:

```text
[INFO] [1788509921.069776117] [rosbag2_recorder]: Press SPACE for pausing/resuming
[INFO] [1788509921.070450910] [rosbag2_storage]: Opened database 'bags/problem10_0.db3' for READ_WRITE.
[INFO] [1788509921.070763933] [rosbag2_recorder]: Listening for topics...
[INFO] [1788509921.070912328] [rosbag2_recorder]: Event publisher thread: Starting
[INFO] [1788509921.071366183] [rosbag2_recorder]: Subscribed to topic '/turtle_distance'
[INFO] [1788509921.071867300] [rosbag2_recorder]: Subscribed to topic '/turtle1/pose'
[INFO] [1788509921.071898723] [rosbag2_recorder]: Recording...
[INFO] [1788509921.072063818] [rosbag2_recorder]: All requested topics are subscribed. Stopping discovery...
[INFO] [1788509950.930738043] [rosbag2_cpp]: Writing remaining messages from cache to the bag. It may take a while
[INFO] [1788509950.931270076] [rosbag2_recorder]: Event publisher thread: Exiting
[INFO] [1788509950.931435350] [rosbag2_recorder]: Recording stopped


```

기록 후 turtlesim과 거리 발행 노드를 완전히 종료하고 bag을 재생한 상태에서 구독자가 수신하는지 확인한다.

```bash
# 터미널 1: 먼저 실행해 재생 시작 부분부터 구독
cd /home/pa19/physicalai-lv1-assignments/hw/physicalai-lv1-assignments/lv1_module2_student
ros2 run turtle_py distance_subscriber

# 터미널 2: 구독자가 실행된 것을 확인한 뒤 재생
cd /home/pa19/physicalai-lv1-assignments/hw/physicalai-lv1-assignments/lv1_module2_student
ros2 bag play bags
```

출력:

```text
'ros2 bag play bags'
Files:             problem10_0.db3
Bag size:          153.4 KiB
Storage id:        sqlite3
Duration:          29.839787502s
Start:             Sep  4 2026 17:18:41.075723381 (1788509921.075723381)
End:               Sep  4 2026 17:19:10.915510883 (1788509950.915510883)
Messages:          2164
Topic information: Topic: /turtle1/pose | Type: turtlesim/msg/Pose | Count: 1866 | Serialization Format: cdr
                   Topic: /turtle_distance | Type: std_msgs/msg/Float32 | Count: 298 | Serialization Format: cdr

[INFO] [1788512416.731178561] [rosbag2_storage]: Opened database 'bags/problem10_0.db3' for READ_ONLY.
[INFO] [1788512416.731224761] [rosbag2_player]: Set rate to 1
[INFO] [1788512416.733060418] [rosbag2_player]: Adding keyboard callbacks.
[INFO] [1788512416.733079324] [rosbag2_player]: Press SPACE for Pause/Resume
[INFO] [1788512416.733085834] [rosbag2_player]: Press CURSOR_RIGHT for Play Next Message
[INFO] [1788512416.733091066] [rosbag2_player]: Press CURSOR_UP for Increase Rate 10%
[INFO] [1788512416.733095719] [rosbag2_player]: Press CURSOR_DOWN for Decrease Rate 10%
[INFO] [1788512416.733283936] [rosbag2_storage]: Opened database 'bags/problem10_0.db3' for READ_ONLY.


'subscriber'
[WARN] [1788512429.224120471] [distance_subscriber]: distance 9.177 exceeds 2.500
[WARN] [1788512429.324063560] [distance_subscriber]: distance 9.177 exceeds 2.500
[WARN] [1788512429.423642253] [distance_subscriber]: distance 9.177 exceeds 2.500
[WARN] [1788512429.523861988] [distance_subscriber]: distance 9.177 exceeds 2.500

```

4. **`pytest` 통과 출력** — 작성한 테스트 3개의 의도

순수 함수는 거리, 목표 방향 및 각도 정규화, inclusive 허용 오차 판정을 검사한다. 정상값, 경계값, NaN·음수 tolerance·목표와 현재 위치 동일 예외를 포함했다.

```text
...                                                                      [100%]
3 passed in 0.00s
```

5. **함수를 틀리게 바꿨을 때 실패 출력**

<=에서 <로 바꿨을 때

```text
FAILED test_math_utils.py::test_waypoint_tolerance_is_inclusive
assert False
1 failed, 2 passed in 0.01s
```

<=로 되돌리면 통과한다.

6. **예외 처리·logging 동작 확인**

publish_rate=0은 시작 시 10Hz fallback을 경고하고 실행 중에 0으로 변경하면 거부한다. 빈 WaypointList는 TF/Marker 노드가 empty waypoint list ignored 경고만 남기고 실행된다.

```text
[WARN] publish_rate must be > 0; using 10 Hz
[WARN] rejected publish_rate <= 0
[WARN] empty waypoint list ignored
```
