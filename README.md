## Overview

**swot-reservoir-wse** is a Python package for generating reservoir-specific Water Surface Elevation (WSE) time series from Surface Water and Ocean Topography (SWOT) observations using user-supplied dam coordinates and a user-defined date range.

The package is built around a configurable source architecture that enables different SWOT science products to be processed through a common workflow. The current release supports the SWOT Level-2 Lake Single Pass (LakeSP) Vector Data Product (Version D), while future releases will extend support to additional SWOT observation products without changing the user interface.

---
## Background

Check out the background and motivation for this project in [intro to swot-reservoir-wse](docs/introduction.md).

---

## Features

* Generates reservoir-specific Water Surface Elevation (WSE) time series from user-supplied dam coordinates and a specified date range.
* Automatically identifies the representative reservoir footprint from the user-supplied dam location and retrieves the required SWOT WSE observations.
* Provides an end-to-end processing workflow from reservoir identification to final WSE time-series generation through a single command.
* Supports multiple SWOT observation products through a configurable observation-source architecture.
* Produces clean CSV time series and graphical visualizations of extracted WSE observations.
* Includes a command-line interface (CLI) for reproducible and scriptable processing workflows.
* Allows processing behaviour, output locations, cache settings, and observation-source parameters to be customized through a centralized configuration system.
* Maintains reusable local caches to reduce repeated processing across successive executions.


---
## Requirements

Before installing and running **swot-reservoir-wse**, ensure that the following requirements are available:

* Python 3.10 or later
* A NASA Earthdata account
* A Google Earth Engine account
* A Google Cloud project registered for Earth Engine API access
* An active internet connection for reservoir footprint extraction and SWOT product discovery
* Sufficient local disk space for downloaded SWOT products and cached files

All required Python dependencies are installed automatically when the package is installed using `pip`.

---


## Initial Setup

Before using **swot-reservoir-wse** for the first time, the required external services must be configured.

The package relies on two external platforms:

* **Google Earth Engine** for reservoir footprint extraction from the JRC Global Surface Water dataset.
* **NASA Earthdata** for discovering and downloading SWOT observation products.


Follow the steps below before using the package for the first time. These steps only need to be completed once.
> **Note**
>
> For your convenience, please copy the links and open them in different windows of your web browser.

---

### 1. Create a NASA Earthdata Account

1. Create a NASA Earthdata account at https://urs.earthdata.nasa.gov/
2. After creating your account, sign-in once through the Earthdata website to activate the account and accept any required terms of use.

This account is required to discover and download granules from required SWOT science products from NASA Earthdata.

Keep your Earthdata username and password available, as they will be requested during the first execution of the package.

---

### 2. Register for Google Earth Engine

Register for Google Earth Engine using your Google account at https://code.earthengine.google.com/

1. Follow the registration process and complete the required account verification .
2. Complete the required registration details. You may register as an individual or as an organization, depending on your use case.
3. Complete any verification steps like payment verification requested during registration.

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

The package will request this Project ID during execution.

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


This associates your Google Cloud project with Google Earth Engine so it can be used by the package.

---


## Installation

If an earlier version of **swot-reservoir-wse** has already been installed, remove the old installation before installing the latest release.

```bash
python -m pip uninstall swot-wse -y
```

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

---

## Architecture

For an overview of the package design and internal processing architecture, see [Package Architecture](docs/architecture.md).

## Initialisation

Before generating a WSE time series, Google Earth Engine must be configured for the package.

Run

```bash
swot-wse auth
```

The package will prompt for your Google Earth Engine **Project ID**.

Example

```text
Google Earth Engine project ID:
```

If Google Earth Engine has not been authenticated previously on your system, a browser window will open requesting authorization.

Once authentication is complete:

- the selected Google Earth Engine Project ID is stored in the package configuration;
- authentication credentials are securely managed by the Google Earth Engine API; and
- future executions normally will not require re-authentication unless the credentials are removed or expire.

### NASA Earthdata

