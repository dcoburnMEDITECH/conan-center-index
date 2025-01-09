from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save, replace_in_file
import os

class llfioRecipe(ConanFile):
    name = "llfio"
    package_type = "library"

    # Optional metadata
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ned14/llfio"
    description = "P1031 low level file i/o and filesystem library for the C++ standard"
    topics = ("c++", "low level", "file io")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("outcome/[>=2.2.9 <3]")
        self.requires("quickcpplib/cci.20231208")
        if self.settings.os == "Windows":
            self.requires("ntkernel-error-category/1.0.0")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
    
    def build(self):
        pass

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"),
                                  dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.ipp", src=os.path.join(self.source_folder, "include"),
                                  dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"),
                                  dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "llfio")
        self.cpp_info.set_property("cmake_target_name", "llfio::llfio")
        self.cpp_info.set_property("pkg_config_name", "llfio")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

