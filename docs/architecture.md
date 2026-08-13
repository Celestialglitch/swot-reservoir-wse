# Package Architecture

This document provides a high-level overview of how **swot-reservoir-wse** transforms a user-supplied dam location into a reservoir-specific Water Surface Elevation (WSE) time series using observations from the Surface Water and Ocean Topography (SWOT) mission.

The document describes the processing architecture and data flow of the package rather than the organization of individual Python modules.

---

# Architecture Overview

**swot-reservoir-wse** follows a modular observation-source architecture.

The package separates three major responsibilities:

1. identifying the reservoir associated with a supplied dam location;
2. processing observations from a selected SWOT data product; and
3. producing a standardized reservoir-level WSE time series.

Reservoir footprint generation and output handling are shared across observation sources, while product-specific discovery, extraction, quality screening, and aggregation are handled by independent source pipelines.

The current release supports:

- **LakeSP** — SWOT Level 2 Lake Single-Pass Vector Obs Data Product, Version D
- **PIXC** — SWOT Level 2 Water Mask Pixel Cloud Data Product, Version D

LakeSP and PIXC are independent observation sources. The source is selected explicitly for each extraction; one source is not used automatically as a fallback for another.

---

# 1. Architecture Overview

A `swot-wse` extraction can be divided into three major stages:

1. **Reservoir identification**
2. **Source-specific SWOT processing**
3. **Output generation**

At a high level:

```text
                         User Input
              (dam coordinates + date range)
                              │
                              ▼
                    Reservoir Identification
                              │
                              ▼
                     Reservoir Footprint
                              │
                              ▼
                    Selected SWOT Source
                      ┌───────┴───────┐
                      │               │
                      ▼               ▼
                   LakeSP            PIXC
                   Source            Source
                      │               │
                      ▼               ▼
               LakeSP Processing   PIXC Processing
                      │               │
                      └───────┬───────┘
                              │
                              ▼
                  Reservoir WSE Time Series
                              │
                              ▼
                     Output Generation
                         CSV / PNG
```

The reservoir footprint is therefore the boundary between the common spatial-identification stage and the product-specific observation processing stage.

This separation is important because LakeSP and PIXC represent SWOT observations differently.

LakeSP provides vector observations associated with detected water features. PIXC, by contrast, provides geolocated pixel-cloud measurements. Consequently, the two products cannot be processed by the same extraction logic even though both can ultimately be used to estimate reservoir WSE.

---

# 2. Extraction Entry Point

A processing run is initiated through:

```bash
swot-wse extract \
    --lat <latitude> \
    --lon <longitude> \
    --start-date YYYY-MM-DD \
    --end-date YYYY-MM-DD \
    --source {lakesp,pixc}
```

The extraction request therefore defines:

```text
dam location
    +
observation period
    +
observation source
```

The latitude and longitude identify the **dam location**, not a pre-existing SWOT lake identifier or reservoir polygon.

This is intentional. The package first resolves the supplied location into a reservoir footprint and then uses that footprint as the spatial basis for processing the selected SWOT product.

The observation source is resolved independently from reservoir identification. Adding another source therefore does not require changing how the reservoir itself is located, provided that the new source can operate on the same geographic reservoir footprint.

---

# 3. Reservoir Identification

## 3.1 Why a reservoir footprint is required

The user supplies a point:

```text
(latitude, longitude)
```

but both supported SWOT processing paths require an area describing the reservoir.

The first task is therefore to convert the supplied dam location into a polygon representing the associated surface-water body.

This stage is independent of LakeSP and PIXC.

---

## 3.2 Surface-water extraction

Reservoir identification uses the **JRC Global Surface Water** dataset through **Google Earth Engine**.

A search region is constructed around the supplied coordinates. Surface-water occurrence information within this region is thresholded according to the active package configuration and converted into candidate water-body polygons.

Conceptually:

```text
Dam coordinate
      │
      ▼
Local search region
      │
      ▼
JRC surface-water occurrence
      │
      ▼
Occurrence threshold
      │
      ▼
Candidate water polygons
```

