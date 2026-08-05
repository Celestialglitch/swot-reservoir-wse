## Overview

swot-reservoir-wse is a Python package for generating reservoir-specific Water Surface Elevation (WSE) time series from Surface Water and Ocean Topography (SWOT) observations using user-supplied reservoir coordinates and a user-defined date range.

The package provides a configurable source architecture that enables different SWOT observation products to be processed through a common workflow. The current release supports the SWOT Level-2 Lake Single Pass (LakeSP) Vector Data Product (Version D).

---
## Background

Check out the background and motivation for this project in [intro to swot-reservoir-wse](docs/introduction.md).

---
## Features

* Reservoir-specific Water Surface Elevation (WSE) time-series extraction from configurable SWOT observation products.
* Modular source architecture supporting multiple SWOT-derived observation products through a common processing interface.
* Automated processing pipeline that performs reservoir footprint extraction, granule discovery, spatial verification, observation extraction, quality filtering, and time-series generation using a single command.
* Integrated workflow combining Google Earth Engine and NASA Earthdata.
* Command-line interface designed for reproducible and scriptable workflows.
* Configurable built-in caching of reservoir footprints and downloaded LakeSP granules to reduce repeated processing and improve execution speed.
* Parallel processing for accelerated extraction from multiple SWOT granules

---
## Requirements

Before installing and running **swot-reservoir-wse**, ensure that the following requirements are available:

* Python 3.10 or better
* A NASA Earthdata account
* A Google Earth Engine account
* A Google Cloud project registered for Earth Engine API access
* An active internet connection for reservoir-footprint extraction and SWOT product discovery
* Sufficient local disk space for downloaded SWOT products and generated cache files

The package installs its required Python dependencies automatically through `pip`.

---


## Initial Setup

Before using **swot-reservoir-wse** for the first time, the required external services must be configured.

The package relies on two external platforms:

* **Google Earth Engine** for reservoir footprint extraction from the JRC Global Surface Water dataset.
* **NASA Earthdata** for discovering and downloading SWOT observation products.


The users are requested to follow the steps mentioned below . These steps only need to be completed once.
> **Note**
>
> For your convenience, please copy the links and open them in different windows of your web browser.

---

### 1. Create a NASA Earthdata Account

1. Create a NASA Earthdata account at https://urs.earthdata.nasa.gov/
2. After creating your account, sign-in once through the Earthdata website to activate the account and accept any required terms of use.

This account is required to search for and download granules from required SWOT science products from NASA Earthdata.

Keep your Earthdata username and password available, as they will be requested during the first execution of the package.

---

### 2. Register for Google Earth Engine

Register for Google Earth Engine using your Google account at https://code.earthengine.google.com/

1. Follow the registration process and complete the required account verification .
2. Fill in your contact details (you can choose organisation/individual based on your convenience ).
3. Add a suitable payment method for payment verification (if applicable).

If your registration is still pending, the package will not be able to extract reservoir footprints.

> **Important**
>
> Use the same Google account throughout the remaining setup steps, including Google Cloud.

---

### 3. Create a Google Cloud Project

Open the Google Cloud Console at https://console.cloud.google.com/

1. Click on My First Project and then click on Select project.
2. Create your project and then open the project dashboard.
3. Select your project display name and copy the **Project ID** displayed on the dashboard.

Do **not** copy the project display name or the project number.

The package will request this Project ID during the first execution.

---

### 4. Enable the Earth Engine API

Within the Google Cloud project created in the previous step:

1. Open **APIs & Services** under Quick Access section.
2. Select **API Library**.
3. Search for **Google Earth Engine API**.
4. Open the Earth Engine API page.
5. Click **Enable**.

The package cannot communicate with Google Earth Engine unless this API is enabled.

---

### 5. Associate the Google Cloud Project with Earth Engine

1. Open the Google Earth Engine Code Editor at https://code.earthengine.google.com/
2. Sign in using the same Google account used to create the Google Cloud project.
3. Click on "Select an existing cloud project" and then choose your existing project (Step 3).
4. In the configuration, click on 'See if you are eligible for non-commercial use' and click on Get Started.
5. Register with appropriate details. New registrations may require approval.
6. Choose Community quota tier (for non-billing account).
7. Finish all the checkboxes and click on Register.


This authorizes your Google Cloud project for Earth Engine API requests.

---


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
This installs swot-reservoir-wse together with all required Python dependencies specified by the package.

Verify the installation.

```bash
swot-wse --help
```
> **Note**
>
> If the installation was successful, the command above will display the available command-line options.

```bash
polygon    Extract reservoir Water Surface Elevation time series
auth       Configure Google Earth Engine authentication
config     View or modify package configuration
cache      Inspect or manage cached files
```
---

## Initialisation

Before using **swot-reservoir-wse**, Google Earth Engine must be configured for the package.

Run

```bash
swot-wse auth
```

The package will prompt for your Google Earth Engine **Project ID**.

Example

```
Google Earth Engine project ID:
```

If Google Earth Engine has not been authenticated previously on your system, a browser window will open requesting authorization. After successful authentication, the selected Project ID is saved in the package configuration, while the credentials are securely managed by the Google Earth Engine API. Unless the credentials are removed or expire, future executions will not require re-authentication.

---

### NASA Earthdata

When SWOT observation products are required for the first time, the package will automatically initiate NASA Earthdata authentication.

Depending on your existing Earthdata login status, you may be prompted to sign in using your NASA Earthdata account. 

