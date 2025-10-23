# Usage instructions

## Requirements

- Tested under __Ubuntu 22.04.4 LTS__
- Tested with __Python 3.10.12__
- For the python packages, see `docs/requirements.txt`

## Build the documentation

1. Install the required packages:

    ```bash
    pip install -r docs/requirements.txt
    ```

1. Install the package to be documented:

    ```bash
    pip install demopkg/
    ```

1. Build the documentation:

    ```bash
    cd docs
    make html
    ```

1. Look at the documentation:

    ```bash
    cd docs
    firefox build/html/index.html
    ```

## Clean build artifacts

In case you want to clean the documentation, you can run:

```bash
cd docs
rm -r source/API
make clean
```

## Adopt to your Python project

1. Add the necessary python packages to this repository. You can do this analogous to the `demopkg` package.
1. Make sure they are importable by either installing them or adopting your `PYTHONPATH`.
1. Replace the `demopkg` entry in the `docs/source/api.rst` with the package you want to document (or multiple packages).


## Adopt to your C++ project
1. Install `doxygen`:
```bash
sudo apt install doxygen
```

2. Copy and paste the `docs` folder of this repo into the root of your C++ repo.
3. Copy and paste the `.gitignore` file in this repo into the `.gitignore` in your C++ repo.
4. Add `breathe` and `exhale` to `docs/requirements.txt` (and install locally):
```
sphinx==7.1.2
sphinx-rtd-theme==1.3.0rc1
breathe==4.35.0
exhale==0.3.7
```

5. Create a Doxygen config file in `docs/source`:
``` bash
doxygen -g Doxyfile.in
```

6. Change the following fields in `docs/source/Doxyfile.in`:
```
GENERATE_XML = YES
INPUT = ../../include/<YOUR LIBRARY NAME>
OUTPUT_DIR = ../build/doxygen
RECURSIVE = YES
PROJECT_NAME = <YOUR PROJECT NAME>
```
7. Delete `docs/source/api.rst`.
8. Modify `docs/source/conf.py` with the following:

a. First, add the import:
```python
from cgitb import html
```
b. Second, change the project name:
```python
project = '<YOUR_PROJECT_NAME>'
```
c. Third, add the config for breathe and exhale:
```python
# Breathe/exhale configuration
breathe_projects = {"<BREATHE_PROJECT_NAME>":"../build/doxygen/xml"}
breathe_default_project = "<BREATHE_PROJECT_NAME>"
exhale_args = {
        "containmentFolder"    : "./API",
        "rootFileName"         : "api.rst",
        "rootFileTitle"        : "API",
        "doxygenStripFromPath" : "..",
        "createTreeView": True
    }
# Tell sphinx what the primary language being documented is.
primary_domain = 'cpp'
# Tell sphinx what the pygments highlight language should be.
highlight_language = 'cpp' 
```
d. Finally, add `breathe` and `exhale` to the sphinx extensions:
```python
extensions = [
    'sphinx.ext.autosummary',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'breathe',
    'exhale'
]
```
9. In `docs/source/index.rst`, replace the `api` line to `API/api`.
10. Replace `docs/Makefile` with:
```make
# Minimal makefile for Sphinx documentation
#
# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
CURRENTDIR    = `pwd`
# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
.PHONY: help Makefile
# For clean, just run the same command as catch all but don't run doxygen
clean: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	rm -r $(SOURCEDIR)/API
	rm -r $(BUILDDIR)
# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
# Before running sphinx, run doxygen for C++ code
%: Makefile
	mkdir -p $(BUILDDIR)
	cd $(SOURCEDIR); doxygen Doxyfile.in
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
```