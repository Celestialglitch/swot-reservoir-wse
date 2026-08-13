# Package Architecture

**swot-reservoir-wse** is organized around a reservoir-centred processing workflow for generating Water Surface Elevation (WSE) time series from Surface Water and Ocean Topography (SWOT) science products.

A processing run begins with a dam location, an observation period, and a selected SWOT source. The dam coordinates are first converted into a representative reservoir footprint. That footprint is then used as the spatial reference for one of two independent observation-source pipelines:

- **SWOT Level 2 Lake Single-Pass Vector Data Product, Version D**
- **SWOT Level 2 Water Mask Pixel Cloud Data Product, Version D**

The two pipelines solve the same final problem—obtaining reservoir-level WSE observations—but operate on fundamentally different source representations.

LakeSP provides vector observations representing individual lakes and reservoirs together with product-level hydrological attributes. PIXC provides geolocated pixel-cloud observations from which reservoir pixels and their WSE values must be extracted directly.

For this reason, **swot-reservoir-wse** shares reservoir identification, configuration, authentication, caching, and output handling across sources while keeping the scientific processing logic for LakeSP and PIXC separate.

---

## 1. Processing Model

Every extraction requires:

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

At the highest level, the package performs three operations:

```text
Dam Location
     │
     ▼
Reservoir Footprint Generation
     │
     ▼
Selected SWOT Source Processing
     │
     ▼
Reservoir WSE Time Series Construction
```

The selected observation source determines the processing performed underneath it as shown below :

```text
                         User Request
                              │
                              ▼
                  Reservoir Footprint Generation
                              │
                              ▼
                      Source Selection
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
          LakeSP Processing          PIXC Processing
                 │                         │
                 ▼                         ▼
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    Output Generation
                              │
                       ┌──────┴──────┐
                       ▼             ▼
                      CSV       optional PNG
```

The two source branches remain independent throughout observation processing.

---

## 2. Reservoir Footprint Generation

The extraction interface accepts a latitude and longitude representing the dam.

A dam location, however, is only a single geographic point identified by its latitude and longitude , as supplied by the user.

However, the required WSE belongs to the water body behind the dam, not to that point.

Therefore, The package first generates a polygon representing the reservoir associated with the supplied dam coordinates.

### 2.1 Surface-Water Search Region

Reservoir footprint generation uses the **Joint Research Centre (JRC) Global Surface Water** dataset through **Google Earth Engine**.

A search region is created around the supplied dam location using:

```text
search_radius_m
```

Within this region, the JRC water-occurrence layer is retrieved.

Each occurrence value represents how frequently the corresponding location was observed as surface water within the JRC record.

The occurrence layer is thresholded using:

```text
pekel_threshold
```

to form a binary surface-water mask, that generates the water-body polygon.

The processing sequence is:

```text
Dam Location
     │
     ▼
Define Search Region
     │
     ▼
Retrieve JRC Water Occurrence
     │
     ▼
Apply Water-Occurrence Threshold
     │
     ▼
Binary Water Mask
     │
     ▼
Candidate Water-Body Polygons
```

---

### 2.2 Reservoir Polygon Selection

Several water bodies may exist within the search region.

The package therefore applies a geometric selection rule to identify a single representative reservoir polygon.

```text
Candidate polygons
       │
       ▼
Does a polygon contain the dam?
       │
   ┌───┴───┐
   │       │
  Yes      No
   │       │
   ▼       ▼
Select    Select
largest   nearest
containing polygon
polygon
   │       │
   └───┬───┘
       ▼
Reservoir Footprint
```

If the dam lies inside one or more candidate polygons, the largest containing polygon is selected.

If no candidate polygon contains the dam point, the nearest candidate polygon is selected.

The second case accounts for situations in which the recorded dam location lies just outside the extracted surface-water geometry.

---

### 2.3 Projected Geometry Coordinate System

Area and distance calculations are performed in a projected coordinate reference system.

The relevant setting in the current package is:

```text
working_crs
```

With the default setting :

```text
working_crs = auto
```

the package selects an appropriate projected CRS for the reservoir location.

After geometric selection is complete, the reservoir footprint is returned in geographic coordinates for use by the SWOT processing pipelines.

---

### 2.4 Reservoir Polygon Cache

Reservoir footprint generation does not need to be repeated for every run.

When:

```text
polygon_cache_enabled = true
```

