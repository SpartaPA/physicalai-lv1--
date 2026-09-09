cmake_minimum_required(VERSION 3.22)
project(sensor_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_compile_options(-Wall -Wextra -pedantic)

add_executable(sensor_demo main.cpp sensor.cpp)
add_executable(no_virtual_destructor no_virtual_destructor.cpp)
add_executable(leak_demo leak_demo.cpp)
