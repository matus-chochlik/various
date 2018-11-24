USER_PYMODDIR = $(shell python -m site --user-site)
USER_BINDIR = $(HOME)/bin

none:

all: user_install

user_install: \
	user_install_relfs_pymods \
	user_install_relfs_exes

user_install_relfs_pymods: \
	$(addprefix $(USER_PYMODDIR)/, $(wildcard relfs/*.py))

user_install_relfs_exes: \
	$(addprefix $(USER_BINDIR)/, $(patsubst %.py,%,$(wildcard relfs-*.py)))

$(USER_PYMODDIR)/relfs/%.py: relfs/%.py | $(USER_PYMODDIR)/relfs
	cp $< $@

$(USER_BINDIR)/relfs-%: relfs-%.py | $(USER_BINDIR)
	cp $< $@

$(USER_BINDIR) $(USER_PYMODDIR)/relfs:
	mkdir -p $@
