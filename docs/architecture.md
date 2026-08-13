# Package Architecture

This document describes how **swot-reservoir-wse** turns a dam location and observation period into a reservoir-specific Water Surface Elevation (WSE) time series from Surface Water and Ocean Topography (SWOT) observations.

Unlike the README, which introduces the package from a user's perspective, this page describes the processing system itself: how information moves through the package, which operations are shared between observation sources, where the LakeSP and PIXC pipelines differ, and how individual SWOT observations are reduced to the final reservoir-level time series.

The package currently supports two independent SWOT Level-2 Version D observation sources:

- **Lake Single Pass (LakeSP) Observation Vector Product**
- **High Rate Pixel Cloud (PIXC) Product**

The user selects one of these sources explicitly for each extraction.

---

# 1. System Overview

An extraction begins with five pieces of information:

```text
dam latitude
dam longitude
start date
end date
observation source
```

For example:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

The coordinates identify a **dam**, but the scientific quantity being extracted belongs to the **reservoir water surface**.

This distinction determines the first stage of the architecture.

A dam coordinate is a point:

```text
                     Dam
                      ●
                 (lat, lon)
```

while SWOT observations must ultimately be associated with the spatial extent of the reservoir:

```text
                Reservoir
           ┌─────────────────┐
          /                   \
         /                     \
        |                       |
        |                 ● Dam |
         \                     /
          \___________________/
```

The package therefore does not use the supplied coordinate as the final spatial query object. It first derives a polygon representing the reservoir associated with that location.

That polygon then becomes the common spatial object used by the selected SWOT processing pipeline.

At the highest level, the architecture is:

```text
                           User Input
                               │
                               │
              latitude + longitude + date range
                         + source
                               │
                               ▼
                  ┌─────────────────────────┐
                  │ Reservoir Identification│
                  │                         │
                  │ JRC Global Surface Water│
                  │ + Google Earth Engine   │
                  └────────────┬────────────┘
                               │
                               ▼
                      Reservoir Polygon
                               │
                               ▼
                    Observation Source
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
             ┌─────────────┐       ┌─────────────┐
             │   LakeSP    │       │    PIXC     │
             │  Pipeline   │       │  Pipeline   │
             └──────┬──────┘       └──────┬──────┘
                    │                     │
                    │ reservoir-level     │ pixel-level
                    │ vector observations │ observations
                    │                     │
                    └──────────┬──────────┘
                               │
                               ▼
                    Daily WSE Observations
                               │
                               ▼
                    Temporal MAD Filtering
                               │
                               ▼
                 Reservoir WSE Time Series
                               │
                     ┌─────────┴─────────┐
                     ▼                   ▼
                    CSV             optional PNG
```

The important architectural point is that **LakeSP and PIXC share the reservoir-identification and output infrastructure, but they do not share the same observation-extraction logic**.

The two SWOT products represent water observations differently, so each source has its own discovery, spatial verification, extraction, screening, and aggregation stages.

---

# 2. Common Processing Layer

Before the source-specific pipeline begins, both LakeSP and PIXC follow the same initial path:

```text
Dam coordinates
      │
      ▼
Reservoir search region
      │
      ▼
JRC surface-water data
      │
      ▼
Candidate water polygons
      │
      ▼
Reservoir selection
      │
      ▼
Reservoir polygon
```

The result is a geographic polygon describing the reservoir that the package will attempt to observe with SWOT.

---

# 3. Reservoir Identification

## 3.1 Why Reservoir Identification Is Necessary

The extraction command accepts a dam latitude and longitude because a dam location is a convenient way for a user to identify a reservoir.

The SWOT products themselves, however, are not queried simply by asking for "the observation at this dam coordinate."

A reservoir can extend many kilometres away from its dam, and valid SWOT measurements may occur throughout that water surface.

The package therefore converts:

```text
dam coordinate
```

into:

```text
reservoir footprint
```

before searching for reservoir observations.

---

## 3.2 JRC Global Surface Water

Reservoir identification uses the **JRC Global Surface Water** dataset through **Google Earth Engine**.

The relevant runtime parameters include:

```text
search_radius_m
pekel_threshold
working_crs
```

The default configuration currently uses:

```text
search_radius_m = 50000
pekel_threshold = 20
working_crs = auto
```

These values are configurable and are described in detail in [Configuration](configuration.md).

