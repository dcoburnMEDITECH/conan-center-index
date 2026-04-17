import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.env import Environment
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, save
from conan.tools.microsoft import VCVars, is_msvc

required_conan_version = ">=2.0"


class PdfiumConan(ConanFile):
    name = "pdfium"
    description = "PDF generation and rendering library."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://opensource.google/projects/pdfium"
    topics = ("generate", "generation", "rendering", "pdf", "document", "print")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        self.folders.source = "src"
        self.folders.build = "src"  # GN outputs inside src/out/Default

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("libjpeg/9e")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("libtiff/[>=4.6 <5]")
        self.requires("openjpeg/[>=2.5 <3]")
        self.requires("freetype/[>=2.13 <3]")
        self.requires("icu/74.2")

    def validate(self):
        if self.settings.os not in ("Windows", "Linux"):
            raise ConanInvalidConfiguration(
                f"{self.ref} is only supported on Windows and Linux at this time"
            )
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("gn/cci.20240611")
        self.tool_requires("ninja/[>=1.10 <2]")

    def source(self):
        srcs = self.conan_data["sources"][self.version]
        get(self, **srcs["pdfium"],
            destination=self.source_folder, strip_root=True)
        get(self, **srcs["build"],
            destination=os.path.join(self.source_folder, "build"))
        get(self, **srcs["abseil_cpp"],
            destination=os.path.join(self.source_folder, "third_party", "abseil-cpp"))
        get(self, **srcs["fast_float"],
            destination=os.path.join(self.source_folder, "third_party", "fast_float", "src"))

    # ── GN helpers ───────────────────────────────────────────────────────

    @property
    def _gn_os(self):
        return {
            "Windows": "win",
            "Linux": "linux",
            "Macos": "mac",
        }.get(str(self.settings.os), str(self.settings.os).lower())

    @property
    def _gn_arch(self):
        return {
            "x86_64": "x64",
            "x86": "x86",
            "armv8": "arm64",
        }.get(str(self.settings.arch), str(self.settings.arch))

    @staticmethod
    def _fwd(p):
        """Forward-slash a path for GN."""
        return p.replace("\\", "/")

    def _gn_str_list(self, items):
        return ", ".join(f'"{self._fwd(d)}"' for d in items)

    def _gn_libs(self, info):
        if is_msvc(self):
            return ", ".join(f'"{l}.lib"' for l in info.libs)
        return ", ".join(f'"{l}"' for l in info.libs)

    def _dep_info(self, name):
        return self.dependencies[name].cpp_info.aggregated_components()

    # ── generate() ───────────────────────────────────────────────────────

    def generate(self):
        if is_msvc(self):
            VCVars(self).generate()
        env = Environment()
        if is_msvc(self):
            env.define("DEPOT_TOOLS_WIN_TOOLCHAIN", "0")
        if self.settings.compiler == "gcc":
            env.define("CC", "gcc")
            env.define("CXX", "g++")
            env.define("LD", "g++")
        elif str(self.settings.compiler) in ("clang", "apple-clang"):
            env.define("CC", "clang")
            env.define("CXX", "clang++")
            env.define("LD", "clang++")
        env.vars(self).save_script("conanbuild_gn")

    # ── build() ──────────────────────────────────────────────────────────

    def build(self):
        src = self.source_folder

        # ── Apply conandata.yml patches (MSVC compat, test dep stripping) ─
        apply_conandata_patches(self)

        # ── Stub gclient-generated files ─────────────────────────────────
        self._patch_gclient_stubs(src)

        # ── Stub GN targets for gclient-only deps ───────────────────────
        self._patch_strip_test_deps(src)

        # ── Patch third-party dep configs with Conan paths ───────────────
        self._patch_third_party_deps(src)

        # ── Stub ICU BUILD.gn (ICU comes from Conan, not downloaded) ─────
        self._patch_icu(src)

        # ── Patch freetype BUILD.gn (Conan freetype, no pkg-config) ──────
        self._patch_freetype(src)

        # ── GN gen + Ninja ───────────────────────────────────────────────
        gn_args = self._build_gn_args()
        with chdir(self, src):
            self.run(f'gn gen out/Default --args="{" ".join(gn_args)}"')
            self.run("ninja -C out/Default pdfium")

    def _patch_gclient_stubs(self, src):
        # python3 → python on Windows
        if self.settings.os == "Windows":
            replace_in_file(self, os.path.join(src, ".gn"),
                            'script_executable = "python3"',
                            'script_executable = "python"',
                            strict=False)

        # LASTCHANGE.committime
        save(self, os.path.join(src, "build", "util", "LASTCHANGE.committime"),
             "1700000000\n")

        # gclient_args.gni
        save(self, os.path.join(src, "build", "config", "gclient_args.gni"),
             textwrap.dedent("""\
                 # Generated by Conan pdfium recipe.
                 checkout_android = false
                 checkout_android_prebuilts_build_tools = false
                 checkout_clang_coverage_tools = false
                 checkout_skia = false
                 checkout_src_internal = false
             """))

        # siso.gni stub (avoids path_exists() which is newer than gn/cci.20240611)
        save(self, os.path.join(src, "build", "toolchain", "siso.gni"),
             textwrap.dedent("""\
                 import("//build/config/gclient_args.gni")
                 declare_args() { use_siso = false }
                 siso_logs = [ "use_siso=false" ]
             """))

    def _patch_strip_test_deps(self, src):
        """Create stub GN targets for gclient-only deps not available in Conan builds."""
        # Stub third_party/test_fonts/BUILD.gn (referenced by testing/BUILD.gn)
        test_fonts_dir = os.path.join(src, "third_party", "test_fonts")
        os.makedirs(test_fonts_dir, exist_ok=True)
        save(self, os.path.join(test_fonts_dir, "BUILD.gn"),
             '# Stub — test fonts not needed for library build.\n'
             'group("test_fonts") {}\n')

        # Stub buildtools/third_party/libc++/BUILD.gn (clang targets always reference it)
        libcxx_dir = os.path.join(src, "buildtools", "third_party", "libc++")
        os.makedirs(libcxx_dir, exist_ok=True)
        save(self, os.path.join(libcxx_dir, "BUILD.gn"), textwrap.dedent("""\
            # Stub — using system libc++, not chromium-bundled.
            group("custom_headers") {}
            group("libcxx_headers") {}
            group("libc++") {}
            group("all_modules") {}
        """))

        # Stub tools/win/DebugVisualizers/BUILD.gn (referenced by abseil-cpp)
        if self.settings.os == "Windows":
            dbgvis_dir = os.path.join(src, "tools", "win", "DebugVisualizers")
            os.makedirs(dbgvis_dir, exist_ok=True)
            save(self, os.path.join(dbgvis_dir, "BUILD.gn"), textwrap.dedent("""\
                # Stub — debug visualizers not needed for library build.
                config("absl") {}
            """))

    def _patch_third_party_deps(self, src):
        third_party_gn = os.path.join(src, "third_party", "BUILD.gn")

        zlib_info = self._dep_info("zlib")
        jpeg_info = self._dep_info("libjpeg")
        png_info = self._dep_info("libpng")
        tiff_info = self._dep_info("libtiff")
        openjp_info = self._dep_info("openjpeg")

        # zlib
        replace_in_file(self, third_party_gn,
            'config("system_zlib_config") {\n'
            '  libs = [ "z" ]\n'
            '  defines = [ "USE_SYSTEM_ZLIB" ]\n'
            '}',
            'config("system_zlib_config") {{\n'
            '  include_dirs = [ {inc} ]\n'
            '  lib_dirs = [ {lib} ]\n'
            '  libs = [ {libs} ]\n'
            '  defines = [ "USE_SYSTEM_ZLIB" ]\n'
            '}}'.format(
                inc=self._gn_str_list(zlib_info.includedirs),
                lib=self._gn_str_list(zlib_info.libdirs),
                libs=self._gn_libs(zlib_info)),
            strict=False)

        # libjpeg
        replace_in_file(self, third_party_gn,
            'config("system_libjpeg_config") {\n'
            '    libs = [ "jpeg" ]\n'
            '    defines = [ "USE_SYSTEM_LIBJPEG" ]\n'
            '  }',
            'config("system_libjpeg_config") {{\n'
            '    include_dirs = [ {inc} ]\n'
            '    lib_dirs = [ {lib} ]\n'
            '    libs = [ {libs} ]\n'
            '    defines = [ "USE_SYSTEM_LIBJPEG", "LIBJPEG_STATIC" ]\n'
            '  }}'.format(
                inc=self._gn_str_list(jpeg_info.includedirs),
                lib=self._gn_str_list(jpeg_info.libdirs),
                libs=self._gn_libs(jpeg_info)),
            strict=False)

        # libpng
        replace_in_file(self, third_party_gn,
            'config("system_libpng_config") {\n'
            '    libs = [ "png" ]\n'
            '    defines = [ "USE_SYSTEM_LIBPNG" ]\n'
            '  }',
            'config("system_libpng_config") {{\n'
            '    include_dirs = [ {inc} ]\n'
            '    lib_dirs = [ {lib} ]\n'
            '    libs = [ {libs} ]\n'
            '    defines = [ "USE_SYSTEM_LIBPNG" ]\n'
            '  }}'.format(
                inc=self._gn_str_list(png_info.includedirs),
                lib=self._gn_str_list(png_info.libdirs),
                libs=self._gn_libs(png_info)),
            strict=False)

        # libtiff
        replace_in_file(self, third_party_gn,
            '    config("system_tiff_config") {\n'
            '      libs = [ "tiff" ]\n'
            '      defines = [ "USE_SYSTEM_LIBTIFF" ]\n'
            '    }',
            '    config("system_tiff_config") {{\n'
            '      include_dirs = [ {inc} ]\n'
            '      lib_dirs = [ {lib} ]\n'
            '      libs = [ {libs} ]\n'
            '      defines = [ "USE_SYSTEM_LIBTIFF" ]\n'
            '    }}'.format(
                inc=self._gn_str_list(tiff_info.includedirs),
                lib=self._gn_str_list(tiff_info.libdirs),
                libs=self._gn_libs(tiff_info)),
            strict=False)

        # openjpeg — replace pkg_config block with a regular config
        replace_in_file(self, third_party_gn,
            'if (use_system_libopenjpeg2) {\n'
            '  pkg_config("libopenjpeg2_from_pkgconfig") {\n'
            '    defines = [ "USE_SYSTEM_LIBOPENJPEG2" ]\n'
            '    packages = [ "libopenjp2" ]\n'
            '  }\n'
            '}',
            'if (use_system_libopenjpeg2) {{\n'
            '  config("libopenjpeg2_from_pkgconfig") {{\n'
            '    include_dirs = [ {inc} ]\n'
            '    lib_dirs = [ {lib} ]\n'
            '    libs = [ {libs} ]\n'
            '    defines = [ "USE_SYSTEM_LIBOPENJPEG2", "OPJ_STATIC" ]\n'
            '  }}\n'
            '}}'.format(
                inc=self._gn_str_list(openjp_info.includedirs),
                lib=self._gn_str_list(openjp_info.libdirs),
                libs=self._gn_libs(openjp_info)),
            strict=False)

        # Ensure OPJ_STATIC is present (idempotent)
        replace_in_file(self, third_party_gn,
            'defines = [ "USE_SYSTEM_LIBOPENJPEG2" ]',
            'defines = [ "USE_SYSTEM_LIBOPENJPEG2", "OPJ_STATIC" ]',
            strict=False)

    def _patch_icu(self, src):
        """Write a stub third_party/icu/BUILD.gn pointing to Conan ICU
        and create header shim for #include "third_party/icu/source/common/..."."""
        icu_info = self._dep_info("icu")
        icu_gn = os.path.join(src, "third_party", "icu", "BUILD.gn")
        save(self, icu_gn, textwrap.dedent(f"""\
            # Generated by Conan pdfium recipe — routes ICU to Conan package.
            config("conan_icu_config") {{
              include_dirs = [ {self._gn_str_list(icu_info.includedirs)} ]
              lib_dirs = [ {self._gn_str_list(icu_info.libdirs)} ]
              libs = [ {self._gn_libs(icu_info)} ]
            }}
            group("icuuc") {{
              public_configs = [ ":conan_icu_config" ]
            }}
        """))

        # pdfium source files include "third_party/icu/source/common/unicode/uchar.h"
        # Create a directory junction/symlink so those includes find Conan ICU headers.
        icu_common_dir = os.path.join(src, "third_party", "icu", "source", "common")
        os.makedirs(icu_common_dir, exist_ok=True)
        # Find the Conan ICU include dir that contains the "unicode/" subfolder
        for inc_dir in icu_info.includedirs:
            unicode_dir = os.path.join(inc_dir, "unicode")
            if os.path.isdir(unicode_dir):
                target = os.path.join(icu_common_dir, "unicode")
                if not os.path.exists(target):
                    os.symlink(unicode_dir, target, target_is_directory=True)
                break

    def _patch_freetype(self, src):
        """Write a Conan-aware build/config/freetype/BUILD.gn (no pkg-config)."""
        ft_info = self._dep_info("freetype")
        ft_dir = os.path.join(src, "build", "config", "freetype")
        os.makedirs(ft_dir, exist_ok=True)
        save(self, os.path.join(ft_dir, "BUILD.gn"), textwrap.dedent(f"""\
            # Generated by Conan pdfium recipe — routes freetype to Conan package.
            import("//build/config/freetype/freetype.gni")
            config("conan_freetype_config") {{
              include_dirs = [ {self._gn_str_list(ft_info.includedirs)} ]
              lib_dirs = [ {self._gn_str_list(ft_info.libdirs)} ]
              libs = [ {self._gn_libs(ft_info)} ]
            }}
            group("freetype") {{
              public_configs = [ ":conan_freetype_config" ]
              visibility = [ "*" ]
            }}
        """))

    def _build_gn_args(self):
        is_debug = str(self.settings.build_type == "Debug").lower()
        gn_args = [
            f'target_os=\\"{self._gn_os}\\"',
            f'target_cpu=\\"{self._gn_arch}\\"',
            f'is_debug={is_debug}',
            'pdf_is_standalone=true',
            'is_component_build=false',
            'is_official_build=false',
            'pdf_enable_xfa=false',
            'pdf_enable_v8=false',
            'pdf_is_complete_lib=true',
            'treat_warnings_as_errors=false',
            'pdf_use_partition_alloc=false',
            # System dep routing — use Conan packages
            'use_system_zlib=true',
            'use_system_libjpeg=true',
            'use_libjpeg_turbo=false',
            'use_system_libpng=true',
            'use_system_libtiff=true',
            'use_system_libopenjpeg2=true',
            # Freetype from Conan (patched BUILD.gn, not pkg-config)
            'pdf_bundle_freetype=false',
            'use_system_freetype=false',
            # Toolchain
            'use_custom_libcxx=false',
        ]
        if is_msvc(self):
            gn_args.append('is_clang=false')
            # Chromium disables iterator debugging by default even in debug builds.
            # Enable it so _ITERATOR_DEBUG_LEVEL matches Conan-built dependencies.
            if self.settings.build_type == "Debug":
                gn_args.append('enable_iterator_debugging=true')
        if self.settings.os == "Linux":
            gn_args.append('use_sysroot=false')
        if self.options.get_safe("fPIC"):
            gn_args.append('extra_cflags=\\"-fPIC\\"')
        return gn_args

    # ── package() ────────────────────────────────────────────────────────

    def package(self):
        src = self.source_folder
        copy(self, "LICENSE", src, os.path.join(self.package_folder, "licenses"))
        # Public headers
        copy(self, "*.h", os.path.join(src, "public"),
             os.path.join(self.package_folder, "include"))
        # Built libraries
        build_out = os.path.join(src, "out", "Default")
        copy(self, "*.lib", build_out,
             os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", build_out,
             os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["pdfium"]
        self.cpp_info.requires = [
            "zlib::zlib",
            "libjpeg::libjpeg",
            "libpng::libpng",
            "libtiff::libtiff",
            "openjpeg::openjpeg",
            "freetype::freetype",
            "icu::icu",
        ]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = [
                "kernel32", "user32", "gdi32", "advapi32", "winmm", "comdlg32",
            ]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "m", "dl"]
        stdcpp = stdcpp_library(self)
        if stdcpp:
            self.cpp_info.system_libs.append(stdcpp)