the package checks the persistent reservoir-polygon cache before contacting Google Earth Engine.

```text
Dam Location
     │
     ▼
Check Polygon Cache
     │
 ┌───┴────────────┐
 │                │
Hit              Miss
 │                │
 ▼                ▼
Load           Generate
Polygon        Polygon
 │                │
 │             Cache
 │                │
 └───────┬────────┘
         ▼
 Reservoir Footprint
```

The cached footprint is independent of the SWOT source and can therefore be reused by both LakeSP and PIXC runs.

---

## 3. Observation-Source Selection

Once the reservoir footprint has been obtained, the common spatial-identification stage is complete.

The processing request is then dispatched according to:

```text
--source lakesp
```

or:

```text
--source pixc
```

```text
                    Reservoir Footprint
                           │
                           ▼
                     Selected Source
                           │
               ┌───────────┴───────────┐
               │                       │
               ▼                       ▼
        LakeSP Processing        PIXC Processing
```

The distinction between the two branches follows directly from the structure of the source products.

LakeSP contains **vectorized lake polygon level observations**.

PIXC contains **individual geolocated pixel level observations**.

Consequently, reservoir association, quality assessment, and WSE aggregation are performed differently in the two pipelines.

---

## 4. SWOT LakeSP Processing

The LakeSP pipeline processes reservoir observations from the SWOT Level 2 Lake Single-Pass vector product.

LakeSP provides water-body polygons and associated hydrological attributes, including WSE and product-quality information. The package therefore works primarily at the **individual lake-observation level** granularity .

The LakeSP workflow consists of four principal stages:

```text
LakeSP Granule Identification
           │
           ▼
Reservoir Polygon Association
           │
           ▼
WSE Quality Control and Aggregation
           │
           ▼
LakeSP WSE Time Series
```

---

### 4.1 LakeSP Granule Identification

The LakeSP archive contains granules containing observations acquired over many locations and mission cycles.

Only a small subset of these granules is relevant to a given reservoir and observation period.

The package therefore begins by querying NASA Earthdata for candidate LakeSP granules.

The search is constrained by:

```text
requested date range
reservoir spatial extent
LakeSP collection
configured science cycles
```

Relevant configuration values are:

```text
sources.lakesp.collection
sources.lakesp.search_buffer_degrees
sources.lakesp.science_cycles
```

The initial query is intentionally broad enough to identify potentially relevant products.

A returned granule is therefore considered a **candidate**, not yet a confirmed reservoir observation.

```text
Reservoir Footprint
       │
       ▼
Build Spatial Search Bounds
       │
       ▼
NASA Earthdata / CMR Search
       │
       ▼
Filter Configured Science Cycles
       │
       ▼
Remove Duplicate Product Records
       │
       ▼
Candidate LakeSP Granules
```

---

### 4.2 Reservoir Polygon Association

A candidate LakeSP granule may contain observations for many unrelated inland water bodies.

The package therefore performs a second spatial-association stage using the generated reservoir footprint.

The LakeSP observation layer is inspected and its geometries are intersected with the reservoir polygon.

```text
Candidate LakeSP Granule
          │
          ▼
Read LakeSP Observation Layer
          │
          ▼
Spatial Intersection
with Reservoir Footprint
          │
      ┌───┴───┐
      │       │
No Match     Match
      │       │
      ▼       ▼
 Discard   Retain Observation
                  │
                  ▼
             Collect lake_id
```

The `lake_id` values associated with intersecting observations are retained and used to isolate the relevant records during extraction.

This step transforms a granule-centred product containing many water bodies into a **reservoir-centred observation dataset**.

---

### 4.3 LakeSP Observation Extraction

Verified `lake_id` values are used to extract observations associated with the selected reservoir.

The downstream LakeSP processing uses fields including:

```text
lake_id
time_str
wse
wse_u
quality_f
partial_f
```

At this stage, the dataset still contains individual LakeSP observations.

Several observations may correspond to the same reservoir during the same acquisition date.

The observations must therefore undergo quality assessment before they can be converted into a reservoir-level daily record.

---

### 4.4 LakeSP WSE Quality Control and Aggregation

LakeSP observations pass through a multi-stage processing sequence.

```text
Reservoir-associated
LakeSP Observations
        │
        ▼
Partial-Observation Screening
        │
        ▼
LakeSP Quality-Class Screening
        │
        ▼
Daily WSE Aggregation
        │
        ▼
Daily Quality Assignment
        │
        ▼
Temporal MAD Filtering
        │
        ▼
Final LakeSP WSE Series
```

