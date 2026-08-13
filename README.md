# SWOT Reservoir WSE

**swot-reservoir-wse** is a Python package for generating reservoir-specific Water Surface Elevation (WSE) time series from Surface Water and Ocean Topography (SWOT) observations.

A user supplies a dam location, a date range, and a SWOT observation source. The package then handles the workflow from reservoir footprint generation to the final quality-controlled reservoir WSE time series.

The current release supports:

- **SWOT Level-2 Lake Single Pass (LakeSP) Observation Vector Product, Version D**
- **SWOT Level-2 High Rate Pixel Cloud (PIXC) Product, Version D**

---

## Overview

A processing run requires:

- dam latitude
- dam longitude
- start date
- end date
- observation source (`lakesp` or `pixc`)

For example:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

From the supplied dam coordinates, **swot-reservoir-wse** derives the corresponding reservoir footprint, identifies relevant SWOT observations, associates them with the reservoir, applies source-specific screening and aggregation, and generates the final reservoir-specific WSE time series.

LakeSP and PIXC are processed as independent observation sources. The user explicitly selects the product to process; there is no automatic fallback between them.

For the project background and motivation, see the [Introduction](docs/introduction.md).

---

## Features

- Generates reservoir-specific WSE time series from dam coordinates and a requested date range.
- Derives the corresponding reservoir footprint from the JRC Global Surface Water dataset using Google Earth Engine.
- Supports independent processing of SWOT LakeSP and PIXC Version D observations.
- Discovers relevant SWOT products through NASA Earthdata.
- Applies source-specific spatial association, screening, daily aggregation, and temporal outlier filtering.
- Supports configurable LakeSP quality classes: `GOOD`, `SUSPECT`, `DEGRADED`, and `BAD`.
- Produces CSV time series and optional PNG visualizations.
- Provides a command-line interface for reproducible and scriptable processing.
- Supports configurable science cycles, search parameters, filtering thresholds, output locations, and parallel processing.
- Manages Google Earth Engine and NASA Earthdata authentication through the CLI.
- Reuses generated reservoir footprints and downloaded LakeSP granules when caching is enabled.

---

## Requirements

Before using **swot-reservoir-wse**, ensure that the following are available:

- Python 3.10 or later
- A NASA Earthdata Login account
- A Google Earth Engine account
- A Google Cloud project configured for Earth Engine access
- An active internet connection
- Sufficient local disk space for downloaded SWOT products and temporary processing data

Required Python dependencies are installed automatically with the package.

PIXC processing operates on high-resolution pixel-cloud data and can require substantially more memory, disk activity, and processing time than LakeSP processing.

---

## External Service Setup

The package relies on two external services:

- **Google Earth Engine** for reservoir footprint generation using the JRC Global Surface Water dataset.
- **NASA Earthdata** for discovery and access to SWOT LakeSP and PIXC products.

The required accounts must be created before the package can authenticate them.

### NASA Earthdata

Create an Earthdata Login account at:

