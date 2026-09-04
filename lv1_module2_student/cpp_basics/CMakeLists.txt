cmake_minimum_required(VERSION 3.22)
project(robot_cpp_basics LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_compile_options(-Wall -Wextra -pedantic)

add_executable(stop_distance stop_distance.cpp)
add_executable(motor_demo main.cpp motor.cpp)
