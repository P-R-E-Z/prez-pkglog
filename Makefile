PROJECT := prez-pkglog
SPEC	:= prez-pkglog.spec
VERSION	:= $(shell grep '^Version' $(SPEC) | awk '{print $$2}')
RELEASE ?= $(shell grep '^Release' $(SPEC) | awk '{print $$2}')
RPMBUILD_DIR := $(shell rpm --eval '%{_topdir}')
MOCKCFG := fedora-42-x86_64

.PHONY: help lint test build sdist wheel srpm rpm mock install release clean format format-cpp check-format
help:
	@echo "Targets: lint test build sdist wheel srpm rpm mock install release clean format format-cpp check-format"

lint:
	uv run ruff check src/

mypy:
	uv run mypy src/

format-cpp:
	@echo "Formatting C++ code..."
	@if command -v clang-format >/dev/null 2>&1; then \
		clang-format -i libdnf5-plugin/dnf5-plugin/src/*.cpp 2>/dev/null || true; \
		echo "C++ formatting complete."; \
	else \
		echo "clang-format not found. Install with: sudo dnf install clang-tools-extra"; \
		exit 1; \
	fi

format: format-cpp
	@echo "Formatting Python code..."
	uv run black src/
	@echo "All formatting complete."

check-format:
	@echo "Checking C++ formatting..."
	@if command -v clang-format >/dev/null 2>&1; then \
		if clang-format --dry-run --Werror libdnf5-plugin/dnf5-plugin/src/*.cpp 2>/dev/null; then \
			echo "C++ formatting is correct."; \
		else \
			echo "C++ formatting issues found. Run 'make format-cpp' to fix."; \
			exit 1; \
		fi; \
	else \
		echo "clang-format not found. Install with: sudo dnf install clang-tools-extra"; \
		exit 1; \
	fi
	@echo "Checking Python formatting..."
	@uv run black --check src/ || (echo "Python formatting issues found. Run 'make format' to fix." && exit 1)
	@echo "All formatting checks passed."

test:
	uv run pytest -q

build: sdist wheel

sdist:
	uv run python -m build --sdist

wheel:
	uv run python -m build --wheel

srpm: sdist
	mkdir -p $(RPMBUILD_DIR)/SOURCES
	# The sdist produced by Python build uses an underscore in the archive name
	# (e.g. prez_pkglog-0.6.1.tar.gz) while the RPM spec expects a hyphen
	# (prez-pkglog-0.6.1.tar.gz). Copy and rename accordingly so rpmbuild finds it.
	cp dist/$(subst -,_,${PROJECT})-${VERSION}.tar.gz \
	  $(RPMBUILD_DIR)/SOURCES/$(PROJECT)-$(VERSION).tar.gz
	rpmbuild -bs $(SPEC)

rpm: srpm
	rpmbuild -bb $(SPEC)

mock: srpm
	mock -r $(MOCKCFG) $(RPMBUILD_DIR)/SRPMS/$(PROJECT)-$(VERSION)-$(RELEASE).src.rpm

install: rpm
	sudo dnf install -y $(RPMBUILD_DIR)/RPMS/x86_64/$(PROJECT)-$(VERSION)-*.x86_64.rpm

release:
	@test "$(v)" || (echo "usage: make release v=patch|minor|major" && exit 1)
	uv run bump2version $(v)
	# Update the .spec file version to match pyproject.toml
	$(eval NEW_VERSION := $(shell grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'))
	sed -i 's/^Version: .*/Version: $(NEW_VERSION)/' $(SPEC)
	git add -A
	git commit -m "Bump version to $(NEW_VERSION)"

clean:
	rm -rf build dist *.egg-info
	find . -name '__pycache__' -exec rm -rf {} +
	rm -f $(RPMBUILD_DIR)/SRPMS/$(PROJECT)*.src.rpm
	rm -f $(RPMBUILD_DIR)/RPMS/x86_64/$(PROJECT)*.x86_64.rpm
	rm -f $(RPMBUILD_DIR)/SOURCES/$(PROJECT)*.tar.gz
