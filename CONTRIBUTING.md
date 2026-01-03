

# Contributing to astr0

> *“Per aspera ad astra” — Through hardships to the stars*

Thank you for your interest in making astr0 better! We welcome contributions from everyone—whether you’re fixing a typo, adding a feature, or improving documentation.

---

## 🚀 How to Contribute

1. **Fork** the repository and create a new branch from `master` for your work.
2. **Set up your environment**:
   - Install dependencies: `pipenv install` or see [docs/getting-started.md](docs/getting-started.md)
3. **Develop** your changes:
   - Write clear, well-documented, and tested code
   - Add or update documentation as needed
4. **Test** your changes:
   - Run all tests: `pipenv run pytest` or `./run_tests.py`
   - Use test markers (`slow`, `golden`, `edge`, etc.) as appropriate
5. **Submit a Pull Request (PR)**:
   - Provide a concise description and rationale
   - Reference related issues if applicable

---

## 🧑‍💻 Code Style & Standards

- Follow [PEP8](https://peps.python.org/pep-0008/) and use type annotations where possible
- Write docstrings for all public modules, classes, and functions
- Use clear, descriptive commit messages
- Prefer small, focused PRs over large, sweeping changes

See the [project philosophy](README.md#philosophy) for guiding principles.

---

## 🧪 Testing

- All new code must include relevant tests
- Use [pytest](https://docs.pytest.org/) and the provided configuration
- Mark tests with `@pytest.mark.slow`, `@pytest.mark.golden`, etc. as appropriate
- Aim for high coverage and test edge cases

Test suite structure:

```
tests/
├── conftest.py         # Shared fixtures and markers
├── core/               # Core module tests
├── cli/                # CLI integration tests
└── output/             # Formatter tests
```

---

## 🔍 Issue Reporting & Feature Requests

- For major changes, open an issue to discuss your proposal before submitting a PR
- Use clear, descriptive titles and provide context or examples
- Tag issues appropriately (bug, enhancement, question, etc.)

---

## 🔎 Code Review Process

- All PRs are reviewed for code quality, clarity, and alignment with project goals
- Be open to feedback and ready to revise your code
- Reviews are constructive and respectful—help each other grow!

---

## 🤝 Community & Conduct

- Be kind, inclusive, and professional in all interactions
- See the [ROADMAP.md](ROADMAP.md) for project direction and priorities
- Questions? Open an issue or start a discussion

---

## 📄 License & Contributor Agreement

By contributing, you agree your work will be licensed under the [MIT License](LICENSE).

---

*Thank you for helping make astr0 shine brighter!*