---

## 3.3 Constructing the Search Region

The supplied dam coordinate is used as the centre of a search region.

Conceptually:

```text
                  search region
          ┌─────────────────────────┐
          │                         │
          │        water body       │
          │      ┌───────────┐      │
          │      │           │      │
          │      │      ●    │      │
          │      │     dam   │      │
          │      └───────────┘      │
          │                         │
          └─────────────────────────┘
```

The configured `search_radius_m` determines the spatial extent within which candidate surface-water regions are considered.

---

## 3.4 Surface-Water Mask

Within that search region, the JRC Global Surface Water occurrence layer is thresholded using:

```text
pekel_threshold
```

The occurrence value represents how frequently a location was identified as surface water in the underlying JRC record.

The threshold converts the occurrence layer into a water/non-water mask for reservoir-footprint extraction.

Conceptually:

```text
JRC water occurrence
        │
        │ occurrence >= threshold
        ▼
binary water mask
        │
        ▼
candidate water regions
```

Changing this threshold can therefore change the geometry identified around the supplied dam location.

---

## 3.5 Candidate Polygon Generation

The selected water mask is converted into candidate water-body geometries.

The package then determines which candidate geometry should represent the reservoir associated with the supplied dam coordinate.

The preferred case is a polygon that contains the dam point.

If multiple candidate polygons contain the point, the largest containing polygon is selected.

Conceptually:

```text
Candidate polygons
       │
       ├── contains dam? ── Yes ──► choose largest containing polygon
       │
       └── No
            │
            ▼
       choose nearest candidate polygon
```

The nearest-polygon behaviour allows the package to handle cases where the supplied dam coordinate does not fall exactly inside the extracted water mask.

---

## 3.6 Working Coordinate Reference System

Some geometric operations require a projected coordinate reference system rather than geographic longitude and latitude.

The package therefore uses the configured:

```text
working_crs
```

setting during the relevant spatial operations.

With:

```text
working_crs = auto
```

an appropriate projected CRS is selected automatically.

After reservoir identification is complete, the resulting footprint is represented in geographic coordinates for use by the downstream SWOT search and intersection stages.

---

# 4. Reservoir Polygon Cache

Generating the reservoir footprint requires communication with Google Earth Engine and geospatial processing that does not need to be repeated for every execution.

When:

```text
polygon_cache_enabled = true
```

the generated reservoir polygon is stored in the persistent reservoir-polygon cache.

The next time the same reservoir location is processed, the package can retrieve the existing geometry instead of generating it again.

The common beginning of the pipeline therefore behaves conceptually as:

```text
Dam coordinates
      │
      ▼
Check polygon cache
      │
      ├── cached ───────────────► load reservoir polygon
      │
      └── not cached
              │
              ▼
       Google Earth Engine
              │
              ▼
       generate reservoir
              │
              ▼
         cache polygon
              │
              ▼
       reservoir polygon
```

This cache is independent of the selected SWOT observation source. The same reservoir footprint can therefore be reused by both LakeSP and PIXC runs.

---

# 5. Source Dispatch

Once a reservoir polygon is available, the common reservoir-identification stage is complete.

The package then dispatches processing to the observation source requested by the user:

```text
--source lakesp
```

or:

```text
--source pixc
```

The architecture deliberately keeps these pipelines independent.

There is no sequence such as:

```text
try LakeSP
    ↓
if unavailable
    ↓
try PIXC
```

and there is no automatic source-selection mode.

Instead:

```text
                    Reservoir Polygon
                           │
                           ▼
                    Selected Source
                           │
                 ┌─────────┴─────────┐
                 │                   │
        source = lakesp       source = pixc
                 │                   │
                 ▼                   ▼
          LakeSP pipeline       PIXC pipeline
```

This matters scientifically because LakeSP and PIXC are different SWOT data products with different observation structures and different processing requirements.

---

# 6. LakeSP Processing Architecture

The LakeSP source operates on the SWOT Level-2 Lake Single Pass Observation Vector Product.

The configured collection is:

```text
SWOT_L2_HR_LakeSP_Obs_D
```

Unlike PIXC, LakeSP already provides vectorized lake observations. The package therefore works primarily with reservoir-associated LakeSP features rather than reconstructing a reservoir WSE directly from individual pixel-cloud measurements.

