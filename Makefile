PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
UDEV_DIR ?= /etc/udev/rules.d

SCRIPT = liquidgui
MODULES = monitor.py
UDEV_RULE = etc/udev/rules.d/60-liquidctl.rules

PYINSTALLER ?= $(PYTHON) -m PyInstaller

.PHONY: all install uninstall test clean binary

# Default target runs basic checks; the standalone binary is optional
all: test

install:
	install -Dm755 $(SCRIPT) $(DESTDIR)$(BINDIR)/$(SCRIPT)
	for m in $(MODULES); do install -Dm644 $$m $(DESTDIR)$(BINDIR)/$$m; done
	install -Dm644 $(UDEV_RULE) $(DESTDIR)$(UDEV_DIR)/60-liquidctl.rules

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/$(SCRIPT)
	for m in $(MODULES); do rm -f $(DESTDIR)$(BINDIR)/$$m; done
	rm -f $(DESTDIR)$(UDEV_DIR)/60-liquidctl.rules

PYTHON ?= python3

test:
	$(PYTHON) -m py_compile $(SCRIPT) $(MODULES)

binary:
	$(PYINSTALLER) --onefile $(SCRIPT)

clean:
	rm -rf __pycache__ build dist
	find . -name "*.pyc" -delete