#### Partial-Observation Screening

Observations identified as partial are excluded before daily aggregation.

```text
partial_f = 0
```

This prevents observations representing incomplete water-body coverage from contributing to the final daily estimate.

---

#### Quality-Class Screening

The remaining observations are screened using the LakeSP quality information.

The package recognizes four classes:

```text
GOOD
SUSPECT
DEGRADED
BAD
```

The default configuration accepts:

```text
good
suspect
degraded
```

The quality policy can therefore be tightened or relaxed without modifying the source code.

---

#### Daily WSE Aggregation

Multiple accepted observations may occur on a single acquisition date.

The package groups those observations by date and uses their median WSE as the representative reservoir observation:

```text
Observation 1 ── WSE
Observation 2 ── WSE
Observation 3 ── WSE
       │
       ▼
   Daily Median
       │
       ▼
Representative Reservoir WSE
```

The observation unit has now changed from:

```text
individual LakeSP polygon
```

to:

```text
reservoir-level daily observation
```

---

#### Daily Quality Assignment

A representative quality status is retained for each daily LakeSP observation.

The most frequently occurring retained quality class among the contributing observations becomes the daily quality status.

If more than one class has the same frequency, the poorer class is selected.

The resulting daily LakeSP record contains:

```text
date
wse_median
quality_status
```

---

#### Temporal MAD Filtering

The daily sequence is finally screened for temporal outliers using the Median Absolute Deviation ( MAD)

The threshold is configured through:

```text
mad_threshold
```

This stage is deliberately separate from LakeSP product-quality screening.

```text
Product quality screening
        │
        │ evaluates individual
        │ LakeSP observations
        ▼
Daily aggregation
        │
        ▼
Temporal MAD filtering
        │
        │ evaluates the resulting
        │ reservoir time series
        ▼
Final LakeSP observations
```

The remaining daily observations form the final LakeSP-derived reservoir WSE time series.

---

### 4.5 LakeSP Granule Cache

LakeSP granules may be retained locally when:

```text
lakesp_cache_enabled = true
```

The cache avoids downloading the same SWOT product again during later processing.

NOTE: It is separate from the reservoir-polygon cache:

```text
Reservoir Polygon Cache
    └── generated reservoir geometries

LakeSP Granule Cache
    └── downloaded LakeSP products
```

---

## 5. SWOT PIXC Processing

The PIXC pipeline processes the SWOT Level 2 Water Mask Pixel Cloud product.

Unlike LakeSP, PIXC contains a **point-based representation of the observed water surface**.

Each retained observation is an individual geolocated pixel with associated measurements, classification information, and quality information.

A reservoir-level WSE therefore has to be constructed from the underlying pixel cloud.

The PIXC workflow consists of three principal stages:

```text
PIXC Granule Identification
          │
          ▼
Reservoir Pixel Extraction
and WSE Computation
          │
          ▼
Pixel Quality Control
and WSE Aggregation
          │
          ▼
PIXC WSE Time Series
```

---

### 5.1 PIXC Granule Identification

The first PIXC stage identifies products whose spatial coverage may contain the reservoir during the requested period.

NASA Earthdata is queried using:

```text
requested date range
reservoir spatial extent
PIXC collection
configured science cycles
```

Relevant configuration values are:

```text
collection
search_buffer_degrees
science_cycles
```

The returned products remain candidate granules until their spatial metadata are verified.

---

#### CMR Footprint Verification

The spatial footprint of each candidate PIXC granule is obtained from CMR metadata and compared with the reservoir footprint.

```text
Candidate PIXC Granule
          │
          ▼
CMR Spatial Footprint
          │
          ▼
Intersects Reservoir?
          │
      ┌───┴───┐
      │       │
     No      Yes
      │       │
      ▼       ▼
   Discard   Verify
```

Only verified granules proceed to full PIXC processing.

This early spatial rejection is particularly useful for PIXC because full pixel-cloud products can be considerably larger than LakeSP vector products.

---

### 5.2 Reservoir Pixel Extraction and WSE Computation

Verified PIXC products are downloaded into temporary processing workspaces and opened as NetCDF data.

The package reads the `pixel_cloud` group to obtain the variables required for reservoir-level processing.

These include measurements such as:

```text
longitude
latitude
height
geoid
classification
classification_qual
```

