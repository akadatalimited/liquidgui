PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
UDEV_DIR ?= /etc/udev/rules.d
DIST_DIR ?= dist
INSTALL_USER ?= $(USER)
ACCESS_GROUP ?= plugdev

SCRIPT = liquidgui
MODULES = monitor.py
UDEV_RULE = etc/udev/rules.d/60-liquidctl.rules
BINARY_PATH = $(DIST_DIR)/liquidgui

PYINSTALLER ?= $(PYTHON) -m PyInstaller

.PHONY: all install install-source install-binary uninstall uninstall-source uninstall-binary uninstall-udev udev-install user-install permissions-install test clean binary help

help:
	@printf '%s\n' \
	'Available targets:' \
	'  make help               Show this help text' \
	'  make test               Run Python syntax checks' \
	'  make binary             Build the standalone binary with PyInstaller' \
	'  make install            Install dist/liquidgui if it exists, otherwise install the source launcher' \
	'  make install-source     Install the source launcher and Python module files' \
	'  make install-binary     Build and install the standalone binary' \
	'  make permissions-install Install udev rule and add the user to the access group' \
	'  make uninstall          Remove installed launcher, binary, and module files' \
	'  make uninstall-udev     Remove the installed udev rule' \
	'  make clean              Remove build artifacts'

# Default target runs basic checks; the standalone binary is optional
all: test

install:
	@if [ -f "$(BINARY_PATH)" ]; then \
		$(MAKE) install-binary; \
	else \
		$(MAKE) install-source; \
	fi

install-source:
	install -Dm755 $(SCRIPT) $(DESTDIR)$(BINDIR)/$(SCRIPT)
	for m in $(MODULES); do install -Dm644 $$m $(DESTDIR)$(BINDIR)/$$m; done

install-binary:
	@test -f $(BINARY_PATH) || { printf 'Built binary not found at %s\nRun make binary first.\n' "$(BINARY_PATH)"; exit 1; }
	install -Dm755 $(BINARY_PATH) $(DESTDIR)$(BINDIR)/liquidgui

udev-install:
	install -Dm644 $(UDEV_RULE) $(DESTDIR)$(UDEV_DIR)/60-liquidctl.rules

user-install:
	sudo groupadd -f $(ACCESS_GROUP)
	sudo usermod -aG $(ACCESS_GROUP) $(INSTALL_USER)
	@printf 'Added %s to %s. Log out and back in for the new group to apply.\n' "$(INSTALL_USER)" "$(ACCESS_GROUP)"

permissions-install: udev-install user-install

uninstall: uninstall-source uninstall-binary

uninstall-source:
	rm -f $(DESTDIR)$(BINDIR)/$(SCRIPT)
	for m in $(MODULES); do rm -f $(DESTDIR)$(BINDIR)/$$m; done

uninstall-binary:
	rm -f $(DESTDIR)$(BINDIR)/liquidgui

uninstall-udev:
	rm -f $(DESTDIR)$(UDEV_DIR)/60-liquidctl.rules

PYTHON ?= python3

test:
	$(PYTHON) -m py_compile $(SCRIPT) $(MODULES)

binary: test
	$(PYINSTALLER) --onefile $(SCRIPT)

clean:
	rm -rf __pycache__ build dist
	find . -name "*.pyc" -delete