The extraction is therefore based on observed surface-water occurrence rather than on a built-in reservoir catalogue.

---

## 3.3 Polygon selection

The generated candidate polygons are evaluated relative to the supplied dam location.

If one or more candidate polygons contain the supplied point, the largest containing polygon is selected.

If the point is not contained by a candidate polygon, the nearest candidate polygon is selected.

This second case is useful because dam coordinates do not necessarily fall directly inside the extracted water polygon. A coordinate may lie on the dam structure, shoreline, or immediately outside the water mask.

The selected geometry is transformed to geographic coordinates (`EPSG:4326`) before it is passed to the observation-source pipeline.

---

## 3.4 Reservoir polygon cache

Generating the reservoir polygon requires a Google Earth Engine operation. Repeating the same extraction for the same location would therefore perform unnecessary remote processing.

When polygon caching is enabled, the generated footprint is stored locally.

A later extraction using the same coordinate key can reuse the stored polygon:

```text
Dam coordinates
      │
      ▼
Polygon cache
   ┌──┴───┐
   │      │
 found   missing
   │      │
   │      ▼
   │   Earth Engine
   │      │
   │      ▼
   │   Generate polygon
   │      │
   └──────┤
          ▼
   Reservoir footprint
```

The cached polygon is independent of the SWOT source. A polygon generated while processing LakeSP can therefore also be reused during a later PIXC extraction for the same reservoir.

---

# 4. Observation-Source Architecture

Once the reservoir footprint has been obtained, the common reservoir-identification stage ends.

Processing is then delegated to the source selected by the user:

```text
--source lakesp
```

or:

```text
--source pixc
```

The source layer provides a common architectural boundary around product-specific processing.

Each source is responsible for turning:

```text
reservoir footprint
+
date range
```

into a reservoir-level WSE time series.

What happens inside that operation is source dependent.

This is necessary because the two supported products expose fundamentally different observation structures:

```text
LakeSP
    │
    └── feature/vector observations
            │
            └── reservoir association through LakeSP features/lake_id

PIXC
    │
    └── geolocated pixel-cloud observations
            │
            └── reservoir association through spatial pixel filtering
```

The package therefore shares orchestration where possible without forcing product-specific scientific processing into a single generic algorithm.

---

# 5. LakeSP Processing

The LakeSP source processes SWOT Level 2 Lake Single-Pass vector observations.

Unlike PIXC, LakeSP already contains observations organized around detected water features. The main problem is therefore to determine which LakeSP observations correspond to the reservoir footprint and then screen and aggregate those observations.

The LakeSP processing path can be summarized as:

```text
Reservoir footprint
        │
        ▼
Candidate granule search
        │
        ▼
Reservoir intersection
        │
        ▼
Lake identifier discovery
        │
        ▼
Observation extraction
        │
        ▼
Product-quality filtering
        │
        ▼
Daily aggregation
        │
        ▼
Temporal MAD filtering
        │
        ▼
LakeSP WSE time series
```

---

## 5.1 Candidate granule discovery

The reservoir footprint and requested date range are used to search NASA Earthdata for candidate LakeSP products.

The spatial query is constructed from the reservoir extent with the configured LakeSP search buffer.

The initial Earthdata result is deliberately treated as a **candidate set**.

A granule returned by the search is not assumed to contain an observation belonging to the reservoir merely because it satisfies the broad spatial query.

Configured SWOT science cycles can also be used to restrict the candidate set before further processing.

---

## 5.2 Reservoir intersection and `lake_id` discovery

Candidate LakeSP products are inspected to determine whether their observation geometries intersect the actual reservoir footprint.

For intersecting observations, the corresponding LakeSP `lake_id` values are collected.

These identifiers establish the association between the geographic reservoir derived earlier and the feature-level observations contained in LakeSP.

This gives the LakeSP branch two distinct spatial stages:

```text
Earthdata spatial search
        │
        ▼
Candidate granules
        │
        ▼
Actual polygon intersection
        │
        ▼
Relevant lake_id values
```