together with additional variables used in the resulting statistics.

---

#### Bounding-Box Prefilter

Before performing point-in-polygon processing, PIXC pixels are first screened using the geographic bounds of the reservoir.

```text
All PIXC Pixels
       │
       ▼
Reservoir Bounding Box
       │
       ▼
Candidate Reservoir Pixels
```

This inexpensive first step eliminates pixels that are clearly outside the target region.

---

#### Exact Reservoir Intersection

The remaining candidate pixels are converted to geographic point geometries and tested against the reservoir footprint.

```text
Candidate PIXC Pixels
         │
         ▼
Point Geometry
         │
         ▼
Inside Reservoir Polygon?
         │
     ┌───┴───┐
     │       │
    No      Yes
     │       │
     ▼       ▼
  Remove   Retain
```

Only pixels spatially associated with the reservoir polygon continue through the PIXC pipeline.

---

#### Pixel WSE Computation

PIXC pixel heights are referenced to the WGS84 ellipsoid.

For each retained pixel, the package derives Water Surface Elevation using:

```text
WSE = height - geoid
```

The result of this stage is therefore a reservoir-specific collection of pixel-level WSE observations.

```text
Pixel 1 ──► WSE₁
Pixel 2 ──► WSE₂
Pixel 3 ──► WSE₃
    ...
Pixel n ──► WSEₙ
```

These measurements still need to undergo PIXC-specific quality control before reservoir-level aggregation.

---

### 5.3 PIXC Quality Control and WSE Aggregation

The PIXC processing branch applies its own screening procedure.

It does **not** use the LakeSP `GOOD`, `SUSPECT`, `DEGRADED`, and `BAD` quality-class workflow, which is much more like a refined summary rather than the raw info.

Instead, filtering is performed using PIXC classification and classification-quality information.

```text
Reservoir PIXC Pixels
        │
        ▼
Water Classification Filter
        │
        ▼
Classification-Quality Screening
        │
        ▼
Accepted Water Pixels
        │
        ▼
Daily Reservoir Aggregation
        │
        ▼
Temporal MAD Filtering
        │
        ▼
Final PIXC WSE Series
```

---

#### Water Classification

The retained water class is controlled by:

```text
water_classification
```

The current default is:

```text
4
```

Only pixels matching the configured classification enter the subsequent quality and aggregation stages.

---

#### Classification-Quality Screening

PIXC observations also contain the `classification_qual` bitmask.

The pipeline removes pixels containing the classification-quality conditions excluded by the current PIXC processing logic.

This screening operates at the **pixel level**, in contrast to the observation-level quality classes used by LakeSP.

---

#### Daily WSE Aggregation

After spatial and quality screening, all accepted PIXC pixels from the same acquisition date are combined into a reservoir-level observation.

The median pixel WSE is used as the representative daily value.

```text
Accepted reservoir pixels
for one acquisition
         │
         ├── WSE₁
         ├── WSE₂
         ├── WSE₃
         ├── ...
         └── WSEₙ
               │
               ▼
          Median WSE
               │
               ▼
      Daily Reservoir WSE
```

The PIXC workflow also retains descriptive statistics for the accepted pixel population, including WSE distribution and pixel-level diagnostic information.

The complete output schema is described in [Outputs](outputs.md).

---

#### Temporal MAD Filtering

The resulting daily PIXC WSE sequence is subjected to temporal Median Absolute Deviation filtering.

The threshold is configured independently through:

```text
mad_threshold
```

The complete PIXC reduction is therefore:

```text
Raw PIXC Pixel Cloud
       │
       ▼
Reservoir Pixel Selection
       │
       ▼
Classification and Quality Screening
       │
       ▼
Pixel WSE Computation
       │
       ▼
Daily Reservoir Aggregation
       │
       ▼
Temporal MAD Filtering
       │
       ▼
Final PIXC WSE Time Series
```

---

### 5.4 PIXC Temporary Data Lifecycle

Since, the pipeline operates directly on high-resolution pixel-cloud products, PIXC processing can require more memory, disk activity, and processing time than LakeSP processing.

PIXC products are currently processed through temporary working directories.

They are not stored in a persistent PIXC granule cache.

```text
Verified PIXC Granule
        │
        ▼
Temporary Download
        │
        ▼
NetCDF Processing
        │
        ▼
Extract Reservoir Pixels
        │
        ▼
Retain Processed Observations
        │
        ▼
Remove Temporary Workspace
```