The LakeSP path is:

```text
Reservoir polygon
       │
       ▼
Earthdata / CMR search
       │
       ▼
Candidate LakeSP granules
       │
       ▼
Granule download / inspection
       │
       ▼
Spatial intersection with reservoir
       │
       ▼
Associated lake_id values
       │
       ▼
Extract LakeSP observations
       │
       ▼
Partial-observation screening
       │
       ▼
Quality-class screening
       │
       ▼
Daily aggregation
       │
       ▼
Daily quality assignment
       │
       ▼
Temporal MAD filtering
       │
       ▼
LakeSP reservoir WSE time series
```

Each stage serves a separate purpose.

---

# 7. LakeSP Product Search

The package first searches NASA Earthdata for LakeSP products that could contain observations of the target reservoir during the requested period.

The search is constrained by:

- the requested start and end dates;
- the spatial region surrounding the reservoir;
- the configured LakeSP collection;
- the configured science-cycle selection.

Relevant configuration includes:

```text
sources.lakesp.collection
sources.lakesp.search_buffer_degrees
sources.lakesp.science_cycles
```

The reservoir bounds are expanded by the configured search buffer before the Earthdata query.

This first search intentionally produces **candidate granules**.

A candidate returned by the metadata search is not yet assumed to contain a valid observation of the target reservoir.

That distinction is important:

```text
Earthdata search result
        ≠
confirmed reservoir observation
```

The metadata search narrows the amount of data that must be inspected. Actual reservoir association is established later.

---

# 8. LakeSP Granule Discovery and Spatial Verification

Candidate LakeSP products are inspected to determine whether their observations actually intersect the generated reservoir polygon.

Conceptually:

```text
Candidate LakeSP granule
          │
          ▼
Read observation geometry
          │
          ▼
Does an observation intersect
the reservoir polygon?
          │
      ┌───┴───┐
      │       │
     No      Yes
      │       │
 discard     ▼
          retain association
                │
                ▼
            lake_id
```

The relevant `lake_id` values are collected from intersecting observations.

These identifiers provide the connection between the generated reservoir geometry and the LakeSP observation records subsequently extracted from the products.

This two-stage design prevents a broad metadata search from being treated as proof that a granule actually contains the target reservoir.

---

# 9. LakeSP Granule Reuse

LakeSP products can be retained in a persistent granule cache when:

```text
lakesp_cache_enabled = true
```

This is separate from the reservoir polygon cache.

The two caches therefore serve different purposes:

```text
Reservoir polygon cache
        │
        └── avoids regenerating reservoir geometry

LakeSP granule cache
        │
        └── avoids downloading the same LakeSP products again
```

When a required LakeSP granule is already cached, the local copy can be reused during subsequent processing.

---

# 10. LakeSP Observation Extraction

Once reservoir-associated LakeSP observations have been identified, the package extracts the fields required for downstream processing.

The extraction stage produces observation records containing information including:

```text
lake_id
time_str
wse
wse_u
quality_f
partial_f
```

At this point, the data still represent individual LakeSP observation records.

They have not yet become the final reservoir time series.

The next stages determine which observations are usable and how multiple observations from the same acquisition date should be represented.

---

# 11. LakeSP Partial-Observation Screening

LakeSP observations can indicate that the observed lake geometry is only partial.

The package excludes observations marked as partial before daily WSE aggregation.

Conceptually:

```text
LakeSP observation
       │
       ▼
partial_f
       │
   ┌───┴────┐
   │        │
partial   accepted
   │        │
remove      ▼
        quality screening
```

This prevents incomplete observations from contributing to the final reservoir-level daily estimate.

---

# 12. LakeSP Quality Screening

LakeSP observations are then evaluated according to their configured quality classes.

The package exposes four quality classes:

```text
GOOD
SUSPECT
DEGRADED
BAD
```

The accepted classes are controlled through:

```text
sources.lakesp.accepted_quality_flags
```

The default configuration retains:

```text
good
suspect
degraded
```

and excludes:

```text
bad
```

This behaviour is configurable because users may require different quality restrictions for different analyses.

