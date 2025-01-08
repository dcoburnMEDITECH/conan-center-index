cmake_minimum_required(VERSION 3.15)
project(llfio CXX)




add_library(llfio src/llfio.cpp)
target_include_directories(llfio PUBLIC include)



set_target_properties(llfio PROPERTIES PUBLIC_HEADER "include/llfio.h")
install(TARGETS llfio)