The first stage limits the amount of data that must be examined. The second establishes the actual reservoir association.

---

## 5.3 Observation extraction

After the relevant `lake_id` values have been identified, LakeSP observations associated with those identifiers are extracted from the verified products.

The extracted records contain the variables required by the subsequent filtering and aggregation stages, including WSE and LakeSP quality information.

Multiple observations may be available for the same acquisition date.

At this point, the records are still individual LakeSP observations rather than the final daily reservoir time series.

---

## 5.4 LakeSP quality screening

LakeSP observations are screened before daily aggregation.

The processing first removes partial observations and then applies the configured LakeSP quality classes.

The package recognizes the LakeSP quality categories:

```text
GOOD
SUSPECT
DEGRADED
BAD
```

The set of accepted classes is configurable.

This allows the scientific screening policy to be changed without modifying the extraction implementation itself.

Only observations that pass the active screening policy proceed to daily aggregation.

---

## 5.5 Daily aggregation

Several accepted LakeSP records can correspond to the same acquisition date.

These observations are grouped by date and reduced to a representative reservoir-level observation.

The daily WSE is calculated using the median of the accepted WSE measurements for that date.

A representative daily quality status is also assigned from the quality information of the observations contributing to the daily value.

The result of this stage is no longer a collection of individual LakeSP feature records. It is a chronological series of reservoir-level daily observations.

---

## 5.6 Temporal outlier filtering

The daily LakeSP WSE series is finally screened for temporal outliers using a Median Absolute Deviation (MAD)-based filter.

For the daily WSE values \(x_i\), the median of the series is:

```text
m = median(x)
```

and the Median Absolute Deviation is:

```text
MAD = median(|x_i - m|)
```

The package evaluates the modified deviation score:

```text
modified_z = 0.6745 × |x_i - m| / MAD
```

An observation is retained when its modified deviation score does not exceed the configured LakeSP MAD threshold.

The result is the final LakeSP-derived reservoir WSE time series.

The threshold is configurable because the temporal screening criterion can affect which observations remain in the scientific output.

---

# 6. PIXC Processing

The PIXC source processes SWOT Level 2 Water Mask Pixel Cloud observations.

PIXC requires a substantially different extraction strategy from LakeSP.

Rather than associating the reservoir with existing feature-level lake observations, the package works directly with geolocated PIXC measurements and determines which pixels belong to the reservoir footprint.

The PIXC processing path is:

```text
Reservoir footprint
        │
        ▼
Candidate granule search
        │
        ▼
CMR footprint verification
        │
        ▼
Granule download
        │
        ▼
Pixel extraction
        │
        ▼
Reservoir spatial filtering
        │
        ▼
Pixel-quality screening
        │
        ▼
Pixel WSE calculation
        │
        ▼
Daily aggregation
        │
        ▼
Temporal MAD filtering
        │
        ▼
PIXC WSE time series
```

---

## 6.1 Candidate PIXC discovery

NASA Earthdata is queried for PIXC products covering the requested observation period and reservoir region.

As with LakeSP, the search result is treated as a candidate set rather than as proof that every returned product contains measurements relevant to the reservoir.

Configured science-cycle restrictions can be applied during this stage.

---

## 6.2 Footprint verification

PIXC products can be large, making unnecessary downloads expensive in both time and storage.

Candidate granules are therefore checked using their CMR spatial metadata before the full product is processed.

Only candidates whose reported footprint intersects the reservoir are retained for subsequent processing.

This creates an inexpensive rejection stage before the more costly download and NetCDF processing stages:

```text
Earthdata results
       │
       ▼
CMR footprint
intersection test
   ┌───┴────┐
   │        │
reject    retain
            │
            ▼
         download
```

---

## 6.3 PIXC product extraction

Verified PIXC products are downloaded and processed individually.

The required measurements are read from the PIXC `pixel_cloud` group. These include pixel coordinates, height information, classification information, quality information, and geoid height required by the extraction pipeline. :contentReference[oaicite:1]{index=1}