For example:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect
```

restricts processing to `GOOD` and `SUSPECT` observations.

Observations belonging to classes not permitted by the active configuration are removed before daily aggregation.

---

# 13. LakeSP Daily Aggregation

Multiple accepted LakeSP records can contribute observations on the same acquisition date.

The package therefore reduces the retained records into a daily reservoir-level representation.

For each acquisition date, the representative WSE is calculated from the retained observations using the daily median.

Conceptually:

```text
2026-02-01
    │
    ├── observation 1 ── WSE
    ├── observation 2 ── WSE
    └── observation 3 ── WSE
              │
              ▼
          daily median
              │
              ▼
       representative WSE
       for 2026-02-01
```

The result is no longer a collection of individual LakeSP records. It is a sequence of reservoir-level daily observations.

---

# 14. LakeSP Daily Quality Status

A representative quality status is also assigned to each acquisition date.

The daily status is determined from the retained quality classes contributing to that date.

The most frequent retained class becomes the daily quality status.

If multiple classes occur equally often, the poorer quality class is selected.

The final daily LakeSP observation therefore contains:

```text
date
wse_median
quality_status
```

This preserves a quality indication alongside the representative daily WSE rather than discarding quality information during aggregation.

---

# 15. LakeSP Temporal Outlier Filtering

Daily aggregation addresses multiple observations within an acquisition date, but a time series can still contain individual dates whose WSE is inconsistent with the rest of the reservoir record.

The LakeSP pipeline therefore applies a temporal Median Absolute Deviation (MAD) filtering stage.

The threshold is configured through:

```text
sources.lakesp.mad_threshold
```

with a default value of:

```text
3.0
```

Conceptually:

```text
daily LakeSP observations
          │
          ▼
       median WSE
          │
          ▼
absolute deviations
          │
          ▼
median absolute deviation
          │
          ▼
identify temporal outliers
          │
          ▼
filtered LakeSP time series
```

The purpose of this stage is different from LakeSP product-quality screening.

Product-quality screening asks:

```text
Does the SWOT product flag indicate that this observation should be retained?
```

Temporal filtering asks:

```text
Is this daily WSE statistically inconsistent with the reservoir's resulting time series?
```

These are therefore separate stages of the pipeline.

---

# 16. PIXC Processing Architecture

The PIXC source operates on the SWOT Level-2 High Rate Pixel Cloud Product.

The configured collection is:

```text
SWOT_L2_HR_PIXC_D
```

PIXC differs fundamentally from LakeSP.

LakeSP provides vectorized lake observations containing reservoir-level quantities that can be associated with the target reservoir.

PIXC provides geolocated pixel-cloud measurements.

The package must therefore determine which PIXC pixels belong to the reservoir, screen those pixels, calculate their WSE values, and aggregate them into a reservoir-level observation.

The PIXC path is:

```text
Reservoir polygon
       │
       ▼
Earthdata / CMR search
       │
       ▼
Candidate PIXC granules
       │
       ▼
CMR footprint verification
       │
       ▼
Verified PIXC granules
       │
       ▼
Download PIXC NetCDF product
       │
       ▼
Read pixel-cloud variables
       │
       ▼
Spatial reservoir filtering
       │
       ▼
Water/classification-quality screening
       │
       ▼
Compute pixel WSE
       │
       ▼
Daily pixel aggregation
       │
       ▼
Temporal MAD filtering
       │
       ▼
PIXC reservoir WSE time series
```

The additional pixel-level processing is the principal reason PIXC extraction can require considerably more memory, disk I/O, and processing time than LakeSP.

---

# 17. PIXC Product Search

PIXC discovery begins with a NASA Earthdata search constrained by:

- the requested observation period;
- the spatial search region;
- the configured PIXC collection;
- the configured science cycles.

Relevant configuration includes:

```text
sources.pixc.collection
sources.pixc.search_buffer_degrees
sources.pixc.science_cycles
```

As with LakeSP, the search result is treated as a set of candidate products rather than proof that each granule contains usable measurements of the target reservoir.

---

# 18. PIXC Footprint Verification

Before downloading and processing the full pixel-cloud product, candidate PIXC granules are checked using their CMR spatial metadata.

The candidate footprint is compared with the target reservoir polygon.

Conceptually:

```text
Candidate PIXC granule
          │
          ▼
CMR spatial footprint
          │
          ▼
Intersects reservoir?
          │
      ┌───┴───┐
      │       │
     No      Yes
      │       │
 discard      ▼
          download PIXC
