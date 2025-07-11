PROJECT := prez-pkglog
SPEC	:= prez-pkglog.spec
VERSION	:= $(shell grep '^Version' $(SPEC) | awk '{print $$2}')
RELEASE ?= $(shell grep '^Release' $(SPEC) | awk '{print $$2}')
RPMBUILD_DIR := $(shell rpm --eval '%{_topdir}')
MOCKCFG := fedora-42-x86_64

.PHONY: help lint test build sdist wheel srpm rpm mock install release clean
help:
	@echo "Targets: lint test build sdist wheel srpm rpm mock install release clean"

lint:
	uv run ruff check src/

mypy:
	uv run mypy src/

test:
	uv run pytest -q

build: sdist wheel

sdist:
	uv run python -m build --sdist

wheel:
	uv run python -m build --wheel

srpm: sdist
	mkdir -p $(RPMBUILD_DIR)/SOURCES
	cp dist/$(subst -,_,${PROJECT})-${VERSION}.tar.gz $(RPMBUILD_DIR)/SOURCES/
	rpmbuild -bs $(SPEC)

rpm: srpm
	rpmbuild -bb $(SPEC)

mock: srpm
	mock -r $(MOCKCFG) $(RPMBUILD_DIR)/SRPMS/$(PROJECT)-$(VERSION)-$(RELEASE).src.rpm

install: rpm
	sudo dnf install -y $(RPMBUILD_DIR)/RPMS/noarch/$(PROJECT)-$(VERSION)-$(RELEASE).noarch.rpm

release:
	@test "$(v)" || (echo "usage: make release v=patch|minor|major" && exit 1)
	uv run bump2version $(v)
	git push && git push --tags

clean:
	rm -rf build dist *.egg-info
	find . -name '__pycache__' -exec rm -rf {} +
	rm -f $(RPMBUILD_DIR)/SRPMS/$(PROJECT)*.src.rpm
	rm -f $(RPMBUILD_DIR)/RPMS/noarch/$(PROJECT)*.noarch.rpm
	rm -f $(RPMBUILD_DIR)/SOURCES/$(PROJECT)*.tar.gz
