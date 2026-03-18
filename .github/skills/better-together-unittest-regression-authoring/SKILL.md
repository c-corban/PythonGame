---
name: better-together-unittest-regression-authoring
description: 'Use when writing Better-Together regression tests, adding unittest coverage, mocking pygame or sockets, reusing tests/test_support.py helpers, or converting a bug repro into a repo-style test.'
argument-hint: 'Describe the bug, changed files, or test coverage you want to add.'
---

# Better-Together Unittest Regression Authoring

## When to Use

- Adding regression coverage after a bug fix.
- Writing new `unittest` modules or extending existing ones.
- Matching repo patterns for headless pygame tests, network tests, launcher tests, or import-safe tests.

## Procedure

1. Start with the [test authoring patterns](./references/test-authoring-patterns.md) and match the nearest existing test style before inventing a new structure.
2. Keep the test focused on the smallest observable behavior that proves the regression is fixed.
3. Reuse existing helpers such as `tests/test_support.py`, import-safe module loading patterns, and `unittest.mock.patch` rather than building new harnesses unless the existing patterns cannot fit.
4. Use the [coverage selection guide](./references/coverage-selection-guide.md) to decide whether the regression should live in a pure helper test, a client/server module test, or a live integration test.
5. When the bug is runtime-visible but hard to automate completely, add the best automated regression you can and clearly document the remaining manual smoke expectation.

## References

- [Test authoring patterns](./references/test-authoring-patterns.md)
- [Coverage selection guide](./references/coverage-selection-guide.md)