```

This provides an early spatial rejection stage.

PIXC files can be large, so eliminating irrelevant candidates before full product processing avoids unnecessary downloads and pixel-level work.

---

# 19. PIXC Product Processing

Verified PIXC products are downloaded into temporary processing workspaces.

Unlike LakeSP granules, PIXC products are not currently maintained in a persistent PIXC granule cache.

Their lifecycle is therefore conceptually:

```text
verified candidate
       │
       ▼
temporary download
       │
       ▼
NetCDF processing
       │
       ▼
extract usable pixels
       │
       ▼
temporary product removed
```

The temporary workspace location is controlled by:

```text
temp_download_dir
```

---

# 20. Reservoir-Level Pixel Selection

A PIXC granule contains measurements over an area considerably broader than the target reservoir.

The package therefore uses the reservoir polygon to retain only pixel-cloud observations spatially associated with the target water body.

Conceptually:

```text
             PIXC pixels

     ·    ·     ·      ·     ·
        ·   ┌───────────┐
     ·      │ · · · · · │    ·
            │ · · · · · │
       ·    │ · · · · · │  ·
            └───────────┘
      ·        reservoir      ·


                 │
                 ▼

       retain pixels spatially
       associated with reservoir

                 │
                 ▼

             · · · · ·
             · · · · ·
             · · · · ·
```

Pixels outside the reservoir geometry do not contribute to the reservoir WSE estimate.

---

# 21. PIXC Classification and Quality Screening

Spatial membership alone does not make a PIXC pixel suitable for WSE estimation.

The PIXC source therefore applies product-specific screening to the selected pixels.

The configured water classification is controlled through:

```text
sources.pixc.water_classification
```

whose current default is:

```text
4
```

Only pixels satisfying the configured classification and the pipeline's classification-quality requirements are retained for aggregation.

The stages are therefore distinct:

```text
all PIXC pixels
       │
       ▼
inside reservoir?
       │
       ▼
required water classification?
       │
       ▼
classification quality acceptable?
       │
       ▼
usable reservoir pixels
```

This is fundamentally different from the LakeSP quality path because the PIXC source is screening individual pixel-cloud measurements rather than already-vectorized lake observations.

---

# 22. PIXC Pixel WSE

For each retained PIXC pixel, the package calculates the WSE used by the reservoir aggregation as:

```text
WSE = height - geoid
```

where the corresponding PIXC height and geoid quantities are used for the accepted pixel.

The output of this stage is therefore a collection of usable reservoir pixels, each with an associated WSE value.

Conceptually:

```text
Pixel 1 ──► WSE₁
Pixel 2 ──► WSE₂
Pixel 3 ──► WSE₃
   ...
Pixel n ──► WSEₙ
```

These pixel-level measurements must still be reduced to a representative reservoir observation.

---

# 23. PIXC Daily Aggregation

Accepted PIXC pixels are grouped by acquisition date.

The pixel WSE values contributing to a date are aggregated to obtain the representative reservoir WSE for that acquisition.

The PIXC aggregation stage also retains summary information describing the accepted pixel population.

The resulting daily records include the representative WSE together with statistics such as:

```text
mean WSE
WSE spread
accepted pixel count
mean water fraction
mean phase-noise standard deviation
```

The exact output schema is documented in [Outputs](outputs.md).

This conversion is the key transition in the PIXC pipeline:

```text
many individual pixel measurements
                │
                ▼
one reservoir-level observation
per acquisition date
```

---

# 24. PIXC Temporal Outlier Filtering

After daily aggregation, the PIXC reservoir observations pass through a temporal Median Absolute Deviation filtering stage.

The threshold is controlled through:

```text
sources.pixc.mad_threshold
```

with the default:

```text
3.0
```

As in the LakeSP pipeline, this stage operates on the resulting reservoir time series rather than on individual raw measurements.

The sequence is therefore:

```text
pixel-level screening
        │
        ▼
daily reservoir aggregation
        │
        ▼
temporal MAD filtering
        │
        ▼
