---
id: installation
title: Installation
sidebar_label: Installation
sidebar_position: 1
description: Install astr0 astronomy toolkit via pip or from source. Requires Python 3.9+.
---

# Installation

## Requirements

- Python 3.9 or higher
- No compiled dependencies (pure Python)

## Install from PyPI

```bash
pip install astr0
```

## Install from Source

```bash
git clone https://github.com/oddurs/astr0.git
cd astr0
pip install -e .
```

## Development Install

For development with all test dependencies:

```bash
pip install -e ".[dev]"
```

## Verify Installation

```bash
astr0 --version
# astr0, version 0.2.1

astr0 time now
```

## Dependencies

astr0 has minimal dependencies:

| Package | Purpose |
|---------|---------|
| click | CLI framework |
| rich | Terminal formatting |

Development dependencies include pytest, hypothesis, mypy, and ruff.
