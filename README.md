# swot-reservoir-wse

**swot-reservoir-wse** is a Python package for generating reservoir-specific Water Surface Elevation (WSE) time series from Surface Water and Ocean Topography (SWOT) observations using user-supplied dam coordinates and a user-defined date range.

The package provides an end-to-end command-line workflow for reservoir footprint extraction, SWOT observation discovery, reservoir association, quality control, temporal aggregation, caching, and output generation.

The current release supports the SWOT Level-2 Lake Single Pass (LakeSP) observation product, Version D.

---

## Overview

A user provides:

- the latitude and longitude of a dam or reservoir location;
- a start date; and
- an end date.

For example:

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16
```

From these inputs, **swot-reservoir-wse** identifies the corresponding reservoir footprint, discovers relevant SWOT observations, associates those observations with the reservoir, applies quality-control procedures, and generates a reservoir-specific WSE time series.

The package is built around an observation-source architecture that separates the common processing workflow from product-specific processing logic. In the current release, LakeSP is the implemented observation source.

For additional background and motivation, see the [Introduction](docs/introduction.md).

---

## Features

- Generates reservoir-specific Water Surface Elevation (WSE) time series from dam coordinates and a specified date range.
- Automatically derives a representative reservoir footprint from the supplied location using the JRC Global Surface Water dataset.
- Discovers relevant SWOT observations through NASA Earthdata.
- Associates SWOT LakeSP observations with the generated reservoir footprint.
- Applies product-quality screening, daily aggregation, and temporal outlier filtering.
- Provides an end-to-end processing workflow through a single reservoir-processing command.
- Produces CSV time series and optional PNG visualizations.
- Provides a command-line interface for reproducible and scriptable processing.
- Manages Google Earth Engine and NASA Earthdata authentication through the package CLI.
- Provides centralized configuration for processing, caching, output generation, and observation-source parameters.
- Maintains reusable reservoir-footprint and LakeSP caches to reduce repeated computation and downloads.
- Uses an observation-source architecture that allows additional SWOT products to be integrated in future releases.

---

## Requirements

Before using **swot-reservoir-wse**, ensure that the following are available:

- Python 3.10 or later
- A NASA Earthdata Login account
- A Google Earth Engine account
- A Google Cloud project configured for Earth Engine access
- An active internet connection
- Sufficient local disk space for downloaded SWOT products and cached data

Python dependencies are installed automatically when the package is installed with `pip`.

---

## External Service Setup

The package relies on two external services:

- **Google Earth Engine** for reservoir footprint extraction using the JRC Global Surface Water dataset.
- **NASA Earthdata** for discovery and access to SWOT observation products.

The required accounts must be created before authentication can be performed through the package.

### 1. Create a NASA Earthdata Login Account

Create a NASA Earthdata Login account at:

https://urs.earthdata.nasa.gov/

After registration, sign in through the Earthdata website and complete any required account activation or terms-of-use steps.

Your Earthdata username and password will be required when authenticating the package.

---

### 2. Register for Google Earth Engine

Register for Google Earth Engine at:

https://code.earthengine.google.com/

Use the Google account that you intend to associate with the Google Cloud project used by the package.

Complete the registration and any verification steps required by Google.

Earth Engine access must be active before the package can perform reservoir-footprint extraction.

---

### 3. Create a Google Cloud Project

Open the Google Cloud Console:

https://console.cloud.google.com/

Create or select the Google Cloud project that will be used with Earth Engine.

From the project dashboard, copy the **Project ID**.

The Project ID is different from the project display name and project number.

The package uses this Project ID when initializing Google Earth Engine.

---

### 4. Enable the Earth Engine API

Within the selected Google Cloud project:

1. Open **APIs & Services**.
2. Open the API Library.
3. Search for **Google Earth Engine API**.
4. Select the API.
5. Enable it for the project.

Earth Engine requests cannot be performed through the project until the API is enabled.

---

### 5. Register the Cloud Project for Earth Engine

Open the Google Earth Engine Code Editor:

https://code.earthengine.google.com/

Sign in using the Google account associated with the Cloud project.

Select or register the Google Cloud project for Earth Engine use and complete the registration procedure presented by Google.

For non-commercial use, select the appropriate non-commercial registration option and quota tier where applicable.

The exact Google registration interface may change over time, so follow the instructions presented by Earth Engine during registration.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Celestialglitch/swot-reservoir-wse.git
cd swot-reservoir-wse
```