final PIXC time series
```

---

# 25. LakeSP and PIXC Compared

The two source pipelines solve the same final problem but begin from different observation representations.

| Stage | LakeSP | PIXC |
| --- | --- | --- |
| Input product | Lake observation vector product | High-rate pixel cloud |
| Earthdata search | Yes | Yes |
| Science-cycle filtering | Yes | Yes |
| Reservoir spatial verification | Lake observation intersection | CMR footprint followed by pixel-level spatial filtering |
| Fundamental observation unit | LakeSP observation record | PIXC pixel |
| Reservoir association | Intersecting observations and `lake_id` | Pixel position relative to reservoir polygon |
| Product-level screening | Partial and LakeSP quality information | Water classification and classification-quality screening |
| WSE before daily aggregation | Product WSE observation | `height - geoid` for retained pixels |
| Daily aggregation | Across retained LakeSP observations | Across retained PIXC pixels |
| Temporal MAD filtering | Yes | Yes |
| Persistent product cache | Yes | No |
| Relative computational cost | Lower | Generally higher |

The architectural separation is therefore intentional.

Treating PIXC merely as another filename format for the LakeSP pipeline would be incorrect because the two products require fundamentally different reservoir-association and aggregation procedures.

---

# 26. Concurrency

Some granule-level work can be performed concurrently.

The maximum worker count is controlled through:

```text
max_workers
```

The default is derived from the available CPU count.

Conceptually:

```text
candidate granules
      │
      ├────► worker 1
      ├────► worker 2
      ├────► worker 3
      └────► worker n
                 │
                 ▼
           collected results
```

Concurrency is particularly important for product discovery and granule processing over longer observation periods.

It must, however, be considered differently for PIXC.

PIXC granules contain high-resolution pixel-cloud data, so processing several granules simultaneously can substantially increase memory use.

For systems with limited memory, `max_workers` can therefore be reduced:

```bash
swot-reservoir-wse config set max_workers 2
```

---

# 27. Output Layer

Both source pipelines eventually produce reservoir-level daily observations.

The output layer converts those observations into persistent user-facing products.

Every successful extraction generates a CSV file.

When:

```text
generate_plot = true
```

a PNG visualization is generated as well.

The output directory is controlled by:

```text
output_dir
```

and filenames include the dam coordinates and selected observation source.

For LakeSP:

```text
19.69000_73.34000_lakesp_wse.csv
19.69000_73.34000_lakesp_wse.png
```

For PIXC:

```text
19.69000_73.34000_pixc_wse.csv
19.69000_73.34000_pixc_wse.png
```

The source name is included because LakeSP and PIXC are independent processing products. Running both sources for the same reservoir therefore produces separate time series rather than silently combining their observations.

For field-level output documentation, see [Outputs](outputs.md).

---

# 28. Configuration in the Architecture

Configuration is loaded before processing and controls behaviour throughout the pipeline.

The architecture can therefore be viewed as two inputs entering the processing system:

```text
                    User Request
                         │
                         │
                         ▼
                   Processing Run
                         ▲
                         │
                  Active config.json
```

Configuration affects multiple stages:

```text
Reservoir identification
    ├── search_radius_m
    ├── pekel_threshold
    └── working_crs

Execution
    ├── max_workers
    └── generate_plot

Caching
    ├── polygon_cache_enabled
    ├── lakesp_cache_enabled
    └── cache_dir

LakeSP
    ├── collection
    ├── search_buffer_degrees
    ├── science_cycles
    ├── accepted_quality_flags
    └── mad_threshold

PIXC
    ├── collection
    ├── search_buffer_degrees
    ├── science_cycles
    ├── water_classification
    └── mad_threshold

Filesystem
    ├── output_dir
    └── temp_download_dir
```

The scientific meaning and validation rules for these parameters are documented in [Configuration](configuration.md).

---

# 29. Authentication in the Architecture

Authentication is configured separately from extraction, but two processing stages depend on authenticated services.

```text
Google Earth Engine credentials
            │
            ▼
Reservoir footprint generation


NASA Earthdata credentials
            │
            ▼
LakeSP / PIXC discovery and access
```

Normal extraction does not intentionally begin an interactive authentication procedure.

The required credentials are expected to have been configured beforehand using:

```bash
swot-reservoir-wse auth
```

This separation allows extraction commands to behave predictably in terminals, scripts, and repeatable processing workflows.

For credential handling and storage, see [Authentication](authentication.md).

---

# 30. End-to-End LakeSP Data Flow

The complete LakeSP path can now be represented as:

```text
User
 │
 │ latitude, longitude
 │ start date, end date
 │ source = lakesp
 ▼
Load configuration
 │
 ▼
