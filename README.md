# swot-wse

A Python package for extracting reservoir **Water Surface Elevation (WSE)** time series from the **Surface Water and Ocean Topography (SWOT)** Level-2 Lake Single Pass (LakeSP) Vector Data Product (Version D).

Given the latitude and longitude of a reservoir together with a user-specified date range, the package automatically identifies the reservoir footprint, retrieves relevant SWOT observations, extracts Water Surface Elevation measurements, performs quality filtering and generates a final time series .

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

## Why Use swot-reservoir-wse

Extraction of reservoir Water Surface Elevation (WSE) time series from SWOT LakeSP observations , for given dam coordinates typically requires multiple independent processing steps, including reservoir footprint generation with Google Earth Engine, SWOT LakeSP granule discovery through NASA Earthdata, spatial intersection between the reservoir footprint and LakeSP polygons, Water Surface Elevation extraction, quality filtering, and time-series generation.

swot-wse combines these steps into a single reproducible workflow to generate reservoir WSE time series from a single command instead of manually processing multiple datasets and software tools.

## Requirements

Before running the package, ensure you have:

- Python 3.10 or newer
- A NASA Earthdata user account
- Access to Google Earth Engine
- A Google Cloud project with the Earth Engine API enabled
---

### Creating the required accounts

- NASA Earthdata: https://urs.earthdata.nasa.gov
- Google Earth Engine: https://code.earthengine.google.com/
- Google Cloud Console: https://console.cloud.google.com/

---

## Installation

Clone the repository.

```bash
git clone https://github.com/Celestialglitch/swot-reservoir-wse.git
cd swot-reservoir-wse
```

Install the package.

```bash
pip install -e .
```

---

## Authentication

The package uses two independent services.

### Google Earth Engine

Google Earth Engine is used to generate the reservoir footprint from the JRC Global Surface Water dataset.

During execution, you will be prompted to provide your Google Earth Engine Cloud Project ID if it has not already been configured.

### NASA Earthdata

NASA Earthdata authentication is required to search and download SWOT LakeSP products.

During execution, you will be prompted for your NASA Earthdata credentials if authentication has not already been established.

---

## Quick Start

Run the command below.

```bash
swot-wse polygon --lat <latitude> --lon <longitude> --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

Example

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16
```

Dates must be provided in the `YYYY-MM-DD` format.

---

## Workflow

The package performs the following operations automatically:

1. Generate (or load from cache) the reservoir footprint using the JRC Global Surface Water dataset.
2. Search NASA Earthdata for SWOT Level-2 LakeSP granules within the specified date range.
3. Identify SWOT observations intersecting the extracted reservoir footprint.
4. Extract Water Surface Elevation observations.
5. Apply the built-in filtering workflow.
6. Generate a Water Surface Elevation time series.
7. Save the results as a CSV file and a plot.

---

## Output

The package produces:

* Water Surface Elevation time-series (CSV)
* Water Surface Elevation plot (PNG)

Outputs are stored under

```
~/Documents/swot_wse/data/outputs/
```

Example

```
19.69000_73.34000_wse.csv
19.69000_73.34000_wse.png
```

---

## Cache

To improve performance, the package automatically caches intermediate products, including:

* Extracted reservoir footprints
* Downloaded SWOT LakeSP granules

Cached files are stored under

```
~/Documents/swot_wse/cache/
```

---

## Project Structure

```text
swot_wse/
├── cache/
│   └── polygon_cache.py
├── filtering/
│   └── stages.py
├── geometry/
│   └── reservoir_extractor.py
├── lakesp/
│   ├── search.py
│   ├── discovery.py
│   └── extract.py
├── cli.py
├── config.py
├── earth_engine.py
├── outputs.py
├── pipeline.py
└── __init__.py
```


---

## License

This project is licensed under the MIT License.
