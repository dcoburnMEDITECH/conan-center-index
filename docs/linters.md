# ConanCenterIndex Linters

Some linter configuration files are available in the folder [linter](../linter), which are executed by Github Actions
and are displayed during [code review](https://github.com/features/code-review) as annotations, to improve recipe quality.
They consume python scripts which are executed to fit CCI rules. Those scripts use [astroid](https://github.com/PyCQA/astroid)
and [pylint](https://pylint.pycqa.org/en/latest/) classes to parse Conan recipe files and manage their warnings and errors.

Pylint by itself is not able to find ConanCenterIndex rules, so astroid is used to iterate over a conanfile's content and
validate CCI requirements. Pylint uses an [rcfile](https://pylint.pycqa.org/en/latest/user_guide/configuration/index.html)
to configure plugins, warnings and errors which should be enabled or disabled.

<!-- toc -->
## Contents

  * [Understanding the different linters](#understanding-the-different-linters)
  * [Running the linters locally](#running-the-linters-locally)
  * [Pylint configuration files](#pylint-configuration-files)
  * [Linter Warning and Errors](#linter-warning-and-errors)
    * [E9005 - conan-missing-name: Every conan recipe must contain the attribute name](#e9005---conan-missing-name-every-conan-recipe-must-contain-the-attribute-name)
    * [E9007 - conan-test-no-name: Do not add name attribute in test package recipes](#e9007---conan-test-no-name-do-not-add-name-attribute-in-test-package-recipes)
    * [E9011 - conan-import-tools: Importing conan.tools or conan.tools.xxx.zzz.yyy should be considered as private](#e9011---conan-import-tools-importing-conantools-or-conantoolsxxxzzzyyy-should-be-considered-as-private)
    * [E9012 - conan-attr-version: Recipe should not contain version attribute](#e9012---conan-attr-version-recipe-should-not-contain-version-attribute)<!-- endToc -->

## Understanding the different linters

There's a three classes of linters currently in place for ConanCenterIndex

- ConanCenter Hook - these are responsible for validating the structure of the recipes and packages.
- Pylint Linter - these are used to ensure the code quality and conventions of a recipes (i.e `conanfile.py`)
- Yaml Checks - stylistic guidance and schema validation check for support files and best practices

## Running the linters locally

Check the [Developing Recipes](developing_recipes_locally.md) for more information on each of the three linters.

## Pylint configuration files

- [Pylint Recipe](../linter/pylintrc_recipe): This `rcfile` lists plugins and rules to be executed over all recipes (not test package) and validate them.
- [Pylint Test Package Recipe](../linter/pylintrc_testpackage): This `rcfile` lists plugins and rules to be executed over all recipes in test package folders only:

## Linter Warning and Errors

Here is the list of current warning and errors provided by pylint, when using CCI configuration.

### E9005 - conan-missing-name: Every conan recipe must contain the attribute name

The attribute `name` is always expected. On the other hand, `version` should not be listed.

```python
def BazConanfile(ConanFile):
    name = "baz"
```

### E9007 - conan-test-no-name: Do not add name attribute in test package recipes

The test package is not a recipe, thus, it should not have a name

```python
def TestPackageConanFile(ConanFile):
    name = "test_package" # Wrong!
```

### E9011 - conan-import-tools: Importing conan.tools or conan.tools.xxx.zzz.yyy should be considered as private

Documented on [conanfile.tools](https://docs.conan.io/1/reference/conanfile/tools.html):
It's not allowed to use `tools.xxx` directly:

```python
from conan import tools
...

tools.scm.Version(self.version)
```

Neither sub modules:

```python
from conan.tools.apple.apple import is_apple_os
```

Only modules under `conan.tools` and `conan.tools.xxx` are allowed:

```python
from conan.tools.files import rmdir
from conan.tools import scm
```

### E9012 - conan-attr-version: Recipe should not contain version attribute

All recipes on CCI should be generic enough to support as many versions as possible, so enforcing a specific
version as attribute will not allow to re-use the same recipe for multiple release versions.

```python
from conan import ConanFile

class FooConanFile(ConanFile):
    version = "1.0.0"  # Wrong!
```

The package version should be passed as command argument, e.g:

    conan create all/ 1.0.0@ -pr:h=default -pr:b=default

Or, if you are running Conan 2.0:

    conan create all/ --version=1.0.0 -pr:h=default -pr:b=default

The only exception is when providing ``system`` packages, which are allowed.

```python
from conan import ConanFile

class FooConanFile(ConanFile):
    version = "system"  # Okay!
```
