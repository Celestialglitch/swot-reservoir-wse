# swot-reservoir-wse

***A source-configurable and easy-to-use Python package to make SWOT-based reservoir water-level monitoring accessible to the global water community***

**swot-reservoir-wse** provides a simple command-line interface for deriving reservoir Water Surface Elevation (WSE) time series from observations of the **[Surface Water and Ocean Topography (SWOT)](https://science.nasa.gov/mission/swot/)** mission. Starting only with the location of a dam, the package identifies the corresponding reservoir and handles the processing required to turn the available SWOT observations into a reservoir-specific record of water surface elevation over time.

**swot-reservoir-wse** currently supports two independently selectable SWOT Level 2 products that represent surface-water observations at different stages of processing.

The [SWOT Level 2 Lake Single-Pass Vector Data Product, Version D (SWOT_L2_HR_LakeSP_D)](https://podaac.jpl.nasa.gov/dataset/SWOT_L2_HR_LakeSP_D) provides feature-level observations of lakes and other water bodies derived from SWOT measurements. For this source, **swot-reservoir-wse** searches the available LakeSP products, spatially identifies the observed lake features associated with the target reservoir, and extracts their reported WSE and quality information. Partial and unacceptable observations are screened according to the active configuration, multiple retained measurements from the same acquisition date are reduced to a representative daily WSE, and temporal outliers are removed before the final reservoir time series is produced.

The [SWOT Level 2 Water Mask Pixel Cloud Data Product, Version D (SWOT_L2_HR_PIXC_D)](https://podaac.jpl.nasa.gov/dataset/SWOT_L2_HR_PIXC_D), in contrast, provides the underlying high-resolution geolocated water detections as an unstructured pixel cloud. Each detected pixel carries quantities such as its geographic position, ellipsoidal height, surface classification, and associated quality information. For this source, **swot-reservoir-wse** works directly with the measurements falling inside the target reservoir. It spatially isolates the reservoir pixels, removes pixels that do not satisfy the required water-classification and quality conditions, converts the retained pixel heights from ellipsoidal height to WSE relative to the geoid, and combines the resulting measurements into a representative reservoir WSE for each acquisition date. The resulting time series is then subjected to temporal outlier screening.

The package therefore provides two independent routes to the same reservoir-level quantity: **LakeSP uses SWOT's processed lake-feature observations, while PIXC derives reservoir WSE directly from the underlying surface-water pixel measurements.**

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

In order to obtain a reservoir WSE time series from SWOT, there exist several steps between downloading the SWOT products and obtaining measurements that belong to a particular reservoir.

**swot-reservoir-wse** brings these steps into a single workflow. Starting only from the supplied dam coordinates, it derives the reservoir boundary using [JRC Global Surface Water](https://global-surface-water.appspot.com/), selects the appropriate SWOT product (LakeSP or PIXC) as source, searches [NASA Earthdata](https://www.earthdata.nasa.gov/) for SWOT observations covering the requested period, identifies measurements belonging to the reservoir, removes unsuitable observations, combines measurements acquired on the same date, and filters temporal outliers before producing the final WSE time series.

For **LakeSP**, the package works with SWOT's vectorized lake observations and identifies the observations associated with the target reservoir. It uses the available product quality information to screen observations before daily aggregation and temporal filtering. For **PIXC**, it works directly with the pixel-cloud product, spatially selects measurements falling within the reservoir boundary, applies pixel-level water classification and quality screening, calculates WSE relative to the geoid, and combines the accepted measurements into reservoir-level WSE observations. The two approaches remain independent and can therefore be run separately for the same reservoir.

The processing can be configured for different SWOT science cycles, LakeSP quality classes, PIXC water classification, product-search regions, reservoir-identification parameters, temporal filtering thresholds, and computational resources. Product discovery and granule processing can use parallel workers where supported, while the worker count can be increased or decreased based on source product. Reservoir boundaries and downloaded LakeSP products can also be cached locally for reuse, avoiding repeated reservoir-footprint generation and unnecessary downloads. Temporary processing data, persistent caches, and final outputs can be directed to configurable filesystem locations, and each successful extraction produces a reservoir WSE time series with optional plot generation.

Detailed descriptions of the processing methods, configuration parameters, authentication, command-line interface, and generated products are available in the [documentation](https://swot-reservoir-wse.readthedocs.io/).

## Documentation

The complete documentation is available at:

[https://swot-reservoir-wse.readthedocs.io/](https://swot-reservoir-wse.readthedocs.io/)

It includes installation and authentication instructions, LakeSP and PIXC usage, configuration options, command reference, processing architecture, and descriptions of the generated outputs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development and contribution guidelines.

## License

This package is distributed under the MIT License. See [LICENSE](LICENSE) for details.
