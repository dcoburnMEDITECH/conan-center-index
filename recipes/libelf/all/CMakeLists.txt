cmake_minimum_required(VERSION 3.15)
project(elf LANGUAGES C)

if(EXISTS "${LIBELF_SRC_DIR}/lib/sys_elf.h.w32")
    file(RENAME "${LIBELF_SRC_DIR}/lib/sys_elf.h.w32" "${LIBELF_SRC_DIR}/lib/sys_elf.h")
    file(RENAME "${LIBELF_SRC_DIR}/lib/config.h.w32" "${LIBELF_SRC_DIR}/lib/config.h")
endif()

file(GLOB_RECURSE SOURCES "${LIBELF_SRC_DIR}/lib/*.c")
file(GLOB_RECURSE HEADERS "${LIBELF_SRC_DIR}/lib/*.h")

add_library(${PROJECT_NAME} ${SOURCES})
set_target_properties(${PROJECT_NAME} PROPERTIES
    PUBLIC_HEADER "${HEADERS}"
    WINDOWS_EXPORT_ALL_SYMBOLS TRUE
)
target_include_directories(${PROJECT_NAME} SYSTEM PUBLIC "${LIBELF_SRC_DIR}/lib")
target_compile_definitions(${PROJECT_NAME} PUBLIC HAVE_MEMCMP=1 HAVE_MEMCPY=1 HAVE_MEMMOVE=1 HAVE_CONFIG_H=1)

include(GNUInstallDirs)

install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/libelf
)

install(FILES "${LIBELF_SRC_DIR}/lib/libelf.h" DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(FILES "${LIBELF_SRC_DIR}/lib/gelf.h"   DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(FILES "${LIBELF_SRC_DIR}/lib/nlist.h"  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
