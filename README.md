## Overview

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
## Requirements

Before installing the package, please ensure that the following requirements are met.

- Python version 3.10 or later
- A NASA Earthdata account
- A Google Earth Engine account
- A Google Cloud project with the Earth Engine API enabled
---

## Initial Setup

Before running the package for the first time, configure the external services used during SWOT LakeSP data discovery and reservoir polygon extraction.

The package uses

- Google Earth Engine to extract the reservoir polygon footprint from the JRC Global Surface Water dataset.
- NASA Earthdata to search for and download SWOT LakeSP products.


### 1. Register for Google Earth Engine

Register for Google Earth Engine using your Google account at https://code.earthengine.google.com/

Your account must be approved before the package can access the Earth Engine API.

If your registration is still pending, the package will not be able to extract reservoir footprints.

---

### 2. Create a NASA Earthdata Account

Create a free NASA Earthdata account at https://urs.earthdata.nasa.gov

This account is required to search for and download SWOT LakeSP products from NASA Earthdata.

Keep your Earthdata username and password available, as they will be requested during the first execution of the package.

---

### 3. Create a Google Cloud Project

1. Open

https://console.cloud.google.com/

2. Create a new Google Cloud project, or select an existing project that you own.

3. After the project has been created, open the project dashboard.

4. Copy the **Project ID** shown on the dashboard.

The package will request this Project ID during the first execution.

---

### 4. Enable the Earth Engine API

Open the Google Cloud Console for the project created in the previous step.

Navigate to **APIs & Services**, open the **Library**, search for **Earth Engine API**, and enable the API for the selected project.

The package cannot communicate with Google Earth Engine unless this API is enabled.

## Installation

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

## First Run

During the first execution, the package will ask for your Google Cloud Project ID.

Example

```
Enter your Google Earth Engine project ID:
```

If Earth Engine has not been authenticated previously, a browser window will open asking you to authorize Earth Engine.

The package will also request your NASA Earthdata login before downloading SWOT LakeSP products.

These authentication steps usually need to be completed only once.

---

## Usage

Run

```bash
swot-wse polygon --lat <latitude> --lon <longitude> --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

Example

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16
```

Dates must be supplied in the format

```
YYYY-MM-DD
```

---

## Command Line Arguments

| Argument | Description |
|-----------|-------------|
| `--lat` | Reservoir latitude |
| `--lon` | Reservoir longitude |
| `--start-date` | Beginning of the search period |
| `--end-date` | End of the search period |

---

## Processing Workflow

For every execution, the package performs the following steps.

1. Generate (or load) the reservoir footprint.
2. Search NASA Earthdata for SWOT LakeSP granules.
3. Identify granules intersecting the reservoir.
4. Download missing LakeSP products.
5. Extract Water Surface Elevation observations.
6. Apply the built-in filtering workflow.
7. Save the final Water Surface Elevation time series.

---

## Output

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

## Cache

To reduce repeated processing, the package automatically stores

- reservoir footprints
- downloaded SWOT LakeSP products

Cache location

```
~/Documents/swot_wse/cache/
```

---

## Possible Messages

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

## License

This project is licensed under the MIT License.
