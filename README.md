# swot-reservoir-wse

swot-reservoir-wse is a Python package for generating reservoir-specific Water Surface Elevation (WSE) time series from the Surface Water and Ocean Topography (SWOT) Level-2 Lake Single Pass (LakeSP) Vector Data Product (Version D) using user-supplied dam coordinates along with a user-defined date range.

---

## Features

* Reservoir WSE time-series extraction from SWOT LakeSP observations using only reservoir coordinates and a date range.
* Automated processing pipeline that performs footprint generation, granule discovery, observation extraction, quality filtering, and time-series generation with a single command.
* Integrated Earth observation workflow combining Google Earth Engine for reservoir footprint generation and NASA Earthdata for SWOT LakeSP discovery and retrieval.
* Command-line interface (CLI) designed for reproducible and scriptable workflows.
* Built-in caching of reservoir footprints and downloaded LakeSP products to reduce repeated processing and improve execution speed.
* Automatic caching of extracted reservoir footprints and downloaded LakeSP granules to avoid redundant processing.
* Parallel data processing to accelerate extraction from multiple SWOT LakeSP granules.

---
# Requirements

Before using the package, you will need

- Python 3.10 or newer
- A NASA Earthdata account
- Access to Google Earth Engine
- A Google Cloud Project with the Earth Engine API enabled

---

# Initial Setup

The package uses two external services.

## 1. Create a NASA Earthdata account

Create a free NASA Earthdata account.

https://urs.earthdata.nasa.gov

This account is used to search and download SWOT LakeSP products.

---

## 2. Register for Google Earth Engine

Sign in using your Google account.

https://code.earthengine.google.com/

Your account must be approved before you can use the Earth Engine API.

---

## 3. Create a Google Cloud Project

Open Google Cloud Console.

https://console.cloud.google.com/

Create a new project (or use an existing one).

Copy the **Project ID**. The package will ask for this value during the first run.

---

## 4. Enable the Earth Engine API

Inside Google Cloud Console

APIs & Services

→ Library

→ Search for

```
Earth Engine API
```

Enable the API for your Cloud Project.

---

# Installation

Clone the repository.

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

Upgrade pip.

```bash
python -m pip install --upgrade pip
```

Install the package.

```bash
python -m pip install .
```

Verify the installation.

```bash
swot-wse --help
```

If the installation was successful, the command above will display the available command-line options.

---

# First Run

During the first execution, the package will ask for your Google Cloud Project ID.

Example

```
Enter your Google Earth Engine project ID:
```

If Earth Engine has not been authenticated previously, a browser window will open asking you to authorize Earth Engine.

The package will also request your NASA Earthdata login before downloading SWOT LakeSP products.

These authentication steps usually need to be completed only once.

---

# Usage

Run

```bash
swot-wse polygon \
    --lat <latitude> \
    --lon <longitude> \
    --start-date YYYY-MM-DD \
    --end-date YYYY-MM-DD
```

Example

```bash
swot-wse polygon \
    --lat 19.690 \
    --lon 73.340 \
    --start-date 2026-01-20 \
    --end-date 2026-07-16
```

Dates must be supplied in the format

```
YYYY-MM-DD
```

---

# Command Line Arguments

| Argument | Description |
|-----------|-------------|
| `--lat` | Reservoir latitude |
| `--lon` | Reservoir longitude |
| `--start-date` | Beginning of the search period |
| `--end-date` | End of the search period |

---

# Processing Workflow

For every execution, the package performs the following steps.

1. Generate (or load) the reservoir footprint.
2. Search NASA Earthdata for SWOT LakeSP granules.
3. Identify granules intersecting the reservoir.
4. Download missing LakeSP products.
5. Extract Water Surface Elevation observations.
6. Apply the built-in filtering workflow.
7. Save the final Water Surface Elevation time series.

---

# Output

The package generates

- Water Surface Elevation time series (`CSV`)
- Water Surface Elevation plot (`PNG`)

Example

```
19.69000_73.34000_wse.csv
19.69000_73.34000_wse.png
```

Outputs are written to

```
~/Documents/swot_wse/data/outputs/
```

---

# Cache

To reduce repeated processing, the package automatically stores

- reservoir footprints
- downloaded SWOT LakeSP products

Cache location

```
~/Documents/swot_wse/cache/
```

---

# Possible Messages

Some messages indicate that no valid observations were found rather than an installation problem.

For example

```
No reservoir polygon could be extracted.
```

The supplied coordinates do not intersect a detectable reservoir footprint.

```
No LakeSP granules found.
```

No SWOT observations were available within the requested date range.

```
No LakeSP intersections found.
```

The available SWOT granules did not intersect the extracted reservoir footprint.

```
No observations remained after filtering.
```

Observations were found but did not satisfy the filtering criteria.

---

# Project Structure

```text
swot_wse/
├── cache/
├── filtering/
├── geometry/
├── lakesp/
├── cli.py
├── config.py
├── earth_engine.py
├── outputs.py
├── pipeline.py
└── __init__.py
```

---

# License

This project is licensed under the MIT License.