Check reservoir polygon cache
 │
 ├── hit ─────────────────────────────┐
 │                                    │
 └── miss                             │
      │                               │
      ▼                               │
 Google Earth Engine                  │
      │                               │
 JRC Global Surface Water             │
      │                               │
 water occurrence threshold           │
      │                               │
 candidate water polygons             │
      │                               │
 reservoir selection                  │
      │                               │
      └──────────► reservoir polygon ◄─┘
                         │
                         ▼
                Earthdata LakeSP search
                         │
                         ▼
                 candidate granules
                         │
                         ▼
              inspect observation geometry
                         │
                         ▼
                reservoir intersection
                         │
                         ▼
                  associated lake_id
                         │
                         ▼
                extract observations
                         │
                         ▼
                 remove partial data
                         │
                         ▼
                quality-class screening
                         │
                         ▼
                   daily median WSE
                         │
                         ▼
                 daily quality status
                         │
                         ▼
                temporal MAD filtering
                         │
                         ▼
                 final LakeSP series
                         │
                ┌────────┴────────┐
                ▼                 ▼
               CSV           optional PNG
```

---

# 31. End-to-End PIXC Data Flow

The complete PIXC path is:

```text
User
 │
 │ latitude, longitude
 │ start date, end date
 │ source = pixc
 ▼
Load configuration
 │
 ▼
Check reservoir polygon cache
 │
 ├── hit ─────────────────────────────┐
 │                                    │
 └── miss                             │
      │                               │
      ▼                               │
 Google Earth Engine                  │
      │                               │
 JRC Global Surface Water             │
      │                               │
 water occurrence threshold           │
      │                               │
 candidate water polygons             │
      │                               │
 reservoir selection                  │
      │                               │
      └──────────► reservoir polygon ◄─┘
                         │
                         ▼
                 Earthdata PIXC search
                         │
                         ▼
                  candidate granules
                         │
                         ▼
                CMR footprint check
                         │
                         ▼
                  verified granules
                         │
                         ▼
               temporary PIXC download
                         │
                         ▼
                   read NetCDF data
                         │
                         ▼
               reservoir pixel selection
                         │
                         ▼
                 classification screening
                         │
                         ▼
              classification-quality check
                         │
                         ▼
                  retained water pixels
                         │
                         ▼
                 WSE = height - geoid
                         │
                         ▼
                  daily aggregation
                         │
                         ▼
                temporal MAD filtering
                         │
                         ▼
                  final PIXC series
                         │
                ┌────────┴────────┐
                ▼                 ▼
               CSV           optional PNG
```

---

# 32. Architectural Boundaries

The package can ultimately be understood as four cooperating layers:

```text
┌──────────────────────────────────────────────────────┐
│                    CLI / User Layer                  │
│                                                      │
│     extract       auth       config       cache      │
└──────────────────────────┬───────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────┐
│              Common Processing Layer                 │
│                                                      │
│ configuration     reservoir identification           │
│ authentication    caching                            │
└──────────────────────────┬───────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────┐
│                Observation Sources                   │
│                                                      │
│        LakeSP                    PIXC                 │
│                                                      │
│ search                     search                    │
│ discovery                  footprint verification    │
│ extraction                 pixel extraction          │
│ quality filtering          pixel screening           │
│ daily aggregation          daily aggregation         │
│ MAD filtering              MAD filtering             │
└──────────────────────────┬───────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────┐
│                     Output Layer                     │
│                                                      │
│                 CSV          PNG                     │
└──────────────────────────────────────────────────────┘
```

This separation is what allows **swot-reservoir-wse** to support multiple SWOT observation products without forcing product-specific assumptions into the common reservoir-identification or output components.

A future observation source can follow the same overall contract:

```text
reservoir polygon
      +
requested period
      ↓
source-specific processing
      ↓
reservoir-level WSE observations
```

while implementing its own product-specific discovery, extraction, screening, and aggregation logic.

---

# Related Documentation

For installation and external-service setup, see [Installation](installation.md).

For authentication and credential handling, see [Authentication](authentication.md).

For configurable processing parameters, see [Configuration](configuration.md).

For command syntax and options, see [Command Reference](command_reference.md).

For generated CSV fields and plots, see [Outputs](outputs.md).

For a practical first-use walkthrough, see [Usage](usage.md).
