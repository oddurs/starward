---
slug: allure-reporting
title: "starward v0.4.1: Test Reporting & Developer Docs"
authors: [oddur]
tags: [release, testing, documentation]
---

starward v0.4.1 brings comprehensive Allure test reporting and expanded developer documentation. With 872 tests now annotated with educational commentary, the test suite itself becomes a learning resource.

<!-- truncate -->

## Allure Test Reporting

Every test in starward is now annotated with [Allure](https://docs.qameta.io/allure/) decorators, producing rich, interactive test reports.

### Generate a Report

```bash
# Run tests with Allure results
pytest --clean-alluredir

# Generate and view the report
allure serve allure-results

# Or use the Makefile
make report
```

### What You'll See

The Allure report provides:

- **Test hierarchy**: Epic → Feature → Story → Test
- **Step-by-step execution**: Each assertion shown in context
- **Educational descriptions**: Astronomical concepts explained
- **Attachments**: Computed values and intermediate results
- **Trends**: History across test runs

### Example Test

```python
@allure.story("Airmass")
class TestAirmass:
    """
    Tests for airmass calculations.

    Airmass quantifies atmospheric path length:
    - Zenith (90°): X = 1.0
    - 45° altitude: X ≈ 1.41 (√2)
    - 30° altitude: X ≈ 2.0 (observation limit)
    """

    @pytest.mark.golden
    @allure.title("Zenith airmass = 1.0")
    def test_zenith_airmass(self):
        """At zenith, light travels minimum atmosphere."""
        with allure.step("Set altitude to zenith (90°)"):
            alt = Angle(degrees=90)

        with allure.step("Calculate airmass"):
            X = airmass(alt)

        with allure.step(f"Verify X = {X:.3f}"):
            assert X == pytest.approx(1.0)
```

## Test Suite Statistics

| Category | Tests | Coverage |
|----------|-------|----------|
| Core calculations | 168 | 97% |
| Celestial bodies | 91 | 93% |
| Catalogs | 220 | 95% |
| Visibility | 138 | 94% |
| CLI | 44 | 88% |
| **Total** | **872** | **94%** |

## Developer Documentation

A new [Development](/docs/development/overview) section joins the documentation:

### Testing Guide

Complete documentation of the test infrastructure:

- Test markers (`@pytest.mark.golden`, `@pytest.mark.edge`)
- Fixture library (observers, coordinates, reference times)
- Allure annotations and best practices
- Coverage reporting

### Contributing Guide

Expanded contribution guidelines:

- Development environment setup
- Code style and standards
- Writing tests with educational value
- Pull request process

### Cheatsheet

Quick reference for CLI and Python API:

```python
# Time
jd = jd_now()
jd = JulianDate(2451545.0)

# Coordinates
coord = ICRSCoord.parse("05h 34m 32s", "+22d 00m 52s")
galactic = coord.to_galactic()

# Sun/Moon
pos = sun_position(jd)
phase = moon_phase(jd)

# Visibility
alt = target_altitude(coord, observer, jd)
X = airmass(alt)
```

### Dependencies

Documentation of runtime and development dependencies, explaining why starward avoids external astronomy libraries in favor of first-principles implementations.

## Makefile

A new Makefile simplifies common tasks:

```bash
make test      # Run pytest with Allure
make report    # Generate and serve Allure report
make clean     # Clean build artifacts
make lint      # Run ruff and mypy
```

## Getting Started

```bash
pip install --upgrade starward

# For development
pip install -e ".[dev]"
make report
```

Explore the [Testing Guide](/docs/development/testing) for full documentation.
