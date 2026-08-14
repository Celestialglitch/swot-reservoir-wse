# swot-reservoir-wse

***A source-configurable and easy-to-use Python package to make SWOT-based reservoir water-level monitoring accessible to the global water community***

The **swot-reservoir-wse** package provides a simple command-line interface for deriving reservoir Water Surface Elevation (WSE) time series from observations of the **[Surface Water and Ocean Topography (SWOT)](https://science.nasa.gov/mission/swot/)** mission. Starting only with the location of a dam, the package identifies the corresponding reservoir and handles the processing required to turn the available SWOT observations into a reservoir-specific record of water surface elevation over time.

**swot-reservoir-wse** currently supports two independently selectable SWOT Level 2 products that represent surface-water observations at different stages of processing. They are [SWOT Level 2 Lake Single-Pass Vector Data Product, Version D (SWOT_L2_HR_LakeSP_D)](https://podaac.jpl.nasa.gov/dataset/SWOT_L2_HR_LakeSP_D) and [SWOT Level 2 Water Mask Pixel Cloud Data Product, Version D (SWOT_L2_HR_PIXC_D)](https://podaac.jpl.nasa.gov/dataset/SWOT_L2_HR_PIXC_D).

```{toctree}
:maxdepth: 1
:caption: Documentation

introduction
architecture
configuration
command_reference
installation
authentication
usage
outputs
