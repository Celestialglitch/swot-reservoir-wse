# Contributing

Contributions to **swot-reservoir-wse** are welcome. These may include bug fixes, documentation improvements, support for additional SWOT observation products, improvements to the existing processing workflow, and other features relevant to reservoir Water Surface Elevation extraction.

## Reporting Issues

If you encounter a problem, please open a GitHub issue with enough information to reproduce it.

Where applicable, include:

- the command that produced the problem
- the relevant input parameters
- the complete error message or traceback
- the operating system and Python version
- the installed version of **swot-reservoir-wse**

Please do not include passwords, authentication tokens, Earthdata credentials, or other sensitive information.

## Proposing Changes

For substantial changes or new functionality, opening an issue before submitting an implementation is recommended. This allows the proposed behaviour and its relationship to the existing processing workflow to be discussed first.

Examples include support for a new SWOT observation product, changes to quality-control procedures, or modifications that affect generated WSE values.

## Development Setup

Clone the repository:

```bash
git clone https://github.com/Celestialglitch/swot-reservoir-wse.git
cd swot-reservoir-wse
```

Create and activate a virtual environment.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the package:

```bash
python -m pip install .
```

After making changes, reinstall the package before testing:

```bash
python -m pip install . --upgrade
```

## Pull Requests

Pull requests should focus on a specific change and should clearly describe what has been modified and why.

Before submitting a pull request:

- verify that the package installs successfully
- test the affected CLI commands
- ensure that existing functionality continues to work
- update the documentation when user-facing behaviour changes
- avoid committing generated outputs, cached SWOT products, credentials, or local runtime files

## Adding Observation Sources

The package is structured so that additional SWOT observation products can be incorporated into the processing framework.

Contributions adding a new observation source should keep product-specific processing separate from the common reservoir WSE workflow and should document the source data, processing procedure, quality-control criteria, configuration parameters, and resulting outputs.

## Documentation

Documentation improvements are welcome, including corrections, clearer explanations, additional examples, and descriptions of scientific or processing parameters.

Documentation for the package is maintained in the `docs/` directory and published through Read the Docs.

## License

By contributing to this repository, you agree that your contributions will be distributed under the terms of the project's [MIT License](LICENSE).