Creating a virtual environment is recommended.

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

Upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

Install the package:

```bash
python -m pip install .
```

If an earlier local installation already exists, upgrade it with:

```bash
python -m pip install . --upgrade
```

Verify the installation:

```bash
swot-wse --help
```

A successful installation displays the available command groups and CLI options.

For additional installation information, see [Installation](docs/installation.md).

---

## Authentication

Before processing reservoirs, authenticate the external services used by the package.

### Authenticate Both Services

Run:

```bash
swot-wse auth
```

The command manages both:

- Google Earth Engine authentication; and
- NASA Earthdata authentication.

For Earth Engine, the package uses the configured Google Cloud Project ID. If no Project ID has been stored, the command prompts for one:

```text
Google Earth Engine project ID:
```

Existing valid credentials are reused when possible.

For NASA Earthdata, existing persistent credentials are also reused when available. Otherwise, the package starts the Earthdata authentication process and stores credentials for subsequent executions.

---

### Authenticate Only Google Earth Engine

```bash
swot-wse auth --earth-engine-only
```

A Project ID can also be supplied directly:

```bash
swot-wse auth --earth-engine-only --project-id my-earth-engine-project
```

---

### Authenticate Only NASA Earthdata

```bash
swot-wse auth --earthdata-only
```

---

### Force Reauthentication

Force authentication instead of reusing existing credentials:

```bash
swot-wse auth --force
```

The option can also be restricted to one service:

```bash
swot-wse auth --earth-engine-only --force
```

or:

```bash
swot-wse auth --earthdata-only --force
```

---

### Remove Stored Authentication

Remove locally managed authentication information:

```bash
swot-wse auth --remove
```

This can also be restricted to a single service:

```bash
swot-wse auth --earth-engine-only --remove
```

```bash
swot-wse auth --earthdata-only --remove
```

For Google Earth Engine, this removes the Project ID stored in the package configuration. Google-managed OAuth credentials are not deleted by this operation.

For complete authentication documentation, see [Authentication](docs/authentication.md).

---

## Basic Usage

Generate a reservoir-specific WSE time series with:

```bash
swot-wse polygon --lat <latitude> --lon <longitude> --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

Example:

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16
```

The latitude and longitude identify the dam or reservoir location from which the package determines the corresponding reservoir footprint.

The observation source can also be selected explicitly:

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

If `--source` is omitted, the default source-selection mode is:

```text
auto
```

In the current release:

```text
auto → LakeSP
```

For a more detailed walkthrough, see [Usage](docs/usage.md).

---

## Processing Workflow

For a typical execution, **swot-reservoir-wse** performs the following workflow:

1. Receive the dam coordinates and requested observation period.
2. Generate or retrieve the corresponding reservoir footprint.
3. Search NASA Earthdata for candidate SWOT LakeSP granules.
4. Determine which candidate granules contain observations associated with the reservoir.
5. Extract relevant LakeSP observations.
6. Apply product-quality screening.
7. Aggregate accepted observations by acquisition date.
8. Apply temporal Median Absolute Deviation (MAD) filtering.
9. Construct the final reservoir-specific WSE time series.
10. Write the generated outputs and retain reusable cached data where enabled.

For the internal package design and data flow, see [Package Architecture](docs/architecture.md).

---

## CLI Commands

The package provides four primary command groups.

| Command | Purpose |
| --- | --- |
| `polygon` | Generate a reservoir-specific WSE time series |
| `auth` | Manage Google Earth Engine and NASA Earthdata authentication |
| `config` | View, modify, or reset package configuration |
| `cache` | Inspect or manage cached data |

Display all commands:

```bash
swot-wse --help
```

Display command-specific help:

```bash
swot-wse polygon --help
swot-wse auth --help
swot-wse config --help
swot-wse cache --help
```

For every supported command and option, see the [Command Reference](docs/command_reference.md).

---

## Configuration

The active package configuration can be displayed with:

```bash
swot-wse config show
```

Individual values can be changed without modifying the package source code:

```bash
swot-wse config set <key> <value>
```

For example:

```bash
swot-wse config set max_workers 4
```