The temporary workspace is configured as:

```text
temp_download_dir
```

---

## 6. Reservoir WSE Time Series Construction

The final product of either source pipeline is a chronological sequence of reservoir-level WSE observations.

The source remains explicit throughout the workflow.

A LakeSP run produces a LakeSP-derived time series and a PIXC run produces a PIXC-derived time series:

The two products are not automatically combined.

Each successful extraction is written independently through the common output layer.

---

## 7. LakeSP and PIXC Processing Compared

The architectural difference between the two sources can be summarized directly.

| Processing Stage | LakeSP | PIXC |
| --- | --- | --- |
| Source representation | Vector water-body observations | Geolocated pixel cloud |
| Discovery service | NASA Earthdata / CMR | NASA Earthdata / CMR |
| Initial spatial verification | Lake observation geometry | CMR granule footprint |
| Reservoir association | Intersecting observations and `lake_id` | Individual pixels within reservoir footprint |
| Fundamental processing unit | LakeSP observation | PIXC pixel |
| Product screening | Partial flag and LakeSP quality class | Water classification and `classification_qual` |
| WSE input | Product WSE field | `height - geoid` |
| Reservoir aggregation | Across retained LakeSP observations | Across retained PIXC pixels |
| Daily representative value | Median WSE | Median WSE |
| Daily LakeSP-style quality status | Yes | No |
| Temporal MAD filtering | Yes | Yes |
| Persistent granule cache | Supported | Not currently used |
| Typical processing demand | Lower | Higher |

This separation is deliberate.

The two pipelines share a common spatial target—the reservoir footprint—but differ in how observations of that target are represented, selected, screened, and aggregated.

---

## 8. Output Generation

Both source pipelines use the same output interface.

Every successful processing run writes a CSV file containing the final source-specific reservoir WSE time series.

When:

```text
generate_plot = true
```

a PNG visualization is generated as well.

Example LakeSP outputs:

```text
19.69000_73.34000_lakesp_wse.csv
19.69000_73.34000_lakesp_wse.png
```

Example PIXC outputs:

```text
19.69000_73.34000_pixc_wse.csv
19.69000_73.34000_pixc_wse.png
```

The output directory is configured as:

```text
output_dir
```

For field definitions and plotting behaviour, see [Outputs](outputs.md).

---

## 9. Runtime Configuration

Processing behaviour is controlled by the active `config.json`.

Configuration is based on several layers of the architecture:

```text
Reservoir Footprint Generation
    ├── search_radius_m
    ├── pekel_threshold
    └── working_crs

Execution
    └── max_workers

Reservoir Cache
    └── polygon_cache_enabled

LakeSP
    ├── collection
    ├── search_buffer_degrees
    ├── science_cycles
    ├── accepted_quality_flags
    ├── mad_threshold
    └── lakesp_cache_enabled

PIXC
    ├── collection
    ├── search_buffer_degrees
    ├── science_cycles
    ├── water_classification
    └── mad_threshold

Filesystem and Outputs
    ├── cache_dir
    ├── temp_download_dir
    ├── output_dir
    └── generate_plot
```

Configuration changes the behaviour of individual processing stages without changing their architectural roles.

For detailed parameter descriptions, see [Configuration](configuration.md).

---

## 10. Authentication

Two authenticated external services are used by the processing system.

```text
Google Earth Engine
        │
        ▼
Reservoir Footprint Generation


NASA Earthdata
        │
        ▼
LakeSP and PIXC Product Access
```

Authentication is configured separately using:

```bash
swot-reservoir-wse auth
```

Normal extraction expects the required authentication state to exist before processing begins.

For credential storage and authentication behaviour, see [Authentication](authentication.md).

---

## 11. Parallel Processing

Granule-level processing can be performed concurrently.

The maximum number of workers is controlled through:

```text
max_workers
```

Conceptually:

```text
Granules
   │
   ├────► Worker 1
   ├────► Worker 2
   ├────► Worker 3
   └────► Worker n
              │
              ▼
        Combined Results
```

PIXC workloads require particular care because multiple pixel-cloud products processed simultaneously can substantially increase memory consumption.

A lower worker count can therefore be configured when necessary:


---

## 12. Complete LakeSP Data Flow

