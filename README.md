# SWOT Reservoir WSE

**swot-reservoir-wse** is a Python package for generating reservoir-specific Water Surface Elevation (WSE) time series from Surface Water and Ocean Topography (SWOT) observations.

A user supplies a dam location and a date range. The package then handles the workflow from reservoir footprint generation to the final quality-controlled WSE time series.

The current release supports the SWOT Level-2 Lake Single Pass (LakeSP) Observation Vector Product, Version D.

---

## Overview

A basic processing run requires:

- dam latitude
- dam longitude
- start date
- end date

For example:

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16
```

From the supplied dam coordinates, the package derives the corresponding reservoir footprint, identifies relevant SWOT observations, associates them with the reservoir, applies quality control, aggregates accepted observations by acquisition date, and generates the final reservoir-specific WSE time series.

The processing framework separates the common reservoir workflow from product-specific observation handling. LakeSP is currently the implemented observation source.

For the project background and motivation, see the [Introduction](docs/introduction.md).

---

## Features

- Generates reservoir-specific WSE time series from dam coordinates and a specified date range.
- Derives the corresponding reservoir footprint from the JRC Global Surface Water dataset.
- Discovers relevant SWOT LakeSP observations through NASA Earthdata.
- Associates LakeSP observations with the generated reservoir footprint.
- Applies quality screening, daily WSE aggregation, and temporal outlier filtering.
- Produces CSV time series and optional PNG visualizations through a single CLI workflow.
- Supports configurable processing, caching, output locations, science-cycle selection, and parallel granule processing.
- Manages Google Earth Engine and NASA Earthdata authentication through the package CLI.
- Reuses cached reservoir footprints and downloaded LakeSP products where possible.

---

## Requirements

Before using **swot-reservoir-wse**, ensure that the following are available:

- Python 3.10 or later
- A NASA Earthdata Login account
- A Google Earth Engine account
- A Google Cloud project configured for Earth Engine access
- An active internet connection
- Sufficient local disk space for downloaded SWOT products and cached data

Required Python dependencies are installed automatically with the package.

---

## External Service Setup

The package relies on:

- **Google Earth Engine** for reservoir footprint generation using the JRC Global Surface Water dataset.
- **NASA Earthdata** for discovery and access to SWOT observation products.

The required accounts must be created before the package can authenticate them.

### NASA Earthdata

Create an Earthdata Login account at:

[https://urs.earthdata.nasa.gov/](https://urs.earthdata.nasa.gov/)

After registration, sign in once through the Earthdata website and complete any required account activation or terms-of-use steps.

---

### Google Earth Engine

Register for Google Earth Engine at:

[https://code.earthengine.google.com/](https://code.earthengine.google.com/)

Use the Google account that will be associated with the Google Cloud project used by the package.

---

### Google Cloud Project

Create or select a Google Cloud project at:

[https://console.cloud.google.com/](https://console.cloud.google.com/)

Copy the **Project ID** from the project dashboard.

The Project ID is different from the project display name and project number.

Enable the **Google Earth Engine API** for that project and complete the Earth Engine project registration process presented by Google.

For more detailed setup instructions, see [Installation](docs/installation.md).

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Celestialglitch/swot-reservoir-wse.git
cd swot-reservoir-wse
```

Create a virtual environment.

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

If an earlier local installation already exists:

```bash
python -m pip install . --upgrade
```

Verify the installation:

```bash
swot-wse --help
```

Once installed, `swot-wse` can be run from any directory.

---

## Authentication

Authenticate Google Earth Engine and NASA Earthdata with:

```bash
swot-wse auth
```

Existing credentials are reused whenever possible.

If Earth Engine has not yet been configured, the package asks for the Google Cloud Project ID:

```text
Google Earth Engine project ID:
```

If Earthdata credentials are not already available, the package requests the Earthdata Login username and password, validates them, and stores them locally for later use.

Authentication can also be managed independently:

```bash
swot-wse auth --earth-engine-only
swot-wse auth --earthdata-only
```

Force reauthentication:

```bash
swot-wse auth --force
```

Remove locally managed authentication information:

```bash
swot-wse auth --remove
```

Service-specific variants are also available:

```bash
swot-wse auth --earth-engine-only --force
swot-wse auth --earthdata-only --force

swot-wse auth --earth-engine-only --remove
swot-wse auth --earthdata-only --remove
```

For credential storage, reauthentication behaviour, and all authentication options, see [Authentication](docs/authentication.md).

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

The latitude and longitude specify the dam location. The package uses that location to determine the corresponding reservoir footprint before processing SWOT observations.

LakeSP can also be selected explicitly:

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

If `--source` is omitted, the default mode is:

```text
auto
```

In the current release:

```text
auto → lakesp
```

LakeSP is currently the only implemented observation source.

See [Usage](docs/usage.md) for a more detailed walkthrough.

---

## Processing Workflow

For a typical execution, **swot-reservoir-wse** performs the following workflow:

1. Receive the dam coordinates and requested observation period.
2. Generate or retrieve the corresponding reservoir footprint.
3. Search NASA Earthdata for candidate SWOT LakeSP granules.
4. Determine which candidate granules contain observations associated with the reservoir.
5. Extract the relevant LakeSP observations.
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
|---|---|
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

