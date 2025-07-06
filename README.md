[![Lint Status](https://github.com/<OWNER>/<REPO>/actions/workflows/lint.yml/badge.svg)](https://github.com/<OWNER>/<REPO>/actions/workflows/lint.yml)

# prez-pkglog

**prez-pkglog** is a cross-distro package-activity logger that record every install locally and removal event on your
system, then writes an append-only history in both JSON and TOML. This is useful for keeping track of what packages are
installed on your system, and then using that information to make updating your dotfiles easier.

---

## Features

- **Zero-maintenance** - hooks directly into DNF and PackageKit; no polling.
- **Two loggers** - automatically mirrors entries to 'packages.json' and 'packages.toml' files.
- **Modular backends** - bolt on APT, Pacman, Homebrew, etc. with a one-liner.
- **Removal provenance** - entries are never deleted; removals get an '# --REMOVED--' sentinel (TOML) or '
  removed=true' (JSON).

---

## Installation

```bash
# one-time enable (Copr)
sudo dnf copr enable prez/prez-pkglog
sudo dnf install prez-pkglog
```

### Shell wrapper to log every git clone

#### .zshrc

```bash
function pkglog_preexec() {
    [[ $1 == git\ clone* ]] || return
    local repo=${${1#git clone }##*/}
    repo=${repo%.git}
    prez-pkglog install $repo git
}
autoload -Uz add-zsh-hook
add-zsh-hook preexec pkglog_preexec
```

#### .bashrc

```bash
function _pkglog_bash_preexec() {
   [[ $BASH_COMMAND == git\ clone* ]]  || return
   local repo=${BASH_COMMAND#git clone}
   repo=${repo##*/}
   repo=${repo%.git}
   prez-pkglog install "$repo" git
}
```

#### config.fish

```bash
function fish_preexec --on-event fish_preexec
  if string match -rq '^git clone ' -- $argv[1]
    set repo (basename (string replace -r '^git clone +' '' $argv[1]) .git)
    prez-pkglog install $repo git
  end
end
```

---

## Log file examples

### JSON

```json
[
  {
    "name": "neovim",
    "manager": "dnf",
    "date": "2025-06-21T17:02:41-05:00",
    "removed": false
  }
]
```

### TOML

```toml
[[package]]
name = "neovim"
manager = "dnf"
date = "2025-06-21T17:02:41-05:00"
removed = false
```

---

## Building the RPM yourself

```bash
python -m build --sdist
rpmbuild -ts dist/prez-pkglog-0.1.0.tar.gz
mock -r fedora-42-x86_64 ~/rpmbuild/SRPMS/prez-pkglog-0.1.0-1.fc42.src.rpm
sudo dnf install ~/rpmbuild/RPMS/noarch/prez-pkglog-0.1.0-1.fc42.noarch.rpm
```

---

## License

MIT License (see LICENSE)

---

## `prez-pkglog.spec` (key info only)

```specfile
%global
%global

%package
%p
