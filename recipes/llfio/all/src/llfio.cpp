#include <iostream>
#include "llfio.h"



void llfio(){
    

    #ifdef NDEBUG
    std::cout << "llfio/20241213: Hello World Release!\n";
    #else
    std::cout << "llfio/20241213: Hello World Debug!\n";
    #endif

    // ARCHITECTURES
    #ifdef _M_X64
    std::cout << "  llfio/20241213: _M_X64 defined\n";
    #endif

    #ifdef _M_IX86
    std::cout << "  llfio/20241213: _M_IX86 defined\n";
    #endif

    #ifdef _M_ARM64
    std::cout << "  llfio/20241213: _M_ARM64 defined\n";
    #endif

    #if __i386__
    std::cout << "  llfio/20241213: __i386__ defined\n";
    #endif

    #if __x86_64__
    std::cout << "  llfio/20241213: __x86_64__ defined\n";
    #endif

    #if __aarch64__
    std::cout << "  llfio/20241213: __aarch64__ defined\n";
    #endif

    // Libstdc++
    #if defined _GLIBCXX_USE_CXX11_ABI
    std::cout << "  llfio/20241213: _GLIBCXX_USE_CXX11_ABI "<< _GLIBCXX_USE_CXX11_ABI << "\n";
    #endif

    // MSVC runtime
    #if defined(_DEBUG)
        #if defined(_MT) && defined(_DLL)
        std::cout << "  llfio/20241213: MSVC runtime: MultiThreadedDebugDLL\n";
        #elif defined(_MT)
        std::cout << "  llfio/20241213: MSVC runtime: MultiThreadedDebug\n";
        #endif
    #else
        #if defined(_MT) && defined(_DLL)
        std::cout << "  llfio/20241213: MSVC runtime: MultiThreadedDLL\n";
        #elif defined(_MT)
        std::cout << "  llfio/20241213: MSVC runtime: MultiThreaded\n";
        #endif
    #endif

    // COMPILER VERSIONS
    #if _MSC_VER
    std::cout << "  llfio/20241213: _MSC_VER" << _MSC_VER<< "\n";
    #endif

    #if _MSVC_LANG
    std::cout << "  llfio/20241213: _MSVC_LANG" << _MSVC_LANG<< "\n";
    #endif

    #if __cplusplus
    std::cout << "  llfio/20241213: __cplusplus" << __cplusplus<< "\n";
    #endif

    #if __INTEL_COMPILER
    std::cout << "  llfio/20241213: __INTEL_COMPILER" << __INTEL_COMPILER<< "\n";
    #endif

    #if __GNUC__
    std::cout << "  llfio/20241213: __GNUC__" << __GNUC__<< "\n";
    #endif

    #if __GNUC_MINOR__
    std::cout << "  llfio/20241213: __GNUC_MINOR__" << __GNUC_MINOR__<< "\n";
    #endif

    #if __clang_major__
    std::cout << "  llfio/20241213: __clang_major__" << __clang_major__<< "\n";
    #endif

    #if __clang_minor__
    std::cout << "  llfio/20241213: __clang_minor__" << __clang_minor__<< "\n";
    #endif

    #if __apple_build_version__
    std::cout << "  llfio/20241213: __apple_build_version__" << __apple_build_version__<< "\n";
    #endif

    // SUBSYSTEMS

    #if __MSYS__
    std::cout << "  llfio/20241213: __MSYS__" << __MSYS__<< "\n";
    #endif

    #if __MINGW32__
    std::cout << "  llfio/20241213: __MINGW32__" << __MINGW32__<< "\n";
    #endif

    #if __MINGW64__
    std::cout << "  llfio/20241213: __MINGW64__" << __MINGW64__<< "\n";
    #endif

    #if __CYGWIN__
    std::cout << "  llfio/20241213: __CYGWIN__" << __CYGWIN__<< "\n";
    #endif
}

void llfio_print_vector(const std::vector<std::string> &strings) {
    for(std::vector<std::string>::const_iterator it = strings.begin(); it != strings.end(); ++it) {
        std::cout << "llfio/20241213 " << *it << std::endl;
    }
}