Nested source-specific values use dotted keys:

```bash
swot-wse config set sources.lakesp.mad_threshold 2.5
```

Restore the default configuration with:

```bash
swot-wse config reset
```

Configuration controls reservoir extraction, LakeSP processing, quality filtering, parallel execution, caching, output generation, and other runtime behaviour.

For descriptions of all configurable parameters, see [Configuration](docs/configuration.md).

---

## Outputs

A successful processing run generates a reservoir-specific Water Surface Elevation time series.

### CSV Time Series

The CSV output contains the processed reservoir WSE observations and their associated information.

### PNG Visualization

When plot generation is enabled, the package also generates a PNG visualization of the WSE time series.

Plot generation can be disabled with:

```bash
swot-wse config set generate_plot false
```

Output files are written to the configured output directory.

For details about generated files, fields, and quality information, see [Outputs](docs/outputs.md).

---

## Cache

The package maintains reusable local caches to avoid unnecessary repeated processing.

| Cache | Purpose |
| --- | --- |
| Reservoir Polygon Cache | Stores generated reservoir footprints |
| LakeSP Granule Cache | Stores downloaded LakeSP products for reuse |

Display the cache summary:

```bash
swot-wse cache
```

Clear reservoir polygons:

```bash
swot-wse cache --clear-polygons
```

Clear LakeSP granules:

```bash
swot-wse cache --clear-lakesp
```

Clear all package caches:

```bash
swot-wse cache --clear-all
```

Caching can also be enabled or disabled through the configuration system.

---

## Possible Processing Messages

Some messages indicate that the requested reservoir or observation period did not produce usable observations. They do not necessarily indicate a package failure.

### No Reservoir Polygon Found

```text
No reservoir polygon found at lat=<latitude>, lon=<longitude>.
```

The package could not identify a suitable reservoir footprint for the supplied location.

### No LakeSP Granules Found

```text
No LakeSP granules found.
```

No candidate LakeSP products were found for the requested spatial and temporal search.

### No LakeSP Intersections Found

```text
No LakeSP intersections found.
```

Candidate products were discovered, but no usable observations were associated with the generated reservoir footprint.

### No Observations After Filtering

```text
No observations remained after filtering.
```

Observations were extracted, but none remained after the configured quality-control procedure.

---

## Troubleshooting

### Google Earth Engine Permission Error

An error similar to:

```text
Caller does not have required permission to use project <PROJECT_ID>.
Grant the caller the roles/serviceusage.serviceUsageConsumer role...
```

indicates that the authenticated Google account does not have the required permission to use the selected Google Cloud project.

Open the Google Cloud Console:

https://console.cloud.google.com/

Then:

1. Select the Google Cloud project used by **swot-reservoir-wse**.
2. Open **IAM & Admin → IAM**.
3. Grant access to the Google account being used for Earth Engine.
4. Assign the **Service Usage Consumer** role where required.
5. Allow a few minutes for IAM changes to propagate.

Then retry authentication:

```bash
swot-wse auth --earth-engine-only
```

If necessary, force a new authentication flow:

```bash
swot-wse auth --earth-engine-only --force
```

### NASA Earthdata Authentication Problems

Force a new Earthdata authentication:

```bash
swot-wse auth --earthdata-only --force
```

The package removes its stored Earthdata credentials and starts a new authentication flow.

To remove the stored credentials without immediately authenticating again:

```bash
swot-wse auth --earthdata-only --remove
```

---

## Documentation

The repository contains detailed documentation for the package:

- [Introduction](docs/introduction.md)
- [Installation](docs/installation.md)
- [Authentication](docs/authentication.md)
- [Usage](docs/usage.md)
- [Configuration](docs/configuration.md)
- [Command Reference](docs/command_reference.md)
- [Package Architecture](docs/architecture.md)
- [Outputs](docs/outputs.md)
- [Contributing](CONTRIBUTING.md)

The documentation can also be built locally with Sphinx:

```bash
python -m pip install -r docs/requirements.txt
python -m sphinx -b html docs docs/_build/html
```

---

## Contributing

Contributions, bug reports, documentation improvements, and proposals for additional SWOT observation-source implementations are welcome.

See [CONTRIBUTING.md](CONTRIBUTING.md) for development and contribution guidelines.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
