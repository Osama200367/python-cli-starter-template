# CLIStart — Python CLI Starter Template

A small, **beginner-friendly** starting point for building command-line tools
in Python. It comes wired up with the things every real project needs but that
are tedious to set up from scratch:

- 📁 A clean, conventional **project layout** (`src/` + `tests/`)
- ⚙️ **Layered configuration** — CLI flags > environment variables > config file > defaults
- 📝 **Logging** you can turn up (`-v`) or down (`-q`) without touching code
- ✅ **Example tests** with `pytest` (covering the logic, the config, and the CLI)
- 🎨 **Linting & formatting** with `ruff`
- 🤖 **Continuous integration** via GitHub Actions (runs on Python 3.11–3.13)

The code is written to be *read*: comments explain **why** things are done a
certain way, so you can learn from the template as well as build on it.

---

## Quickstart

You need **Python 3.11 or newer** (the config loader uses the standard-library
`tomllib`, added in 3.11).

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install the project (editable) with its dev tools
pip install -e ".[dev]"

# 3. Run it!
clistart --help
clistart greet --name Ada
clistart process "hello world"   # -> HELLO WORLD  (default transform)
```

### Try the features

```bash
# The richer example: transform text, mode driven by config/flags/env.
clistart process "hello world" --transform reverse   # -> dlrow olleh
clistart process "hello world" --transform title     # -> Hello World

# Turn logging up to see what's happening under the hood:
clistart -v process "hello world"

# Configure via environment variable (note the CLISTART_ prefix):
CLISTART_TRANSFORM=lower clistart process "HELLO"    # -> hello

# Or via a config file:
cp config.example.toml config.toml                   # then edit config.toml
clistart process "hello world"                       # uses config.toml's value
```

### Run the tests and linter

```bash
pytest                # run the test suite
ruff check .          # lint
ruff format .         # auto-format your code
```

---

## Folder structure

```
python-cli-starter-template/
├── pyproject.toml          # Project metadata, dependencies, tool config (all here)
├── README.md               # This file
├── LICENSE                 # MIT — do whatever you like with it
├── .gitignore
├── config.example.toml     # Copy to config.toml and edit to customize
├── .github/
│   └── workflows/
│       └── ci.yml          # Runs ruff + pytest automatically on GitHub
├── src/
│   └── clistart/           # The importable package (rename this for your project)
│       ├── __init__.py     # Holds the version number
│       ├── cli.py          # The Typer CLI: commands, options, help text
│       ├── config.py       # Settings dataclass + the layered config loader
│       ├── logging_setup.py# One-call logging configuration
│       └── core.py         # The actual logic — kept independent of the CLI
└── tests/
    ├── conftest.py         # Shared test fixtures
    ├── test_core.py        # Tests the logic directly
    ├── test_config.py      # Tests the config precedence rules
    └── test_cli.py         # Tests the commands end-to-end
```

### Why is the code split up like this?

The single most important idea in this template is that **`core.py` (what the
program does) is separate from `cli.py` (how the user invokes it).** Because the
logic doesn't depend on Typer, you can:

- test it directly, with plain function calls (see `test_core.py`), and
- reuse it later from a web app, a scheduled job, or a notebook.

The config loader in `config.py` is the other reusable centerpiece. It merges
four sources in a fixed order so behaviour is predictable:

> **CLI flags** beat **environment variables** (`CLISTART_*`) beat the **config
> file** beat the **built-in defaults**.

---

## Using this as a base for your own project

1. **Rename the package.** Change `src/clistart/` to `src/yourname/`, and update
   the references in `pyproject.toml` (`[project.scripts]` and the import paths)
   and in the `tests/`.
2. **Rename the command.** In `pyproject.toml`, the line
   `clistart = "clistart.cli:app"` under `[project.scripts]` controls your
   terminal command name.
3. **Edit the metadata.** Update `name`, `description`, `authors`, and the
   `LICENSE` copyright line.
4. **Replace the example logic.** Swap the transforms in `core.py` and the
   commands in `cli.py` for whatever your tool actually does. Keep the config
   and logging wiring — that's the part you don't want to rebuild each time.
5. **Add your settings.** Add fields to the `Settings` dataclass in `config.py`;
   they automatically pick up file, env-var, and default support. (The env-var
   prefix and config-table name live in `config.py` as `ENV_PREFIX` and the
   `[clistart]` table — rename those to match your project.)

---

## License

Released under the [MIT License](LICENSE).
