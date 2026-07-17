# swot-wse

A Python package for extracting reservoir **Water Surface Elevation (WSE)** time series from the **Surface Water and Ocean Topography (SWOT)** Level-2 Lake Single Pass (LakeSP) Vector Data Product.

Given the latitude and longitude of a reservoir together with a user-specified date range, the package automatically identifies the reservoir footprint, retrieves relevant SWOT observations, extracts Water Surface Elevation measurements, and generates a filtered time series.

---

## Features

* Automatic reservoir footprint extraction from the **JRC Global Surface Water** dataset using Google Earth Engine.
* Automatic retrieval of SWOT Level-2 LakeSP observations through NASA Earthdata.
* Spatial filtering of SWOT granules intersecting the extracted reservoir footprint.
* Automatic extraction of Water Surface Elevation (WSE) observations.
* Generation of filtered WSE time-series CSV files and plots.
* Automatic caching of extracted reservoir footprints and downloaded LakeSP granules to avoid redundant processing.

---

## Requirements

Before running the package, ensure that you have:

* Python 3.10 or newer
* A NASA Earthdata account
* Access to Google Earth Engine
* A Google Earth Engine Cloud Project

---

## Installation

Clone the repository.

```bash
git clone https://github.com/Celestialglitch/Reservoir-WSE-finder.git
cd Reservoir-WSE-finder
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

```
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
└── ...
```

---

## License

This project is licensed under the MIT License.