[https://urs.earthdata.nasa.gov/](https://urs.earthdata.nasa.gov/)

After registration, sign in once through the Earthdata website and complete any required account activation or terms-of-use steps.

### Google Earth Engine

Register for Google Earth Engine at:

[https://code.earthengine.google.com/](https://code.earthengine.google.com/)

Use the Google account that will be associated with the Google Cloud project used by the package.

### Google Cloud Project

Create or select a Google Cloud project at:

[https://console.cloud.google.com/](https://console.cloud.google.com/)

Copy the **Project ID** from the project dashboard.

The Project ID is different from the project display name and project number.

Enable the **Google Earth Engine API** for the project and complete the Earth Engine project-registration procedure presented by Google.

For detailed setup instructions, see [Installation](docs/installation.md).

---

## Installation

Clone the repository:
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
Upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

Install the package:
Install the package:

```bash
python -m pip install .
```

If an earlier local installation already exists:

```bash
python -m pip install . --upgrade
```

If an earlier local installation already exists:

```bash
python -m pip install . --upgrade
```

Verify the installation:
Verify the installation:

```bash
swot-reservoir-wse --help
```

For complete installation and external-service setup instructions, see [Installation](docs/installation.md).

---

## Working Directory

**swot-reservoir-wse** uses the directory from which the command is run as its runtime working directory.

With the default configuration, running the package from a directory may create:

```text
working-directory/
├── config.json
├── cache/
│   ├── reservoir_polygons/
│   └── lakesp_granules/
├── downloads/
│   └── temp/
└── outputs/
```

This allows separate projects or analyses to maintain independent configurations and outputs.

Authentication credentials themselves are managed separately:

- Google Earth Engine OAuth credentials are managed by the Earth Engine authentication system.
- NASA Earthdata credentials are stored in the user's netrc file.

---

## Authentication

Authenticate Google Earth Engine and NASA Earthdata with:

```bash
swot-reservoir-wse auth
```

Existing valid credentials are reused whenever possible.

If Earth Engine has not yet been configured in the current working directory, the package asks for the Google Cloud Project ID:

```text
Google Earth Engine project ID:
```

If Earthdata credentials are unavailable, the package requests the Earthdata Login username and password, validates them, and stores them in the user's netrc credential file.

The services can also be managed independently:

```bash
swot-reservoir-wse auth --earth-engine-only
swot-reservoir-wse auth --earthdata-only
```

Force reauthentication:

```bash
swot-reservoir-wse auth --force
```

Remove authentication information managed directly by the package:

```bash
swot-reservoir-wse auth --remove
```

Service-specific variants are also available:

```bash
swot-reservoir-wse auth --earth-engine-only --force
swot-reservoir-wse auth --earthdata-only --force

swot-reservoir-wse auth --earth-engine-only --remove
swot-reservoir-wse auth --earthdata-only --remove
```

For credential storage, removal, reauthentication behaviour, and all authentication options, see [Authentication](docs/authentication.md).

---

## Basic Usage

The general extraction command is:

```bash
swot-reservoir-wse extract --lat <latitude> --lon <longitude> --start-date YYYY-MM-DD --end-date YYYY-MM-DD --source <source>
```

Supported observation sources are:

```text
lakesp
pixc
```

The source must be selected explicitly.

### LakeSP

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

### PIXC

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
```

The latitude and longitude specify the dam location. The package uses that location to derive the corresponding reservoir footprint before processing the selected SWOT observations.

See [Usage](docs/usage.md) for a detailed walkthrough.

---

## Processing Workflow

Every extraction begins with a common reservoir-identification stage:

1. Receive the dam coordinates and requested observation period.
2. Generate or retrieve the corresponding reservoir footprint.
3. Execute the source pipeline selected by the user.
4. Construct the final reservoir-specific WSE time series.
5. Write the generated outputs.

The source-specific processing differs after the reservoir footprint has been obtained.

### LakeSP

The LakeSP pipeline:

1. searches NASA Earthdata for candidate LakeSP granules;
2. verifies reservoir intersections;
3. identifies associated LakeSP `lake_id` values;
4. extracts reservoir observations;
5. removes partial observations;
6. applies the configured LakeSP quality classes;
7. aggregates accepted observations by acquisition date;
8. assigns a representative daily quality status;
9. applies temporal Median Absolute Deviation (MAD) filtering.

### PIXC

The PIXC pipeline:

1. searches NASA Earthdata for candidate PIXC granules;
2. verifies candidate footprints using CMR metadata;
3. downloads verified PIXC products;
4. extracts and spatially filters pixel-cloud observations;
5. applies the configured water classification and classification-quality screening;
6. calculates pixel WSE as `height - geoid`;
7. aggregates accepted pixels by acquisition date;
8. applies temporal MAD filtering.

For the complete processing design, see [Package Architecture](docs/architecture.md).

---

## CLI Commands
## CLI Commands

The package provides four primary command groups.
The package provides four primary command groups.

| Command | Purpose |
| --- | --- |
| `extract` | Generate a reservoir-specific WSE time series |
| `auth` | Manage Google Earth Engine and NASA Earthdata authentication |
| `config` | View, modify, or reset package configuration |
| `cache` | Inspect or clear persistent cached data |

Display all commands:
Display all commands:

```bash
swot-reservoir-wse --help
```

Display command-specific help:

```bash
swot-reservoir-wse extract --help
swot-reservoir-wse auth --help
swot-reservoir-wse config --help
swot-reservoir-wse cache --help
```

For every command and option, see the [Command Reference](docs/command_reference.md).

---

## Configuration

Display the active configuration:

```bash
swot-reservoir-wse config show
```

Change an individual value:

```bash
swot-reservoir-wse config set <key> <value>
```

For example:

```bash
swot-reservoir-wse config set max_workers 4
```

LakeSP-specific settings use dotted keys:

```bash
swot-reservoir-wse config set sources.lakesp.mad_threshold 2.5
```

For example, change the accepted LakeSP quality classes:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded
```

PIXC settings are configured independently:

```bash
swot-reservoir-wse config set sources.pixc.mad_threshold 2.5
```

Restrict PIXC science cycles:

```bash
swot-reservoir-wse config set sources.pixc.science_cycles 045,046,047
```

Restore all defaults:

```bash
swot-reservoir-wse config reset
```

See [Configuration](docs/configuration.md) for every configurable parameter and its effect on processing.

---

## Outputs

Every successful run generates a source-specific CSV time series.

Example LakeSP files:

```text
19.69000_73.34000_lakesp_wse.csv
19.69000_73.34000_lakesp_wse.png
```

Example PIXC files:

```text
19.69000_73.34000_pixc_wse.csv
19.69000_73.34000_pixc_wse.png
```

The PNG file is generated when:

```text
generate_plot = true
```

Disable plotting with:

```bash
swot-reservoir-wse config set generate_plot false
```

### LakeSP Output

The final LakeSP CSV contains:

```text
date
wse_median
quality_status
```

The supported daily quality-status labels are:

```text
GOOD
SUSPECT
DEGRADED
BAD
```

Only quality classes permitted by the active configuration can contribute to the final daily status.

The LakeSP PNG uses quality-dependent circular markers connected by a grey WSE progression line.

### PIXC Output

The PIXC CSV contains the daily representative WSE together with additional pixel-level summary statistics such as mean WSE, WSE spread, accepted pixel count, mean water fraction, and mean phase-noise standard deviation.

For the complete schemas and plotting behaviour, see [Outputs](docs/outputs.md).

---

## Cache

The package currently maintains two persistent cache types.

| Cache | Purpose |
| --- | --- |
| Reservoir Polygon Cache | Stores generated reservoir footprints |
| LakeSP Granule Cache | Stores downloaded LakeSP products for reuse |

Display the current cache status:

```bash
swot-reservoir-wse cache
```

Clear the reservoir polygon cache:

```bash
swot-reservoir-wse cache --clear-polygons
```

Clear the LakeSP granule cache:

```bash
swot-reservoir-wse cache --clear-lakesp
```

Clear both:

```bash
swot-reservoir-wse cache --clear-all
```

PIXC granules are currently processed in temporary working directories and are not retained in a persistent PIXC granule cache.

Caching behaviour and paths can be changed through the configuration system.

---

## Possible Processing Messages
## Possible Processing Messages

Some messages indicate that the requested location, period, or source did not produce usable observations. They do not necessarily indicate a package failure.

### No reservoir polygon found

```text
```text
No reservoir polygon found at lat=<latitude>, lon=<longitude>.
```

A suitable reservoir footprint could not be identified for the supplied location.
A suitable reservoir footprint could not be identified for the supplied location.

### No LakeSP granules found
### No LakeSP granules found

```text
```text
No LakeSP granules found.
```

No candidate LakeSP products were found for the requested location and period.

### No LakeSP intersections found
### No LakeSP intersections found

```text
```text
No LakeSP intersections found.
```

Candidate LakeSP products were found, but no relevant observations intersected the generated reservoir footprint.

### No LakeSP observations after filtering

```text
No observations remained after filtering.
```

LakeSP observations were extracted, but none remained after the configured screening and temporal filtering stages.

### No PIXC granules found

```text
No PIXC granules found.
```

No candidate PIXC products were found for the requested location and period.

### No PIXC intersections found

```text
No PIXC intersections found.
```

Candidate PIXC metadata were found, but no candidate footprint intersected the reservoir.

### No usable PIXC pixels found

```text
No usable PIXC pixels found.
```

Verified PIXC granules were processed, but no pixels remained after spatial and product-level filtering.

### No PIXC observations after filtering

```text
No PIXC observations remained after filtering.
```

Daily PIXC observations were generated, but none remained after temporal filtering.

---

## Troubleshooting

### Google Earth Engine permission error

An error similar to:
### Google Earth Engine permission error

An error similar to:

```text
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
3. Grant access to the Google account used for Earth Engine.
4. Assign the **Service Usage Consumer** role where required.
5. Allow a few minutes for the permission change to propagate.

Retry:

```bash
swot-reservoir-wse auth --earth-engine-only
```

If necessary:

```bash
swot-reservoir-wse auth --earth-engine-only --force
```

### NASA Earthdata authentication problems

Force Earthdata reauthentication:

```bash
swot-reservoir-wse auth --earthdata-only --force
```

Remove stored Earthdata credentials:

```bash
swot-reservoir-wse auth --earthdata-only --remove
```

Then authenticate again:

```bash
swot-reservoir-wse auth --earthdata-only
```

### PIXC processing uses too much memory

PIXC processing can be memory-intensive because multiple high-resolution pixel-cloud granules may be processed concurrently.

Reduce the worker count:

```bash
swot-reservoir-wse config set max_workers 4
```

or, on systems with less available memory:

```bash
swot-reservoir-wse config set max_workers 2
```

---

## Documentation

Complete documentation for **swot-reservoir-wse** is available on Read the Docs:

[**https://swot-reservoir-wse.readthedocs.io/**](https://swot-reservoir-wse.readthedocs.io/)

Documentation includes:

- [Introduction](https://swot-reservoir-wse.readthedocs.io/en/latest/introduction.html)
- [Installation](https://swot-reservoir-wse.readthedocs.io/en/latest/installation.html)
- [Authentication](https://swot-reservoir-wse.readthedocs.io/en/latest/authentication.html)
- [Usage](https://swot-reservoir-wse.readthedocs.io/en/latest/usage.html)
- [Configuration](https://swot-reservoir-wse.readthedocs.io/en/latest/configuration.html)
- [Command Reference](https://swot-reservoir-wse.readthedocs.io/en/latest/command_reference.html)
- [Package Architecture](https://swot-reservoir-wse.readthedocs.io/en/latest/architecture.html)
- [Outputs](https://swot-reservoir-wse.readthedocs.io/en/latest/outputs.html)

Documentation source files are maintained in the `docs/` directory of this repository.

---

## Contributing

Bug reports, documentation improvements, processing enhancements, and contributions adding support for additional SWOT observation products are welcome.

See [CONTRIBUTING.md](CONTRIBUTING.md) for development and contribution guidelines.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.