PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
SYSTEMD_DIR ?= /etc/systemd/system
INIT_DIR ?= /etc/init.d
UDEV_DIR ?= /etc/udev/rules.d

SCRIPT = liquidgui
MODULE = curves.py
SYSTEMD_SERVICE = etc/systemd/system/liquidgui.service
INIT_SCRIPT = etc/init.d/liquidgui
UDEV_RULE = etc/udev/rules.d/60-liquidctl.rules

PYINSTALLER ?= $(PYTHON) -m PyInstaller

.PHONY: all install uninstall test clean binary

all: test binary

install:
	install -Dm755 $(SCRIPT) $(DESTDIR)$(BINDIR)/$(SCRIPT)
	install -Dm644 $(MODULE) $(DESTDIR)$(BINDIR)/$(MODULE)
	install -Dm644 $(SYSTEMD_SERVICE) $(DESTDIR)$(SYSTEMD_DIR)/liquidgui.service
	install -Dm755 $(INIT_SCRIPT) $(DESTDIR)$(INIT_DIR)/liquidgui
	install -Dm644 $(UDEV_RULE) $(DESTDIR)$(UDEV_DIR)/60-liquidctl.rules

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/$(SCRIPT)
	rm -f $(DESTDIR)$(BINDIR)/$(MODULE)
	rm -f $(DESTDIR)$(SYSTEMD_DIR)/liquidgui.service
	rm -f $(DESTDIR)$(INIT_DIR)/liquidgui
	rm -f $(DESTDIR)$(UDEV_DIR)/60-liquidctl.rules

PYTHON ?= python3

test:
	$(PYTHON) -m py_compile $(SCRIPT) $(MODULE)

binary:
	$(PYINSTALLER) --onefile $(SCRIPT)

clean:
	rm -rf __pycache__ build dist
	find . -name "*.pyc" -delete
