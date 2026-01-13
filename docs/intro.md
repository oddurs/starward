---
id: intro
title: astr0 Documentation
sidebar_label: Home
slug: /
sidebar_position: 1
description: Professional astronomy calculation toolkit for Python with CLI support. Calculate Julian dates, coordinate transformations, sun/moon positions, and planetary ephemeris.
keywords: [astronomy, python, cli, julian date, coordinates, ephemeris]
---

# astr0 Documentation

> *Per aspera ad astra* — Through hardships to the stars

Welcome to the astr0 documentation! astr0 is a professional astronomy calculation toolkit with a focus on transparency and learning.

## Quick Links

| Document | Description |
|----------|-------------|
| [Installation](/getting-started/installation) | How to install astr0 |
| [Quick Start](/getting-started/quickstart) | Get up and running in minutes |
| [CLI Overview](/cli-reference/overview) | Command-line interface reference |
| [Python API](/python-api/overview) | Using astr0 as a Python library |
| [Verbose Mode](/guides/verbose) | See the math behind calculations |

## Features

- **Time Systems** — Julian dates, sidereal time, epoch conversions
- **Coordinates** — ICRS, Galactic, Horizontal transformations
- **Sun & Moon** — Position, rise/set times, phases, twilight
- **Planets** — Mercury through Neptune positions and visibility
- **Verbose Mode** — Show your work with step-by-step calculations
- **Multiple Outputs** — Plain text, JSON, and LaTeX formats

## Philosophy

astr0 is built on these principles:

1. **Precision First** — Every calculation traceable, every assumption explicit
2. **Show Your Work** — Verbose mode reveals the math behind each result
3. **Modular Design** — Each module stands alone, plays well with others
4. **Test Everything** — 500+ tests validated against authoritative sources

## Getting Started

```bash
# Install via pip
pip install astr0

# Check current time in all formats
astr0 time now

# Get planetary positions
astr0 planets all

# Show the math with verbose mode
astr0 sun position --verbose
```

## Version

This documentation is for astr0 **v0.3.0**.
