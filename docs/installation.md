# Installation

This page describes how to install **swot-reservoir-wse** and prepare the external services required for reservoir WSE processing.

The package requires:

- Python 3.10 or later
- NASA Earthdata Login
- Google Earth Engine access; and
- a Google Cloud project configured for Earth Engine.

## External Service Setup

Before installing and running **swot-reservoir-wse**, create the accounts required to access Google Earth Engine and NASA Earthdata.

### NASA Earthdata Login

SWOT products are discovered and downloaded through NASA Earthdata.

Create an account at:

https://urs.earthdata.nasa.gov/

After creating the account:

1. Sign in through the Earthdata website
2. Complete any account-verification steps
3. Accept any terms of use presented by Earthdata.

The username and password will later be used when authenticating **swot-reservoir-wse**.

You do not need to place Earthdata credentials inside the repository or config.json.

**swot-reservoir-wse** stores validated Earthdata credentials in the user's standard netrc credential file.

### Google Earth Engine

Register for Google Earth Engine at:

https://code.earthengine.google.com/

Use the Google account that will also have access to the Google Cloud project used by **swot-reservoir-wse**.

Complete the Earth Engine registration and any verification requested by Google.

Earth Engine access must be active before reservoir footprints can be generated.

### Google Cloud Project

Open the Google Cloud Console:

https://console.cloud.google.com/

Create a new project or select an existing project that will be used with Google Earth Engine.

Locate and copy the:

    Project ID

For example, if the console displays:

    Project name   : Reservoir Analysis
    Project ID     : reservoir-analysis-123
    Project number : 123456789

the value required by **swot-reservoir-wse** is:

    reservoir-analysis-123

### Enable the Google Earth Engine API

Inside the selected Google Cloud project:

1. Open **APIs & Services**
2. Open the **API Library**
3. Search for **Google Earth Engine API**
4. Open the API page
5. Enable the API for the project.

The project cannot be used by the Earth Engine API until this step is complete.

### Register the Cloud Project for Earth Engine

Open the Earth Engine interface:

https://code.earthengine.google.com/

Sign in using the Google account associated with the Cloud project.

Select or register the Google Cloud project for Earth Engine use and complete the registration process shown by Google.

For non-commercial use, choose the appropriate non-commercial registration and quota options where applicable.

The Earth Engine registration interface can change over time. Follow the options shown by Google if the wording differs from the examples in this documentation.

## Install the Package

### Clone the Repository

Clone the project:

    git clone https://github.com/Celestialglitch/swot-reservoir-wse.git

Enter the repository:

    cd swot-reservoir-wse

### Create a Virtual Environment

Using a virtual environment is recommended so that the package dependencies remain isolated from the system Python installation.

#### Windows

Create the environment:

    python -m venv .venv

Activate it:

    .venv\Scripts\activate

#### Linux / macOS

Create the environment:

    python3 -m venv .venv

Activate it:

    source .venv/bin/activate

After activation, the terminal normally displays the virtual-environment name.

For example:

    (.venv)

### Upgrade pip

Upgrade the package installer:

    python -m pip install --upgrade pip

### Install swot-reservoir-wse

Install the package from the cloned repository:

    python -m pip install .

The installation automatically installs the Python dependencies declared by the package, including the libraries required for:

- NASA Earthdata access
- Google Earth Engine
- geospatial processing
- LakeSP processing
- PIXC NetCDF processing
- numerical analysis and
- plot generation.

### Upgrade an Existing Local Installation

If **swot-reservoir-wse** has already been installed from the repository and the source code has since been updated, run:

    python -m pip install . --upgrade

For development work where changes should be immediately visible without reinstalling after every source-code modification, an editable installation can instead be used:

    python -m pip install -e .

An editable installation is useful during development but is not required for normal package use.

## Verify the Installation

Run:

    swot-reservoir-wse --help

A successful installation displays the available command groups, including:

    extract
    config
    cache
    auth

Check the extraction command:

    swot-reservoir-wse extract --help

The command should show the required arguments:

    --lat
    --lon
    --start-date
    --end-date
    --source

The supported observation sources are:

    lakesp
    pixc

## Set Up a Working Directory

**swot-reservoir-wse** uses the directory from which it is run as the runtime working directory.