## Usage

The package provides a command-line interface (CLI) for reservoir Water Surface Elevation (WSE) extraction, Google Earth Engine authentication, package configuration, and cache management.

Display the available commands at any time using

```bash
swot-wse --help
```

---

### Authenticate Google Earth Engine

Before using the package for the first time, authenticate Google Earth Engine and save the associated Project ID.

```bash
swot-wse auth
```

---

### Generate a Reservoir Water Surface Elevation Time Series

Generate a reservoir-specific Water Surface Elevation (WSE) time series using

```bash
swot-wse polygon \
    --lat <latitude> \
    --lon <longitude> \
    --start-date YYYY-MM-DD \
    --end-date YYYY-MM-DD \
    [--source <source>]
```

Example

```bash
swot-wse polygon \
    --lat 19.690 \
    --lon 73.340 \
    --start-date 2026-01-20 \
    --end-date 2026-07-16
```

The optional `--source` argument specifies the SWOT observation source to use. By default, the package uses `auto`, which automatically selects the most appropriate supported source. In the current release, `auto` resolves to the SWOT Level-2 LakeSP Vector Data Product.

---

### View Current Configuration

```bash
swot-wse config show
```

---

### Modify Package Configuration

```bash
swot-wse config set <parameter> <value>
```

---

### Restore Default Configuration

```bash
swot-wse config reset
```

---

### Inspect Cache

```bash
swot-wse cache
```

---

### Clear Cached Reservoir Polygons

```bash
swot-wse cache --clear-polygons
```

---

### Clear Cached LakeSP Products

```bash
swot-wse cache --clear-lakesp
```

---

### Clear All Cached Data

```bash
swot-wse cache --clear-all
```

---

## Configuration

Most processing parameters can be modified without changing the source code.

Display the current configuration at any time using

```bash
swot-wse config show
```

### General Configuration

| Parameter               | Default           | Description                                                                                |
| ----------------------- | ----------------- | ------------------------------------------------------------------------------------------ |
| `earth_engine_project`  | `null`            | Google Earth Engine Project ID.                                                            |
| `search_radius_m`       | `50000`           | Search radius (metres) used during reservoir footprint extraction.                         |
| `pekel_threshold`       | `20`              | Minimum JRC Global Surface Water occurrence (%) used to delineate the reservoir footprint. |
| `working_crs`           | `auto`            | Projected CRS used for area and distance calculations.                                     |
| `max_workers`           | CPU Count − 1     | Maximum number of parallel worker threads.                                                 |
| `generate_plot`         | `true`            | Generate a PNG plot of the extracted WSE time series.                                      |
| `polygon_cache_enabled` | `true`            | Enable caching of extracted reservoir polygons.                                            |
| `lakesp_cache_enabled`  | `true`            | Enable caching of downloaded LakeSP granules.                                              |
| `cache_dir`             | `cache/`          | Directory used to store cached files.                                                      |
| `output_dir`            | `outputs/`        | Directory used to store generated outputs.                                                 |
| `temp_download_dir`     | `downloads/temp/` | Temporary workspace used while processing downloaded files.                                |


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

The package generates output in 2 formats

- Water Surface Elevation time series (`CSV`)
  
  <img width="337" height="370" alt="image" src="https://github.com/user-attachments/assets/dd5395a9-faa9-49ca-b173-da9613e780dd" />


- Water Surface Elevation plot (`PNG`)
  
  <img width="3000" height="1500" alt="19 69000_73 34000_wse" src="https://github.com/user-attachments/assets/dc4afe5d-c953-4d67-a82f-1abc4d150d31" />



Outputs are written to

```
/Documents/swot_wse/data/outputs/
```

---

## Cache

The package stores reservoir footprints and downloaded SWOT LakeSP granules on disk , in the form of cache , to avoid repeated downloads and reduce execution time.

The cache location in current setup is :

```
/Documents/swot_wse/cache/
```
> **Important**
>
> The cache is stored on disk and does not increase RAM usage during execution.

Reservoir footprint files occupy very little disk space and are generally negligible.

Downloaded SWOT LakeSP granules require more storage and remain in the cache for reuse in future executions. 

The package does not automatically delete cached files. 

Users may delete the cache directory at any time to clear disk space as any missing files will simply be downloaded or regenerated again when required.

> **Note**
>
> The future versions of this package will be more optimized in this regard.



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

Observations were found but did not survive after the filtering criteria is applied.

---

## Troubleshooting

### 1. Google Earth Engine permission error

If you receive an error similar to 
```
Caller does not have required permission to use project <PROJECT_ID>.
Grant the caller the roles/serviceusage.serviceUsageConsumer role...
```
your Google account does not have permission to use the selected Google Cloud project for Earth Engine API requests.
To resolve this, follow the below steps :
1. Open your Google Cloud project at https://console.cloud.google.com/ (make sure you are logged in with your project).
2. Open IAM & Admin under Quick access and select IAM option. Then click on Grant Access option.
3. Type your gmail in New Principals section and select your account in gmail:user_name option as autochoice with a tick.
4. Click on 'Select a role' under Assign Roles section and assign the Service Usage Consumer role to your Google account..

After changing permissions, please wait a few minutes for Google Cloud IAM permissions to update the policy.

### 2. Google Earth Engine authentication window issue

If authentication does not start automatically, run the following command :
```
earthengine authenticate --force
```
This will force open the authentication window.

## License

This project is licensed under the MIT License.