NASA Earthdata authentication is performed automatically when SWOT observation products are accessed for the first time.

Depending on your existing login status, you may be prompted to authenticate with your NASA Earthdata account before product discovery and download begins.

---

## Usage

The package currently provides four command groups.

| Command | Purpose |
|---------|---------|
| `polygon` | Generate reservoir-specific Water Surface Elevation (WSE) time series |
| `auth` | Configure Google Earth Engine authentication |
| `config` | View or modify package configuration |
| `cache` | Inspect or manage cached files |

Display all available commands using

```bash
swot-wse --help
```

### Generate a Reservoir WSE Time Series

```bash
swot-wse polygon --lat <latitude> --lon <longitude>  --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

Example

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16
```

By default, the package automatically selects the appropriate supported SWOT observation source. In the current release, `auto` resolves to **LakeSP**.

The package also provides commands for:

- configuring Google Earth Engine authentication
- viewing and modifying runtime configuration
- inspecting or managing cached files.

---

## Command Reference

A complete reference for every supported command, command-line option, configurable parameter, and usage example is available in [Command Reference](docs/command_reference.md).


---

## Processing Workflow

For each execution, **swot-reservoir-wse** performs the following workflow:

1. Generate a reservoir footprint from the user-supplied dam location.
2. Identify SWOT LakeSP granules available for the requested time period and spatial extent.
3. Associate LakeSP observations with the generated reservoir footprint.
4. Apply quality-control procedures to retain reliable observations.
5. Aggregate accepted observations to derive representative reservoir-level Water Surface Elevation (WSE) values.
6. Construct the final reservoir-specific WSE time series.
7. Export the generated outputs.

---

## Output

The package currently generates two output files for each processed reservoir.

### Water Surface Elevation Time Series (`CSV`)

<img width="337" height="370" alt="image" src="https://github.com/user-attachments/assets/dd5395a9-faa9-49ca-b173-da9613e780dd" />

### Water Surface Elevation Plot (`PNG`)

<img width="3000" height="1500" alt="19.69000_73.34000_wse" src="https://github.com/user-attachments/assets/dc4afe5d-c953-4d67-a82f-1abc4d150d31" />

By default, outputs are written to the package's configured output directory.

The output location can be viewed or modified using the configuration system.

For more details check out [Command Reference](docs/command_reference.md).


---

## Cache

To reduce repeated processing and unnecessary downloads, the package maintains a local cache.

The current release supports two independent cache types.

| Cache | Purpose |
|--------|---------|
| Reservoir Polygon Cache | Stores extracted reservoir footprints. |
| LakeSP Granule Cache | Stores downloaded LakeSP products for future reuse. |

Both cache types can be enabled or disabled independently through the package configuration.

By default, cached files are retained between executions and are reused whenever possible.

Cached data may be removed at any time using the built-in cache management commands or by deleting the configured cache directory. Missing files are regenerated or downloaded automatically when required.

For cache management commands and cache configuration options, see the [Command Reference](docs/command_reference.md).


---

## Possible Messages

Some messages indicate that no usable observations were found rather than an installation or configuration problem.

### No reservoir polygon found

```
No reservoir polygon found at lat=<latitude>, lon=<longitude>.
```

The supplied coordinates do not intersect a detectable reservoir footprint.

---

### No observation products found

```
No LakeSP granules found.
```

No observation products were available for the requested location and time period.

---

### No spatial intersections found

```
No LakeSP intersections found.
```

Observation products were found, but none intersected the extracted reservoir footprint.

---

### No observations after filtering

```
No observations remained after filtering.
```

Observations were extracted successfully but were removed by the configured quality-control procedure.

## Troubleshooting

### 1. Google Earth Engine permission error

If you receive an error similar to 
```
Caller does not have required permission to use project <PROJECT_ID>.
Grant the caller the roles/serviceusage.serviceUsageConsumer role...
```
your Google account does not have permission to use the selected Google Cloud project for Earth Engine API requests.
To resolve this :
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
