# Introduction

Freshwater reservoirs play a critical role in drinking water supply, irrigation, hydropower generation, flood control, and water resource management. Monitoring changes in reservoir water levels is essential for estimating water storage, supporting reservoir operations, improving flood and drought preparedness, and understanding long-term hydrological and climate variability. One of the fundamental variables used for these applications is **Water Surface Elevation (WSE)**, which describes the height of the water surface relative to a reference surface. Changes in WSE directly reflect changes in reservoir storage and provide an important indicator of the hydrological state of a reservoir over time.

The [Surface Water and Ocean Topography (SWOT)](https://science.nasa.gov/mission/swot/) mission, jointly developed by the **National Aeronautics and Space Administration (NASA)** and the **Centre National d'Études Spatiales (CNES)**, represents a major advancement in the remote sensing of global surface water. Launched on 16 December 2022, SWOT observes the elevation and extent of water across lakes, reservoirs, rivers, wetlands, and the ocean. Its **Ka-band Radar Interferometer (KaRIn)** measures surface elevation across two-dimensional swaths rather than only along a narrow satellite ground track, providing new capabilities for observing inland water bodies at large scales. SWOT observations are distributed through [NASA Earthdata](https://www.earthdata.nasa.gov/) as a collection of science products representing different stages and forms of the satellite measurements.

Two of these products are instrumental for deriving reservoir Water Surface Elevation: the **Lake Single-Pass (LakeSP) Vector Data Product** and the **Water Mask Pixel Cloud (PIXC) Data Product**. Although both originate from SWOT observations, they represent the measured surface water in fundamentally different ways and therefore require different processing approaches.

## LakeSP

The [SWOT Level 2 Lake Single-Pass Vector Data Product, Version D (SWOT_L2_HR_LakeSP_D)](https://podaac.jpl.nasa.gov/dataset/SWOT_L2_HR_LakeSP_D) provides feature-level observations of lakes and other water bodies derived from SWOT measurements. The product is distributed as continent-specific granules containing vectorized observations of water bodies detected during a SWOT pass. These observations contain quantities such as Water Surface Elevation together with the other information describing the observed feature and the quality of the measurement.

Although the SWOT LakeSP product is publicly available through NASA Earthdata, generating a continuous reservoir-specific Water Surface Elevation (WSE) time series from user-supplied dam coordinates is not straightforward. For a specific reservoir of interest, the first challenge is to identify the correct LakeSP granules, within which the polygons might exist. The second challenge is in searching for the correct lake polygon inside each granule that spatially maps to our reservoir. The third challenge is the inconsistent quality of WSE observations which introduces uneven outliers and biases.

**swot-reservoir-wse** brings these steps into a single workflow. Starting from the supplied dam coordinates, the package first derives the corresponding reservoir footprint from the [JRC Global Surface Water](https://global-surface-water.appspot.com/) dataset. Then, it identifies appropriate LakeSP granules from LakeSP product using NASA CMR search, discovers intersecting SWOT lake polygons within each granule, retrieves the required observations, performs observation quality filtering, and generates a reservoir-specific Water Surface Elevation time series through a single reproducible command.

## PIXC

The [SWOT Level 2 Water Mask Pixel Cloud Data Product, Version D (SWOT_L2_HR_PIXC_D)](https://podaac.jpl.nasa.gov/dataset/SWOT_L2_HR_PIXC_D) provides a different view of the same observed surface water. Instead of representing an observed lake as a vectorized lake feature with an already reported lake-level WSE, PIXC contains the underlying geolocated measurements as an unstructured cloud of individual pixels detected across the SWOT swath. These pixels contain information such as geographic position, measured height, surface classification, and associated quality information.

This provides access to measurements much closer to the underlying SWOT observations, but it also means that a reservoir WSE value is not directly available from the product. It has to be derived from the individual PIXC measurements associated with that reservoir.

For a specific reservoir of interest, the first challenge is again to identify the PIXC granules that may contain observations of the reservoir. However, unlike LakeSP, there is no lake feature from which the reservoir WSE can simply be extracted. The relevant measurements must instead be found among the much larger collection of pixels contained within each granule. The pixels that actually fall inside the reservoir must be spatially isolated, and measurements that do not satisfy the required water-classification and quality conditions must be removed. The retained pixel heights must then be converted from ellipsoidal height to Water Surface Elevation relative to the geoid and combined to obtain a representative WSE for the reservoir.

**swot-reservoir-wse** performs these steps through an independent PIXC processing workflow. Using the same reservoir footprint derived from the supplied dam coordinates, the package searches NASA Earthdata for relevant PIXC products over the requested observation period and checks their spatial association with the reservoir before processing the pixel-cloud measurements.

For each relevant acquisition, the package identifies the PIXC measurements lying within the reservoir boundary and applies the required classification and quality screening. The retained pixel heights are converted to geoid-referenced WSE and combined to obtain a representative reservoir-level WSE for that acquisition date. Once observations from the requested period have been processed, temporal outlier filtering is applied to the resulting sequence to produce the final PIXC-derived reservoir WSE time series.

PIXC processing is consequently different from LakeSP processing at a fundamental level. With LakeSP, **swot-reservoir-wse** begins with SWOT's processed lake-feature observations and determines which of those observations belong to the reservoir. With PIXC, the package begins with the underlying surface-water pixel measurements and derives the reservoir-level observation itself.

## Two Independent Routes to Reservoir WSE

LakeSP and PIXC are therefore supported as two independently selectable SWOT observation sources within **swot-reservoir-wse**.

Both workflows begin with the same basic information supplied by the user: the dam location and the observation period. The reservoir footprint is derived once from the dam location and then used as the spatial reference for the selected processing workflow.

From that point, the two routes are different. LakeSP identifies and processes SWOT's vectorized lake observations, while PIXC identifies and processes the individual surface-water pixels belonging to the reservoir. Both routes ultimately reduce the available SWOT measurements to a quality-controlled sequence of reservoir-level WSE observations over time.

This allows the same reservoir to be processed independently from either the higher-level LakeSP observations or the underlying PIXC measurements, without requiring the user to manually identify SWOT granules, lake features, or reservoir pixels.