For the complete CLI reference, see [Command Reference](docs/command_reference.md).

---

## Configuration

Display the active configuration:

```bash
swot-wse config show
```

Change an individual value:

```bash
swot-wse config set <key> <value>
```

For example:

```bash
swot-wse config set max_workers 4
```

Nested LakeSP settings use dotted keys:

```bash
swot-wse config set sources.lakesp.mad_threshold 2.5
```

Restore the defaults:

```bash
swot-wse config reset
```

Configuration controls reservoir footprint generation, LakeSP processing, parallel execution, caching, output generation, and quality filtering.

See [Configuration](docs/configuration.md) for the meaning and effect of every configurable parameter.

---

## Outputs

A successful run generates a reservoir-specific WSE time series as a CSV file.

The current output contains:

- observation date
- representative daily WSE
- daily quality status

When plot generation is enabled, the package also creates a PNG visualization of the final time series.

Plot generation can be disabled with:

```bash
swot-wse config set generate_plot false
```

Outputs are written to the configured output directory.

By default, runtime data are maintained under the user-level package directory:

```text
~/.swot_wse/
```

For details about the CSV fields, `GOOD` and `SUSPECT` quality statuses, MAD filtering, and generated files, see [Outputs](docs/outputs.md).

---

## Cache

The package maintains two reusable caches:

| Cache | Purpose |
|---|---|
| Reservoir Polygon Cache | Stores generated reservoir footprints |
| LakeSP Granule Cache | Stores downloaded LakeSP products for reuse |

Display the current cache status:

```bash
swot-wse cache
```

Clear the reservoir polygon cache:

```bash
swot-wse cache --clear-polygons
```

Clear the LakeSP granule cache:

```bash
swot-wse cache --clear-lakesp
```

Clear both:

```bash
swot-wse cache --clear-all
```

Caching behaviour and locations can also be changed through the configuration system.

---

## Possible Processing Messages

Some messages indicate that a requested reservoir or observation period did not produce usable observations. They do not necessarily indicate a package failure.

### No reservoir polygon found

```text
No reservoir polygon found at lat=<latitude>, lon=<longitude>.
```

A suitable reservoir footprint could not be identified for the supplied location.

### No LakeSP granules found

```text
No LakeSP granules found.
```

No candidate LakeSP products were found for the requested location and time period.

### No LakeSP intersections found

```text
No LakeSP intersections found.
```

Candidate products were found, but no relevant LakeSP observations intersected the generated reservoir footprint.

### No observations after filtering

```text
No observations remained after filtering.
```

Observations were extracted, but none remained after the configured quality-control procedure.

---

## Troubleshooting

### Google Earth Engine permission error

An error similar to:

```text
Caller does not have required permission to use project <PROJECT_ID>.
Grant the caller the roles/serviceusage.serviceUsageConsumer role...
```

usually indicates that the authenticated Google account does not have the required permission to use the selected Google Cloud project.

Open the Google Cloud Console:

[https://console.cloud.google.com/](https://console.cloud.google.com/)

Then:

1. Select the project used by **swot-reservoir-wse**.
2. Open **IAM & Admin → IAM**.
3. Grant access to the Google account being used for Earth Engine.
4. Assign the **Service Usage Consumer** role where required.
5. Allow a few minutes for the permission change to propagate.

Retry authentication:

```bash
swot-wse auth --earth-engine-only
```

If necessary:

```bash
swot-wse auth --earth-engine-only --force
```

### NASA Earthdata authentication problems

Force Earthdata reauthentication:

```bash
swot-wse auth --earthdata-only --force
```

Remove the stored Earthdata credentials without immediately authenticating again:

```bash
swot-wse auth --earthdata-only --remove
```

---

## Documentation

Complete documentation for **swot-reservoir-wse** is available on Read the Docs:

**[https://swot-reservoir-wse.readthedocs.io/](https://swot-reservoir-wse.readthedocs.io/)**

The documentation includes:

- [Introduction](https://swot-reservoir-wse.readthedocs.io/en/latest/introduction.html)
- [Installation](https://swot-reservoir-wse.readthedocs.io/en/latest/installation.html)
- [Authentication](https://swot-reservoir-wse.readthedocs.io/en/latest/authentication.html)
- [Usage](https://swot-reservoir-wse.readthedocs.io/en/latest/usage.html)
- [Configuration](https://swot-reservoir-wse.readthedocs.io/en/latest/configuration.html)
- [Command Reference](https://swot-reservoir-wse.readthedocs.io/en/latest/command_reference.html)
- [Package Architecture](https://swot-reservoir-wse.readthedocs.io/en/latest/architecture.html)
- [Outputs](https://swot-reservoir-wse.readthedocs.io/en/latest/outputs.html)

The documentation covers the complete workflow from installation and authentication through reservoir processing, configuration, output interpretation, and the internal package architecture.

Documentation source files are maintained in the [`docs/`](docs/) directory of this repository.

---

## Contribution

Bug reports, documentation improvements, processing enhancements, and contributions adding support for additional SWOT observation products are welcome.

See [CONTRIBUTING.md](CONTRIBUTING.md) for development and contribution guidelines.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