You may therefore create a separate directory for an analysis:

    reservoir-analysis/

and run **swot-reservoir-wse** from that directory.

With the default configuration, the package may create:

    reservoir-analysis/
    ├── config.json
    ├── cache/
    │   ├── reservoir_polygons/
    │   └── lakesp_granules/
    ├── downloads/
    │   └── temp/
    └── outputs/

This allows different analyses to maintain separate runtime configuration and output files.

The Python package itself does not need to be located in the working directory after installation.

## Initial Authentication

From the directory in which you want to run the analysis:

    swot-reservoir-wse auth

If an Earth Engine Project ID has not yet been stored in that directory's configuration, the package prompts:

    Google Earth Engine project ID:

Enter the Google Cloud Project ID configured for Earth Engine.

The package then checks Google Earth Engine authentication.

For NASA Earthdata, existing credentials are reused when possible. Otherwise, the package asks for:

    Earthdata Login username:
    Earthdata password:

The password is entered without being echoed to the terminal.

After successful authentication:

- The Earth Engine Project ID is stored in the working-directory config.json
- Google Earth Engine OAuth credentials remain managed by Google's authentication system
- NASA Earthdata credentials are stored in the user's netrc credential file.

This section covers only the initial authentication required after installation. For reauthentication, credential removal, service-specific authentication, credential storage, and all authentication options, see [Authentication](authentication.md).

## Verify the Active Configuration

Run:

    swot-reservoir-wse config show

Verify that:

    earth_engine_project

contains the expected Google Cloud Project ID.

The default runtime paths should normally resemble:

    cache
    outputs
    downloads/temp

These paths are relative to the active working directory unless absolute paths have been configured.

For explanations of all available configuration parameters, see [Configuration](configuration.md).

### Verify the Installation

After installation, verify that the command-line interface is available:

    swot-reservoir-wse --help

Then confirm that the package can load its runtime configuration:

    swot-reservoir-wse config show

A successful configuration display confirms that the installed package is accessible and that the configuration system can be initialized from the current working directory.

For instructions regarding normal processing workflow, see [Usage](usage.md).

## Troubleshooting

### swot-reservoir-wse Command Not Found

Confirm that the environment in which the package was installed is active.

On Windows:

    .venv\Scripts\activate

On Linux or macOS:

    source .venv/bin/activate

Then verify:

    python -m pip show swot-reservoir-wse

and retry:

    swot-reservoir-wse --help

### Earth Engine Project Is Not Configured

If processing reports:

    Earth Engine project is not configured.

run:

    swot-reservoir-wse auth

or:

    swot-reservoir-wse auth --earth-engine-only

Remember that the Earth Engine Project ID is stored in the config.json of the current working directory.

If **swot-reservoir-wse** is executed from a different directory, that directory may have a different configuration.

### Earth Engine Permission Error

If Earth Engine reports that the caller does not have permission to use the selected project:

1. open the Google Cloud project;
2. verify that the authenticated Google account has access to the project;
3. check the project's IAM configuration;
4. assign the **Service Usage Consumer** role if required;
5. allow time for the IAM update to propagate.

Then retry:

    swot-reservoir-wse auth --earth-engine-only

If necessary:

    swot-reservoir-wse auth --earth-engine-only --force

### Earthdata Authentication Failure

Force a fresh Earthdata authentication:

    swot-reservoir-wse auth --earthdata-only --force

To remove the stored Earthdata entry first:

    swot-reservoir-wse auth --earthdata-only --remove

Then authenticate again:

    swot-reservoir-wse auth --earthdata-only

### PIXC Processing Uses Too Much Memory

PIXC granules contain large pixel-cloud datasets.

Reduce parallel processing:

    swot-reservoir-wse config set max_workers 2

A lower worker count reduces the number of PIXC granules being processed simultaneously.

## Next Steps

After installation:

- see [Usage](usage.md) for the normal processing workflow
- see [Authentication](authentication.md) for credential management
- see [Configuration](configuration.md) for every configurable parameter
- see [Command Reference](command_reference.md) for all CLI commands
- see [Package Architecture](architecture.md) for the LakeSP and PIXC processing design
- see [Outputs](outputs.md) for info about generated CSV and PNG products
