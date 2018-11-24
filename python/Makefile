PY_MODULES = \
	argparse2bco \
	argparse2man \
	os_path_utils

PY_EXECUTABLES = \
	proman

PROCFGS = $(wildcard *.procfg)
#------------------------------------------------------------------------------#
USER_PYMODDIR = $(shell python -m site --user-site)
USER_PROCFGDIR= $(HOME)/.config/procfg
USER_BINDIR = $(HOME)/bin

none:

all: user_install

user_install: \
	user_install_py_modules \
	user_install_py_executables \
	user_install_procfgs

user_install_py_modules: \
	$(addsuffix .py, $(addprefix $(USER_PYMODDIR)/, $(PY_MODULES)))

user_install_py_executables: \
	$(addprefix $(USER_BINDIR)/, $(PY_EXECUTABLES))

user_install_procfgs: \
	$(addprefix $(USER_PROCFGDIR)/, $(PROCFGS))


$(USER_PYMODDIR)/%.py: %.py | $(USER_PYMODDIR)
	cp $< $@

$(USER_BINDIR)/%: %.py | $(USER_BINDIR)
	cp $< $@
	chmod u+x $@

$(USER_PROCFGDIR)/%.procfg: %.procfg | $(USER_PROCFGDIR)
	cp $< $@

$(USER_PYMODDIR) $(USER_BINDIR) $(USER_PROCFGDIR):
	mkdir -p $@
