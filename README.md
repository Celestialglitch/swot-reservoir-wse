## Overview

swot-reservoir-wse is a Python package for generating reservoir-specific Water Surface Elevation (WSE) time series from the Surface Water and Ocean Topography (SWOT) Level-2 Lake Single Pass (LakeSP) Vector Data Product (Version D) using user-supplied dam coordinates along with a user-defined date range.

---
## Background

Please check out the complete project introduction in [intro to swot-reservoir-wse](docs/introduction.md).

---
## Features

* Reservoir WSE time-series extraction from SWOT LakeSP observations using only reservoir coordinates and a date range.
* Automated processing pipeline that performs footprint generation, granule discovery, polygon intersection, observation extraction, quality filtering, and time-series generation with a single command.
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

Before running **swot-reservoir-wse** for the first time, the users must configure the external services used by the package.

The package requires consistent access to two external platforms:

- **Google Earth Engine** to extract the reservoir footprint from the JRC Global Surface Water dataset.
- **NASA Earthdata** to discover and download SWOT LakeSP products.

The users are requested to follow the steps mentioned below . These steps only need to be completed once.
> **Note**
>
> For your convenience, please copy the links and open them in different windows of your web browser.

---

### 1. Create a NASA Earthdata Account

1. Create a NASA Earthdata account at https://urs.earthdata.nasa.gov/
2. After creating your account, sign-in once through the Earthdata website to activate the account and accept any required terms of use.

This account is required to search for and download SWOT LakeSP products from NASA Earthdata.

Keep your Earthdata username and password available, as they will be requested during the first execution of the package.

---

### 2. Register for Google Earth Engine

Register for Google Earth Engine using your Google account at https://code.earthengine.google.com/

1. Click on Start Free to get free credits to continue (for new users).
2. Fill in your contact details (you can choose organisation/individual based on your convenience ).
3. Add a suitable payment method for payment verification.

If your registration is still pending, the package will not be able to extract reservoir footprints.

> **Important**
>
> Use the same Google account throughout the remaining setup steps, including Google Cloud.

---

### 3. Create a Google Cloud Project

Open the Google Cloud Console at https://console.cloud.google.com/

1. Click on My First Project and then click on Select project.
2. Create your project and then open the project dashboard.
3. Select your project dispaly name and copy the **Project ID** displayed on the dashboard.

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


This authorizes Earth Engine to use your Google Cloud project for API requests.

### 6. Grant yourself permission to use Google Cloud project
For the final step, your Google account must be granted permission to consume Google APIs from that project.
1. Open your Google Cloud project at https://console.cloud.google.com/ (make sure you are logged in with your project).
2. Open IAM & Admin under Quick access and select IAM option. Then click on Grant Access option.
3. Type your gmail in New Principals section and select your account in gmail:user_name option as autochoice with a tick.
4. Click on 'Select a role' under Assign Roles section and select Access Approval followed by Access Approval Editor.

After changing permissions, please wait a few minutes for Google Cloud IAM permissions to update the policy.

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

Verify the installation.

```bash
swot-wse --help
```

If the installation was successful, the command above will display the available command-line options.

---

## Initialisation

During the first execution of **swot-reservoir-wse**, the package will request your Google Cloud **Project ID**  
Example

```
Enter your Google Earth Engine Project ID:
```
Once you fill in your **Project ID**  you will be authenticated for the required services as below.

### Google Earth Engine

If Earth Engine has not been authenticated previously, a browser window will open asking you to authorize Earth Engine.

After successful authentication, you will see the following in that window:
```
Google Earth Engine authorization successful!

Credentials have been retrieved. Please close this window.
```
Afterwards, the credentials are stored locally and future executions will not require re-authentication unless the credentials are removed or expire.
```
Successfully saved authorization token.
```

---

### NASA Earthdata

Before downloading SWOT LakeSP products, the package will request your NASA Earthdata credentials.

Example

```
Enter your Earthdata username:
Enter your Earthdata password:
```

After successful authentication, the package will begin searching and downloading the required SWOT products automatically.

## Usage

The software package currently supports one major CLI command only.

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

The package generates output in 2 formats

- Water Surface Elevation time series (`CSV`)
  <img width="337" height="370" alt="image" src="https://github.com/user-attachments/assets/dd5395a9-faa9-49ca-b173-da9613e780dd" />


- Water Surface Elevation plot (`PNG`)
  <img width="3000" height="1500" alt="19 69000_73 34000_wse" src="https://github.com/user-attachments/assets/dc4afe5d-c953-4d67-a82f-1abc4d150d31" />



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

Observations were found but did not survive after the filtering criteria is applied.

---

## License

This project is licensed under the MIT License.
