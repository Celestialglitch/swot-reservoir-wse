# swot-reservoir-wse

swot-reservoir-wse is a Python package for generating reservoir-specific Water Surface Elevation (WSE) time series from NASA Surface Water and Ocean Topography (SWOT) observations.

Given a dam location, observation period, and SWOT data source, the package derives the corresponding reservoir footprint, discovers relevant SWOT observations, performs source-specific spatial and quality processing, and produces a reservoir WSE time series.

Supported SWOT Level-2 High Rate products:

- Lake Single Pass (LakeSP) Observation Vector Product, Version D
- Water Mask Pixel Cloud (PIXC) Product, Version D

Full documentation: https://swot-reservoir-wse.readthedocs.io/

---

## Installation

swot-reservoir-wse requires Python 3.10 or later, NASA Earthdata access, Google Earth Engine access, and a Google Cloud project configured for Earth Engine.

Clone and install the package:

    git clone https://github.com/Celestialglitch/swot-reservoir-wse.git
    cd swot-reservoir-wse
    python -m pip install .

For environment setup and external-service configuration, see the Installation Guide:

https://swot-reservoir-wse.readthedocs.io/en/latest/installation.html

---

## Authentication

Configure Google Earth Engine and NASA Earthdata access:

    swot-reservoir-wse auth

Authentication can also be managed independently for either service.

See the Authentication documentation for account setup, credential storage, reauthentication, and removal:

https://swot-reservoir-wse.readthedocs.io/en/latest/authentication.html

---

## Usage

Run an extraction by providing the dam coordinates, observation period, and SWOT source.

LakeSP:

    swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp

PIXC:

    swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc

LakeSP and PIXC are independent processing sources and must be selected explicitly.

For the complete workflow, see:

https://swot-reservoir-wse.readthedocs.io/en/latest/usage.html

---

## Outputs

Successful processing produces a source-specific CSV time series and, when plotting is enabled, a PNG visualization.

Example:

    outputs/
    ├── 19.69000_73.34000_lakesp_wse.csv
    └── 19.69000_73.34000_lakesp_wse.png

PIXC outputs use the corresponding pixc filename identifier.

See the Outputs documentation for CSV schemas, quality information, and plot details:

https://swot-reservoir-wse.readthedocs.io/en/latest/outputs.html

---

## Documentation

Complete documentation is available at:

https://swot-reservoir-wse.readthedocs.io/

It includes:

- Installation
- Usage
- Configuration
- Authentication
- Command Reference
- Package Architecture
- Outputs

---

## Contributing

Contributions, bug reports, and documentation improvements are welcome.

See CONTRIBUTING.md for development and contribution guidelines.

---

## License

swot-reservoir-wse is distributed under the MIT License.

See LICENSE for the complete license text.
