#pragma once

#include <vector>
#include <string>


#ifdef _WIN32
  #define LLFIO_EXPORT __declspec(dllexport)
#else
  #define LLFIO_EXPORT
#endif

LLFIO_EXPORT void llfio();
LLFIO_EXPORT void llfio_print_vector(const std::vector<std::string> &strings);