```text
User Input
    │
    ▼
Load Configuration
    │
    ▼
Reservoir Polygon Cache
    │
    ├── available ────────────────┐
    │                             │
    └── unavailable               │
            │                     │
            ▼                     │
     Google Earth Engine          │
            │                     │
     JRC Global Surface Water     │
            │                     │
     Surface-Water Threshold      │
            │                     │
     Candidate Water Polygons     │
            │                     │
     Reservoir Selection          │
            │                     │
            └────► Reservoir ◄────┘
                     Polygon
                       │
                       ▼
              LakeSP Granule Search
                       │
                       ▼
               Candidate Granules
                       │
                       ▼
             Observation Geometry
                  Verification
                       │
                       ▼
              Reservoir Association
                       │
                       ▼
                Associated lake_id
                       │
                       ▼
               Observation Extraction
                       │
                       ▼
              Partial-Flag Screening
                       │
                       ▼
              Quality-Class Screening
                       │
                       ▼
                Daily Median WSE
                       │
                       ▼
              Daily Quality Status
                       │
                       ▼
               Temporal MAD Filter
                       │
                       ▼
              Final LakeSP WSE Series
                       │
                  ┌────┴────┐
                  ▼         ▼
                 CSV    optional PNG
```

---

## 13. Complete PIXC Data Flow

```text
User Input
    │
    ▼
Load Configuration
    │
    ▼
Reservoir Polygon Cache
    │
    ├── available ────────────────┐
    │                             │
    └── unavailable               │
            │                     │
            ▼                     │
     Google Earth Engine          │
            │                     │
     JRC Global Surface Water     │
            │                     │
     Surface-Water Threshold      │
            │                     │
     Candidate Water Polygons     │
            │                     │
     Reservoir Selection          │
            │                     │
            └────► Reservoir ◄────┘
                     Polygon
                       │
                       ▼
               PIXC Granule Search
                       │
                       ▼
                Candidate Granules
                       │
                       ▼
               CMR Footprint Check
                       │
                       ▼
                Verified Granules
                       │
                       ▼
               Temporary Download
                       │
                       ▼
               Read Pixel Cloud
                       │
                       ▼
               Bounding-Box Filter
                       │
                       ▼
              Reservoir Intersection
                       │
                       ▼
              Water Classification
                       │
                       ▼
           Classification-Quality
                   Screening
                       │
                       ▼
                Accepted Pixels
                       │
                       ▼
               WSE = height - geoid
                       │
                       ▼
                Daily Median WSE
                       │
                       ▼
               Temporal MAD Filter
                       │
                       ▼
               Final PIXC WSE Series
                       │
                  ┌────┴────┐
                  ▼         ▼
                 CSV    optional PNG
```

---

## 14. Architectural Summary

The package can be viewed as four cooperating layers:

```text
┌───────────────────────────────────────────────────────┐
│                     User Interface                    │
│                                                       │
│        extract        auth        config       cache   │
└──────────────────────────┬────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────┐
│                  Shared Spatial Layer                 │
│                                                       │
│       configuration      reservoir identification     │
│       authentication     reservoir polygon cache      │
└──────────────────────────┬────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────┐
│                Observation-Source Layer               │
│                                                       │
│          LakeSP                     PIXC              │
│                                                       │
│ granule identification       granule identification   │
│ polygon association          footprint verification   │
│ observation extraction       reservoir pixel extraction│
│ LakeSP quality control       PIXC pixel quality control│
│ daily aggregation            daily aggregation        │
│ temporal filtering           temporal filtering       │
└──────────────────────────┬────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────┐
│                     Output Layer                      │
│                                                       │
│                   CSV        PNG                      │
└───────────────────────────────────────────────────────┘
```

The main architectural boundary lies between the shared **reservoir-identification layer** and the independent **SWOT observation-source pipelines**.

Each supported source receives the same reservoir footprint and requested observation period, but remains responsible for its own:

```text
product discovery
spatial association
observation extraction
source-specific quality control
reservoir-level aggregation
temporal screening
```

This allows additional SWOT observation products to be incorporated without forcing LakeSP- or PIXC-specific assumptions into the common reservoir-identification and output components.

---

## Related Documentation

For installation and service setup, see [Installation](installation.md).

For a practical extraction walkthrough, see [Usage](usage.md).

For all command syntax and options, see [Command Reference](command_reference.md).

For authentication and credential management, see [Authentication](authentication.md).

For processing parameters, see [Configuration](configuration.md).

For generated CSV fields and plots, see [Outputs](outputs.md).
