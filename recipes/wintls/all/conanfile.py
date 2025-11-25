from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=2.0"


class PackageConan(ConanFile):
    name = "wintls"
    description = "WinTLS is a Windows TLS library that provides boost with schannel support."
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case not listed there, use "DocumentRef-<license-file-name>:LicenseRef-<package-name>"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wintls.dev/"
    # no "conan" and project name in topics. Use topics from the upstream listed on GH
    topics = ("windows", "tls", "ssl", "networking", "cplusplus", "boost", "async-programming", "asio", "sspi", "schannel")
    package_type = "header-library"
    settings = "os", "compiler"
    options = {
        "with_asio": [True, False],
    }
    default_options = {
        "with_asio": False,
    }
    # Do not copy sources to build folder for header only projects, unless you need to apply patches
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    # same package ID for any package
    def package_id(self):
        self.info.clear()

    def validate(self):
        # Validate the minimum cpp standard supported when installing the package. For C++ projects only
        check_min_cppstd(self, 14)
        # in case it does not work in another configuration, it should be validated here. Always comment the reason including the upstream issue.
        # INFO: Upstream does not support DLL: See <URL>
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} must be used on Windows.")

    def source(self):
        # Download source package and extract to source folder
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # The attribute no_copy_source should not be used when applying patches in build
        # Using patches is always the last resort to fix issues. If possible, try to fix the issue in the upstream project.
    
    def requirements(self):
        if self.options.get_safe("with_asio", True):
            self.requires("asio/1.34.2")
        else:
            self.requires("boost/[>=1.84.0 <1.88.0]")

    # Suppress warning message about missing build() method when running Conan
    def build(self):
        pass

    # Copy all files to the package folder
    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        # Prefer CMake.install() or similar in case the upstream offers an official method to install the headers.
        copy(self, "*.hpp", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        copy(self, "*.hpp", os.path.join(self.source_folder, "include","wintls"), os.path.join(self.package_folder, "include","wintls"))
        copy(self, "*.hpp", os.path.join(self.source_folder, "include","wintls","detail"), os.path.join(self.package_folder, "include","wintls","detail"))


    def package_info(self):
        # crypt32, secur32, ws2_32 and wsock32 are required to use wintls
        self.cpp_info.system_libs = ["crypt32", "secur32", "ws2_32", "wsock32"]
        if self.options.get_safe("with_asio", True):
            self.cpp_info.defines = ["WINTLS_USE_STANDALONE_ASIO"]
        # Folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

    