Because PIXC contains large numbers of observations, spatial rejection is performed in stages rather than immediately constructing geometry for every pixel in the product.

---

## 6.4 Reservoir spatial filtering

The reservoir polygon bounds are first used as a coarse geographic filter.

Pixels outside the reservoir bounding box can be rejected using their coordinates without performing more expensive geometric operations.

The remaining candidate pixels are then tested against the actual reservoir polygon.

Conceptually:

```text
All PIXC pixels
       │
       ▼
Reservoir bounding-box filter
       │
       ▼
Candidate reservoir pixels
       │
       ▼
Point-in-polygon filtering
       │
       ▼
Pixels inside reservoir
```

The bounding-box stage is therefore an optimization; the reservoir polygon remains the actual spatial criterion used to determine reservoir membership.

This two-stage strategy avoids unnecessary geometry construction and point-in-polygon operations for pixels that are clearly outside the reservoir.

---

## 6.5 PIXC quality screening

Spatial membership alone does not imply that a PIXC observation should contribute to the reservoir WSE estimate.

The retained pixels are therefore screened using PIXC classification and classification-quality information.

The current processing selects the configured water classes and rejects pixels whose relevant quality information does not satisfy the active PIXC screening policy.

This stage is separate from spatial filtering:

```text
Inside reservoir
      ≠
Accepted WSE observation
```

A pixel must satisfy both the spatial criterion and the configured product-quality criteria before it contributes to daily WSE aggregation.

---

## 6.6 Pixel-level WSE

For accepted PIXC pixels, reservoir WSE is calculated from the PIXC height and geoid variables.

The current processing uses:

```text
WSE = height - geoid
```

The resulting value represents the pixel water-surface elevation relative to the geoid rather than the ellipsoidal height stored directly in the PIXC height measurement. :contentReference[oaicite:2]{index=2}

At this point the dataset still consists of many individual pixel-level WSE observations.

---

## 6.7 Daily reservoir aggregation

Accepted PIXC pixels are grouped by acquisition date.

For each date, the median of the accepted pixel WSE values is used as the representative reservoir WSE. :contentReference[oaicite:3]{index=3}

The PIXC pipeline also derives summary statistics describing the accepted pixel population. These statistics are retained in the PIXC output so that the daily WSE value is accompanied by information about the observations from which it was calculated.

This stage performs the key reduction:

```text
many accepted PIXC pixels
             │
             ▼
       one acquisition date
             │
             ▼
representative reservoir WSE
```

---

## 6.8 Temporal outlier filtering

The resulting sequence of daily PIXC observations is screened using a MAD-based temporal filter.

The purpose of this stage is different from pixel-level quality screening.

Pixel screening operates **within an acquisition** and determines which PIXC measurements are eligible to contribute to that day's estimate.

Temporal filtering operates **between daily reservoir observations** and identifies daily WSE values that deviate strongly from the overall temporal series.

The remaining observations form the final PIXC-derived reservoir WSE record. :contentReference[oaicite:4]{index=4}

---

# 7. Why LakeSP and PIXC Remain Separate

Although both pipelines eventually produce reservoir WSE observations, merging their internal processing would hide important differences between the products.

The association problem alone is fundamentally different:

```text
LakeSP
Reservoir polygon
      │
      ▼
Intersect LakeSP features
      │
      ▼
Identify lake_id
      │
      ▼
Extract feature WSE
```

versus:

```text
PIXC
Reservoir polygon
      │
      ▼
Filter geolocated pixels
      │
      ▼
Apply pixel quality criteria
      │
      ▼
Calculate pixel WSE
      │
      ▼
Aggregate pixels
```

The source abstraction therefore standardizes **where the pipelines connect to the rest of the package**, not the scientific processing inside each source.

This allows source-specific processing to evolve independently while preserving a common extraction interface.

It also provides the architectural basis for supporting additional SWOT observation products in the future without placing product-specific logic directly inside the top-level extraction workflow.

---

# 8. Shared Output Stage

