# swot-reservoir-wse

A configurable Python package that generates reservoir-specific **Water Surface Elevation (WSE) time series** from observations of the **Surface Water and Ocean Topography (SWOT)** mission.

Starting from a dam location and an observation period, the package identifies the corresponding reservoir footprint, discovers relevant SWOT observations, performs source-specific spatial and quality processing, and generates a quality-controlled reservoir WSE time series.

The package currently supports two independently selectable SWOT Level-2 High Rate products:

- **Lake Single Pass (LakeSP) Observation Vector Product, Version D**
- **Water Mask Pixel Cloud (PIXC) Product, Version D**

> **Documentation:**  
> [https://swot-reservoir-wse.readthedocs.io/](https://swot-reservoir-wse.readthedocs.io/)

---

## Why swot-reservoir-wse?

SWOT observations are publicly available through NASA Earthdata, but obtaining a reservoir-specific WSE time series from a dam coordinate requires considerably more than downloading a product.

For **LakeSP**, relevant continent/pass granules must be discovered, the lake observations corresponding to the target reservoir must be spatially identified, appropriate observations must be extracted, and product-quality information must be handled before constructing the time series.

For **PIXC**, the processing problem is different. Relevant pixel-cloud granules must be discovered and spatially verified, individual measurements belonging to the reservoir must be isolated, unsuitable pixels must be screened, and the remaining pixel-level measurements must be reduced to reservoir-level WSE observations.

**swot-reservoir-wse** automates these workflows behind a reproducible command-line interface.

---

## Features

- Generate reservoir-specific WSE time series directly from **dam coordinates**.
- Automatically derive reservoir footprints from **JRC Global Surface Water** using **Google Earth Engine**.
- Process **SWOT LakeSP Version D** observations.
- Process **SWOT PIXC Version D** pixel-cloud observations.
- Discover SWOT products automatically through **NASA Earthdata / CMR**.
- Perform source-specific spatial association and quality screening.
- Aggregate accepted observations into reservoir-level WSE measurements.
- Apply temporal **Median Absolute Deviation (MAD)** outlier filtering.
- Configure LakeSP quality classes, SWOT science cycles, search parameters, filtering thresholds, and processing concurrency.
- Cache generated reservoir polygons and downloaded LakeSP products for reuse.
- Generate **CSV time series** and optional **PNG visualizations**.
- Manage Google Earth Engine and NASA Earthdata authentication through the CLI.

---

## Processing Overview

A user provides:

```text
dam latitude
dam longitude
start date
end date
observation source
```

The package then performs:

```text
                         Dam Location
                              │
                              ▼
                    Reservoir Footprint
                 JRC Global Surface Water
                              │
                              ▼
                    Selected SWOT Source
                              │
                   ┌──────────┴──────────┐
                   │                     │
                   ▼                     ▼
                LakeSP                  PIXC
                   │                     │
          Vector observations      Pixel-cloud data
                   │                     │
          Lake association        Reservoir pixels
                   │                     │
          LakeSP screening        PIXC screening
                   │                     │
          Daily aggregation       Daily aggregation
                   │                     │
                   └──────────┬──────────┘
                              │
                              ▼
                    Temporal Filtering
                              │
                              ▼
                  Reservoir WSE Time Series
                              │
                       ┌──────┴──────┐
                       ▼             ▼
                      CSV        optional PNG
```

LakeSP and PIXC are **independent processing sources**. The user explicitly selects which product to process; the package does not automatically fall back from one source to the other.

For the complete processing system, see the [Package Architecture](https://swot-reservoir-wse.readthedocs.io/en/latest/architecture.html).

---

## Requirements

Before using the package, you need:

- **Python 3.10 or later**
- a **NASA Earthdata Login** account
- a **Google Earth Engine** account
- a **Google Cloud project** configured for Earth Engine access
- an active internet connection

PIXC processing operates on high-resolution pixel-cloud products and can require substantially more memory, network transfer, disk activity, and processing time than LakeSP processing.

For account creation and external-service setup, see the [Installation Guide](https://swot-reservoir-wse.readthedocs.io/en/latest/installation.html).

---

## Installation

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

Upgrade `pip` and install the package:

```bash
python -m pip install --upgrade pip
python -m pip install .
```

Verify the installation:

```bash
swot-reservoir-wse --help
```

For the complete installation procedure, including Google Earth Engine and NASA Earthdata account setup, see the [Installation Guide](https://swot-reservoir-wse.readthedocs.io/en/latest/installation.html).

---

## Authentication

The package uses two authenticated external services:

| Service | Purpose |
| --- | --- |
| **Google Earth Engine** | JRC Global Surface Water access and reservoir-footprint generation |
| **NASA Earthdata** | SWOT LakeSP and PIXC product discovery and access |

Configure both with:

```bash
swot-reservoir-wse auth
```

During the initial Earth Engine setup, the package may request the **Google Cloud Project ID** associated with Earth Engine access.

During the initial Earthdata setup, the package may request your **Earthdata Login username and password**.

Existing valid credentials are reused when available.

Authentication can also be managed separately:

```bash
swot-reservoir-wse auth --earth-engine-only
swot-reservoir-wse auth --earthdata-only
```

For reauthentication, credential removal, storage locations, and all authentication options, see [Authentication](https://swot-reservoir-wse.readthedocs.io/en/latest/authentication.html).

---

## Quick Start

The general extraction command is:

```bash
swot-reservoir-wse extract --lat <latitude> --lon <longitude> --start-date YYYY-MM-DD --end-date YYYY-MM-DD --source <source>
```

where:

```text
<source> = lakesp | pixc
```

### LakeSP

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

### PIXC

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
```

The supplied latitude and longitude identify the **dam location**. The package first derives the corresponding reservoir footprint and then uses that footprint throughout the selected SWOT processing pipeline.

For a complete walkthrough, see [Usage](https://swot-reservoir-wse.readthedocs.io/en/latest/usage.html).

---

## LakeSP and PIXC

The two supported sources ultimately produce reservoir WSE time series but operate on fundamentally different SWOT observation representations.

| | LakeSP | PIXC |
| --- | --- | --- |
| SWOT product | Lake Single Pass Observation Vector | High Rate Pixel Cloud |
| Observation representation | Vectorized lake observations | Geolocated pixel-cloud measurements |
| Reservoir association | Spatially intersecting lake observations and `lake_id` | Pixel location relative to reservoir footprint |
| Quality processing | LakeSP partial and quality information | PIXC classification and classification-quality information |
| Reservoir WSE | Obtained from retained LakeSP observations | Derived from retained pixel measurements |
| Persistent product cache | Yes | No |
| Processing requirement | Generally lower | Generally higher |

For the complete processing stages and their scientific roles, see [Package Architecture](https://swot-reservoir-wse.readthedocs.io/en/latest/architecture.html).

---

## Outputs

Every successful extraction generates a source-specific **CSV time series**.

With plot generation enabled, a **PNG visualization** is generated alongside it.

Example LakeSP outputs:

```text
outputs/
├── 19.69000_73.34000_lakesp_wse.csv
└── 19.69000_73.34000_lakesp_wse.png
```

Example PIXC outputs:

```text
outputs/
├── 19.69000_73.34000_pixc_wse.csv
└── 19.69000_73.34000_pixc_wse.png
```

LakeSP output includes the representative daily WSE and aggregated quality status.

PIXC output includes the representative reservoir WSE together with statistics describing the accepted pixel population.

For complete column definitions, quality-status interpretation, and visualization behaviour, see [Outputs](https://swot-reservoir-wse.readthedocs.io/en/latest/outputs.html).

---

## Configuration

Runtime behaviour is controlled through `config.json`.

Display the active configuration:

```bash
swot-reservoir-wse config show
```

Change a parameter:

```bash
swot-reservoir-wse config set <key> <value>
```

For example:

```bash
swot-reservoir-wse config set max_workers 4
```

Source-specific settings use dotted keys:

```bash
swot-reservoir-wse config set sources.lakesp.mad_threshold 2.5
swot-reservoir-wse config set sources.pixc.mad_threshold 2.5
```

Restore the package defaults:

```bash
swot-reservoir-wse config reset
```

Configuration controls:

```text
reservoir footprint generation
SWOT product discovery
science-cycle selection
LakeSP quality screening
PIXC pixel selection
temporal MAD filtering
parallel execution
persistent caching
temporary storage
output generation
```

See [Configuration](https://swot-reservoir-wse.readthedocs.io/en/latest/configuration.html) for every parameter, default value, valid range, and processing effect.

---

## Cache

The package maintains persistent caches for:

```text
Reservoir polygons
Downloaded LakeSP granules
```

Inspect the cache:

```bash
swot-reservoir-wse cache
```

Clear generated reservoir polygons:

```bash
swot-reservoir-wse cache --clear-polygons
```

Clear cached LakeSP granules:

```bash
swot-reservoir-wse cache --clear-lakesp
```

Clear all persistent package caches:

```bash
swot-reservoir-wse cache --clear-all
```

PIXC products are processed through temporary workspaces and are not currently retained in a persistent PIXC granule cache.

---

## Command-Line Interface

The package exposes four primary command groups:

| Command | Purpose |
| --- | --- |
| `extract` | Generate a reservoir-specific WSE time series |
| `auth` | Manage Google Earth Engine and NASA Earthdata authentication |
| `config` | Inspect, modify, or reset runtime configuration |
| `cache` | Inspect or clear persistent package caches |

Display the CLI:

```bash
swot-reservoir-wse --help
```

or inspect an individual command:

```bash
swot-reservoir-wse extract --help
swot-reservoir-wse auth --help
swot-reservoir-wse config --help
swot-reservoir-wse cache --help
```

For every command, argument, and option, see the [Command Reference](https://swot-reservoir-wse.readthedocs.io/en/latest/command_reference.html).

---

## Documentation

Full documentation is maintained on **Read the Docs**:

[**swot-reservoir-wse.readthedocs.io**](https://swot-reservoir-wse.readthedocs.io/)

| Documentation | Description |
| --- | --- |
| [Introduction](https://swot-reservoir-wse.readthedocs.io/en/latest/introduction.html) | Scientific background, SWOT products, and motivation |
| [Installation](https://swot-reservoir-wse.readthedocs.io/en/latest/installation.html) | Installation and external-service setup |
| [Authentication](https://swot-reservoir-wse.readthedocs.io/en/latest/authentication.html) | Earth Engine and Earthdata authentication |
| [Usage](https://swot-reservoir-wse.readthedocs.io/en/latest/usage.html) | Practical extraction workflow |
| [Configuration](https://swot-reservoir-wse.readthedocs.io/en/latest/configuration.html) | Runtime configuration and processing parameters |
| [Command Reference](https://swot-reservoir-wse.readthedocs.io/en/latest/command_reference.html) | Complete CLI reference |
| [Package Architecture](https://swot-reservoir-wse.readthedocs.io/en/latest/architecture.html) | LakeSP and PIXC processing architecture |
| [Outputs](https://swot-reservoir-wse.readthedocs.io/en/latest/outputs.html) | CSV schemas and generated visualizations |

The documentation source is maintained in the `docs/` directory of this repository.

---

## Project Structure

```text
swot-reservoir-wse/
│
├── docs/                   # Read the Docs documentation
├── swot_reservoir_wse/     # Python package
├── config.example.json     # Example runtime configuration
├── pyproject.toml          # Package metadata and dependencies
├── CONTRIBUTING.md         # Contribution guidelines
├── LICENSE                 # Project license
└── README.md
```

Runtime directories such as `cache/`, `downloads/`, and `outputs/` are created separately from the source package as required.

---

## Contributing

Bug reports, documentation improvements, processing enhancements, and contributions extending the package are welcome.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and development guidelines.

---

## License

**swot-reservoir-wse** is distributed under the **MIT License**.

See [LICENSE](LICENSE) for the complete license text.
