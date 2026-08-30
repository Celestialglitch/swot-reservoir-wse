# swot-reservoir-wse

***A source-configurable and easy-to-use Python package to make SWOT-based reservoir water-level monitoring accessible to the global water community***

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/Celestialglitch/swot-reservoir-wse/releases/tag/v0.3.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22176957.svg)](https://doi.org/10.5281/zenodo.22176957)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Documentation](https://readthedocs.org/projects/swot-reservoir-wse/badge/?version=latest)](https://swot-reservoir-wse.readthedocs.io/)

The **swot-reservoir-wse** package provides a simple command-line interface for deriving reservoir Water Surface Elevation (WSE) time series from observations of the **[Surface Water and Ocean Topography (SWOT)](https://science.nasa.gov/mission/swot/)** mission. Starting only with the location of a dam, the package identifies the corresponding reservoir and handles the processing required to turn the available SWOT observations into a reservoir-specific record of water surface elevation over time.

**swot-reservoir-wse** currently supports two independently selectable SWOT Level 2 products that represent surface-water observations at different stages of processing. They are [SWOT Level 2 Lake Single-Pass Vector Data Product, Version D (SWOT_L2_HR_LakeSP_D)](https://podaac.jpl.nasa.gov/dataset/SWOT_L2_HR_LakeSP_D) and [SWOT Level 2 Water Mask Pixel Cloud Data Product, Version D (SWOT_L2_HR_PIXC_D)](https://podaac.jpl.nasa.gov/dataset/SWOT_L2_HR_PIXC_D).

## Installing swot-reservoir-wse

Clone the repository:

    git clone https://github.com/Celestialglitch/swot-reservoir-wse.git
    cd swot-reservoir-wse

Create a virtual environment and install the package.

On Windows:

    python -m venv .venv
    .venv\Scripts\activate
    python -m pip install .

On Linux or macOS:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install .

The package uses **NASA Earthdata** to access SWOT observations and **Google Earth Engine** to identify reservoir boundaries from user supplied dam location.

The complete setup procedure is available in the [Installation Guide](https://swot-reservoir-wse.readthedocs.io/en/latest/installation.html).


## About **swot-reservoir-wse**

In order to obtain a reservoir WSE time series from SWOT mission, there exist multiple steps between downloading the SWOT products and obtaining measurements that belong to a particular reservoir.

**swot-reservoir-wse** brings these steps into a single workflow. Starting from user-supplied dam coordinates, it derives the reservoir boundary using [JRC Global Surface Water](https://global-surface-water.appspot.com/), searches [NASA Earthdata](https://www.earthdata.nasa.gov/) for observations from the selected [LakeSP](https://podaac.jpl.nasa.gov/dataset/SWOT_L2_HR_LakeSP_D) or [PIXC](https://podaac.jpl.nasa.gov/dataset/SWOT_L2_HR_PIXC_D) product, identifies measurements belonging to the reservoir, performs source-specific quality processing, combines observations acquired on the same date, and filters temporal outliers before producing the final WSE time series.

LakeSP and PIXC are implemented as independent processing workflows. LakeSP works with SWOT's vectorized lake observations, while PIXC works directly with the underlying pixel-cloud measurements to derive reservoir-level WSE. The same reservoir can therefore be processed independently using either source.

The workflow is configurable for SWOT science cycles, source-specific quality criteria, spatial search and reservoir-identification parameters, temporal filtering, parallel processing, caching, runtime storage, and output generation. Reservoir footprints and downloaded LakeSP products can be reused through persistent caching, and successful processing produces a reservoir WSE time series with optional visualization.

Detailed descriptions of the processing methods, configuration parameters, authentication, command-line interface, and generated products are available in the [documentation](https://swot-reservoir-wse.readthedocs.io/).

## Documentation

The complete documentation is available at:

[https://swot-reservoir-wse.readthedocs.io/](https://swot-reservoir-wse.readthedocs.io/)

It includes installation and authentication instructions, package architecture, LakeSP and PIXC usage, command reference, configuration options, and descriptions of the generated outputs.

## Citation

If you use **swot-reservoir-wse** in research or other academic work, please cite the software as:

> Dasgupta, O., & Das, P. (2026). *swot-reservoir-wse* (Version 0.3.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.22176957

Citation metadata is also available in [CITATION.cff](CITATION.cff).


## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development and contribution guidelines.

## License

This package is distributed under the MIT License. See [LICENSE](LICENSE) for details.