Both source pipelines return a reservoir-level time series to the common output layer.

The output layer is responsible for writing the processed result rather than deciding how the observations were scientifically derived.

Output filenames include the source name so that LakeSP and PIXC extractions for the same reservoir remain distinct.

For example:

```text
19.69000_73.34000_lakesp_wse.csv
19.69000_73.34000_lakesp_wse.png

19.69000_73.34000_pixc_wse.csv
19.69000_73.34000_pixc_wse.png
```

The exact output schema is source dependent because the two processing pipelines retain different metadata and summary information.

See [Outputs](outputs.md) for the complete output schemas.

---

# 9. Caching and Temporary Data

The package distinguishes between data that are useful across multiple executions and data required only during a single processing run.

## Persistent data

The current persistent cache includes:

```text
cache/
├── reservoir_polygons/
└── lakesp_granules/
```

Reservoir polygons can be reused by either source.

LakeSP granules are retained so that previously downloaded products can be reused when the same data are required again.

## Temporary data

PIXC products are currently processed through temporary working directories rather than a persistent PIXC granule cache.

Temporary download and extraction data are therefore separate from persistent cache state.

This distinction is particularly relevant for PIXC because individual products can be substantially larger than LakeSP vector products.

---

# 10. Configuration Boundaries

The configuration system follows the same separation used by the processing architecture.

Settings that affect the package as a whole remain at the common configuration level, while product-specific settings are grouped under their respective source:

```text
sources.lakesp.*
sources.pixc.*
```

This prevents LakeSP processing parameters from implicitly affecting PIXC processing and vice versa.

Examples of source-specific concerns include:

```text
LakeSP
├── collection
├── science cycles
├── search buffer
├── accepted quality classes
└── MAD threshold

PIXC
├── collection
├── science cycles
├── search parameters
├── accepted water classifications
├── quality screening
└── MAD threshold
```

The architecture document intentionally does not enumerate configuration defaults because those values may change independently of the processing design.

See [Configuration](configuration.md) for the active parameters and defaults.

---

# 11. Failure Boundaries

The pipeline distinguishes between a processing failure and the absence of usable observations.

For example, any of the following can legitimately produce no WSE time series:

```text
no reservoir footprint identified
no candidate SWOT products found
no product intersects the reservoir
no LakeSP observations survive screening
no PIXC pixels satisfy the spatial/quality criteria
no daily observations survive temporal filtering
```

These cases describe valid outcomes of the requested extraction rather than necessarily indicating a software error.

By contrast, failures involving authentication, inaccessible external services, invalid configuration, malformed products, or unexpected processing exceptions represent operational errors.

Keeping these cases separate is important for both command-line behaviour and programmatic use of the package.

---

# 12. Architectural Summary

The package is organized around one central principle:

> **Reservoir identification is shared; interpretation of SWOT observations belongs to the selected source.**

The complete data flow is therefore:

```text
User
 │
 ├── dam latitude
 ├── dam longitude
 ├── start date
 ├── end date
 └── source
      │
      ▼
Reservoir footprint
(JRC Global Surface Water / Earth Engine)
      │
      ▼
Source selection
 ┌────┴─────────────────────┐
 │                          │
 ▼                          ▼
LakeSP                     PIXC
 │                          │
 ├─ candidate search        ├─ candidate search
 ├─ intersection            ├─ footprint verification
 ├─ lake_id association     ├─ product download
 ├─ observation extraction  ├─ pixel extraction
 ├─ quality screening       ├─ spatial filtering
 ├─ daily aggregation       ├─ quality screening
 └─ temporal filtering      ├─ pixel WSE calculation
                            ├─ daily aggregation
                            └─ temporal filtering
 │                          │
 └────────────┬─────────────┘
              ▼
      Reservoir WSE result
              │
              ▼
         Output layer
          ├── CSV
          └── PNG
```

The result is a single user-facing extraction interface over multiple independent SWOT observation pipelines, with shared reservoir identification, configuration infrastructure, caching, authentication, and output handling.
