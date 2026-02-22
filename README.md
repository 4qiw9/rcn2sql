# rcn2sql

Convert RCN `.gml` files to SQLite database.

## Download

Pre-built binaries available on [Releases](https://github.com/your-username/rcn2sql/releases):
- `rcn2sql-linux-amd64` - Linux
- `rcn2sql-macos-amd64` - macOS  
- `rcn2sql-windows-amd64.exe` - Windows

## Requirements

- Python 3.10+
- No external dependencies (stdlib only)

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
```

```bash
python cli.py pipeline --gml rcn.gml --db rcn.sqlite
```

## Project structure

```
rcn2sql/
├── cli.py               # main entry point
├── src/
│   ├── load_rcn.py      # load GML -> raw tables
│   ├── build_wide.py    # build wide table
│   ├── logging_config.py
│   ├── utils.py
│   └── parsers/         # parsers per feature type
├── tests/               # pytest tests
├── log/
├── rcn_struct_desc.md   # GML structure and DB schema
└── README.md
```

## CLI

### pipeline

Full pipeline: parse + build-wide.

```bash
python cli.py pipeline --gml <file.gml> --db <database.sqlite>
```

### parse

Parse GML file(s) into raw tables. Supports glob patterns.

```bash
python cli.py parse --gml <file.gml> --db <database.sqlite>
```

```bash
python cli.py parse --gml "data/*.gml" --db <database.sqlite>
```


### build-wide

Build wide table from raw tables.

```bash
python cli.py build-wide --db <database.sqlite> --drop
```

### imports

Show import history.

```bash
python cli.py imports --db <database.sqlite>
```

## Options

| Argument | Default | Description |
| --- | --- | --- |
| `--gml` | - | Path to GML file(s), supports glob patterns (e.g., `"data/*.gml"`) |
| `--db` | `rcn_raw.sqlite` | Path to SQLite database |
| `--table` | `rcn_wide` | Wide table name |
| `--batch` | `100000` | Batch size for inserts |
| `--log-every` | `500000` | Log progress every N records |
| `--limit` | - | Limit rows (for testing) |
| `--force` | - | Force re-import even if file was already imported |
| `--drop` | - | Drop table before creating |

## Testing

```bash
pip install -r requirements.txt
```

```bash
pytest tests/
```

## Documentation

[rcn_struct_desc.md](rcn_struct_desc.md)

