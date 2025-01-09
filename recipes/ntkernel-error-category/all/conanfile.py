import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.50.0"


class NTKernelErrorConan(ConanFile):
    name = "ntkernel-error-category"
    description = "A portable C++ 11 STL std::error_category implementation for the NT kernel error code space"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ned14/ntkernel-error-category"
    topics = ("result", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    
    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "clang": "3.9",
            "gcc": "6",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("This library is only for the Windows platform")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "Licence.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"),
                                  dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.ipp", src=os.path.join(self.source_folder, "include"),
                                  dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"),
                                  dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ntkernel-error")
        self.cpp_info.set_property("cmake_target_name", "ntkernel-error::ntkernel-error")
        self.cpp_info.set_property("pkg_config_name", "ntkernel-error")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
