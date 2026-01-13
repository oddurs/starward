---
id: overview
title: CLI Overview
sidebar_label: Overview
sidebar_position: 1
description: Command-line interface for astronomical calculations. Time conversions, coordinates, sun/moon positions, and planetary ephemeris.
---

# CLI Overview

astr0 provides a comprehensive command-line interface for astronomical calculations.

## Global Options

| Option | Description |
|--------|-------------|
| `--verbose`, `-v` | Show calculation steps |
| `--json` | Output in JSON format |
| `--output`, `-o` | Output format: `plain`, `json`, `latex` |
| `--precision`, `-p` | Precision level (see below) |
| `--version` | Show version |
| `--help` | Show help |

## Precision Levels

| Level | Decimals | Use Case |
|-------|----------|----------|
| `compact` | 2 | Quick reference |
| `display` | 4 | Readable output |
| `standard` | 6 | Default |
| `high` | 10 | Research |
| `full` | 15 | Maximum precision |

```bash
astr0 --precision high sun position
```

## Command Groups

| Group | Alias | Description |
|-------|-------|-------------|
| `time` | `t` | Time conversions |
| `coords` | `c` | Coordinate transformations |
| `angles` | `a` | Angular calculations |
| `sun` | `s` | Solar position and events |
| `moon` | `m` | Lunar position and phases |
| `planets` | `p` | Planetary positions |
| `observer` | `o` | Observer management |
| `vis` | `v` | Visibility calculations |
| `constants` | `const` | Astronomical constants |

## Examples

```bash
# Using aliases
astr0 t now          # time now
astr0 p all          # planets all
astr0 s rise         # sun rise

# Combining options
astr0 -v --json planets position mars

# Pipeline to jq
astr0 planets all --json | jq '.planets.jupiter'
```

## Detailed References

- [Time Commands](/cli-reference/time)
- [Coordinate Commands](/cli-reference/coords)
- [Sun & Moon](/cli-reference/sun-moon)
- [Planets](/cli-reference/planets)
