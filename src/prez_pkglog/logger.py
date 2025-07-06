# prez-pkglog - light cross-distro package logger engine
import datetime as dt
import json
import pathlib
import sys

try:
    import toml
except ImportError:
    toml = None

DATA_DIR = pathlib.Path.home() / ".local/share/prez-pkglog"
JSON_FILE = DATA_DIR / "packages.json"
TOML_FILE = DATA_DIR / "packages.toml"


def _now():
    return dt.datetime.now().isoformat(timespec="seconds")


def _ensure():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not JSON_FILE.exists():
        JSON_FILE.write_text("[]")
    if not TOML_FILE.exists():
        TOML_FILE.write_text("")


def _load():
    return json.loads(JSON_FILE.read_text())


def _save(entries):
    JSON_FILE.write_text(json.dumps(entries, indent=2))


def _append_toml(entry, removed=False):
    if toml is None:
        return
    with TOML_FILE.open("a") as f:
        if removed:
            f.write("# --REMOVED--\n")
        f.write(toml.dumps({"package": entry}))
        f.write("\n")


def record(action, name, manager):
    _ensure()
    entries = _load()
    entry = {
        "name": name,
        "manager": manager,
        "date": _now(),
        "removed": action == "remove",
    }
    entries.append(entry)
    _save(entries)
    _append_toml(entry, removed=entry["removed"])


def main():
    if len(sys.argv) != 4:
        print("Usage: prez-pkglog <install|remove> <name> <manager>")
        sys.exit(1)
    _, action, name, manager = sys.argv
    record(action, name, manager)


if __name__ == "__main__":
    main()
