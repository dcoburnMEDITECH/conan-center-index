"""

Pylint plugin/rules for conanfiles in Conan Center Index

"""

from pylint.lint import PyLinter
from linter.check_package_name import PackageName
from linter.check_import_tools import ImportTools
from linter.check_layout_src_folder import LayoutSrcFolder
from linter.check_version_attribute import VersionAttribute


def register(linter: PyLinter) -> None:
    linter.register_checker(PackageName(linter))
    linter.register_checker(ImportTools(linter))
    linter.register_checker(LayoutSrcFolder(linter))
    linter.register_checker(VersionAttribute(linter))
