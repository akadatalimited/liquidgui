PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
SYSTEMD_DIR ?= /etc/systemd/system
INIT_DIR ?= /etc/init.d

SCRIPT = liquidgui
SYSTEMD_SERVICE = etc/systemd/system/liquidgui.service
INIT_SCRIPT = etc/init.d/liquidgui

.PHONY: all install uninstall test clean

all: test

install:
	install -Dm755 $(SCRIPT) $(DESTDIR)$(BINDIR)/$(SCRIPT)
	install -Dm644 $(SYSTEMD_SERVICE) $(DESTDIR)$(SYSTEMD_DIR)/liquidgui.service
	install -Dm755 $(INIT_SCRIPT) $(DESTDIR)$(INIT_DIR)/liquidgui

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/$(SCRIPT)
	rm -f $(DESTDIR)$(SYSTEMD_DIR)/liquidgui.service
	rm -f $(DESTDIR)$(INIT_DIR)/liquidgui

PYTHON ?= python3

test:
	$(PYTHON) -m py_compile $(SCRIPT)

clean:
	rm -rf __pycache__
	find . -name "*.pyc" -delete
