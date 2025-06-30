cmake_minimum_required(VERSION 3.21)
project(Projeto C)

set(CMAKE_C_STANDARD 11)

add_compile_options(-Wall -Wextra)

add_executable(Projeto main.c Source.File.c header_file.h)
