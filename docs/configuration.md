# Configuration

**swot-reservoir-wse** uses a centralized runtime configuration to control reservoir footprint generation, SWOT product discovery and processing, quality control, parallel execution, caching, temporary storage, and output generation.

Most users can begin with the default configuration. However, parameters can be changed when a processing workflow requires different spatial search settings, SWOT science cycles, observation-quality criteria, temporal filtering thresholds, computational resources, or filesystem locations.

The parameters documented here correspond directly to stages of the processing system described in [Package Architecture](architecture.md). This page focuses on the configuration values that control those stages.

---

## 1. Configuration File

The active configuration is stored in:

```text
config.json
```

in the directory from which **swot-reservoir-wse** is being used.

For example:

```text
reservoir-analysis/
│
├── config.json
├── cache/
├── downloads/
└── outputs/
```

The repository also provides:

```text
config.example.json
```

as a reference configuration without user-specific values.

`config.json` represents the runtime configuration of the current working directory.

---

## 2. Configuration Structure

The configuration is completely based on the processing architecture.

```text
Configuration
│
├── External Service Configuration
│   └── earth_engine_project
│
├── Reservoir Footprint Generation
│   ├── search_radius_m
│   ├── pekel_threshold
│   └── working_crs
│
├── Observation Sources
│   │
│   ├── LakeSP
│   │   ├── collection
│   │   ├── search_buffer_degrees
│   │   ├── science_cycles
│   │   ├── accepted_quality_flags
│   │   └── mad_threshold
│   │
│   └── PIXC
│       ├── collection
│       ├── search_buffer_degrees
│       ├── science_cycles
│       ├── water_classification
│       └── mad_threshold
│
├── Parallel Execution
│   └── max_workers
│
├── Persistent Caching
│   ├── polygon_cache_enabled
│   ├── lakesp_cache_enabled
│   └── cache_dir
│
├── Runtime Storage
│   ├── temp_download_dir
│   └── output_dir
│
└── Output Generation
    └── generate_plot
```

LakeSP and PIXC parameters are intentionally maintained separately because the two products use different observation representations and quality-control procedures.

Two authenticated external services participate in this processing architecture:

- **Google Earth Engine** is used during reservoir-footprint generation through the JRC Global Surface Water dataset.
- **NASA Earthdata** is used for SWOT LakeSP and PIXC product discovery and access.

Authentication itself is documented separately in [Authentication](authentication.md). 
---

## 3. Viewing and Modifying Configuration

Display the complete active configuration with:

```bash
swot-reservoir-wse config show
```

A typical configuration has the following structure:

```json
{
  "earth_engine_project": null,
  "search_radius_m": 50000,
  "pekel_threshold": 20,
  "working_crs": "auto",
  "max_workers": 4,
  "generate_plot": true,
  "polygon_cache_enabled": true,
  "lakesp_cache_enabled": true,
  "cache_dir": "cache",
  "output_dir": "outputs",
  "temp_download_dir": "downloads/temp",
  "sources": {
    "lakesp": {
      "collection": "SWOT_L2_HR_LakeSP_Obs_D",
      "search_buffer_degrees": 0.5,
      "science_cycles": [
        "001",
        "002",
        "003"
      ],
      "mad_threshold": 3.0,
      "accepted_quality_flags": [
        "good",
        "suspect",
        "degraded"
      ]
    },
    "pixc": {
      "collection": "SWOT_L2_HR_PIXC_D",
      "search_buffer_degrees": 0.5,
      "science_cycles": [
        "001",
        "002",
        "003"
      ],
      "mad_threshold": 3.0,
      "water_classification": 4
    }
  }
}
```

The exact Earth Engine Project ID, worker count, paths, and science-cycle lists depend on the active configuration.

Individual values are changed with:

```bash
swot-reservoir-wse config set <key> <value>
```

For example:

```bash
swot-reservoir-wse config set max_workers 4
```

Nested source-specific parameters use dotted notation:

```bash
swot-reservoir-wse config set sources.lakesp.mad_threshold 2.5
```

```bash
swot-reservoir-wse config set sources.pixc.mad_threshold 2.5
```

Changes are written to the active `config.json` and used by subsequent executions.

---

## 4. External Services

The processing pipeline uses two authenticated external services:

| Service | Used For | Runtime Configuration |
| --- | --- | --- |
| **Google Earth Engine** | JRC Global Surface Water access for reservoir-footprint generation | `earth_engine_project` |
| **NASA Earthdata** | Discovery and access of LakeSP and PIXC products | No parameter in `config.json` |

Both services require authentication before they can be used by the processing pipeline:

```bash
swot-reservoir-wse auth
```

They can also be authenticated independently:

```bash
swot-reservoir-wse auth --earth-engine-only
```

```bash
swot-reservoir-wse auth --earthdata-only
```

The difference is where the information required by each service is maintained.

Google Earth Engine requires a Google Cloud Project ID in addition to its authentication credentials. The Project ID is therefore part of the runtime configuration and is stored as:

```text
earth_engine_project
```

NASA Earthdata does not require an equivalent processing parameter in `config.json`. Its username and password are authentication credentials rather than package configuration values and are stored separately in the user's netrc credential file after successful authentication.

Credential storage, validation, reauthentication, and removal for both services are documented in [Authentication](authentication.md).

---

### 4.1 `earth_engine_project`

```text
Default: null
```

Stores the Google Cloud Project ID used when initializing Google Earth Engine for reservoir-footprint generation.

It is normally configured during Earth Engine authentication:

```bash
swot-reservoir-wse auth --earth-engine-only
```

or when authenticating both required services:

```bash
swot-reservoir-wse auth
```

The value may also be set directly:

```bash
swot-reservoir-wse config set earth_engine_project my-earth-engine-project
```

or cleared:

```bash
swot-reservoir-wse config set earth_engine_project none
```

The Project ID is configuration information rather than an authentication credential. This is particularly effective for multiple authenticated accounts only. However, setting it directly therefore does not authenticate Google Earth Engine.

NASA Earthdata has no corresponding configuration key. Its credentials are managed through the authentication system rather than through `config set`.

For complete authentication behaviour, see [Authentication](authentication.md).

---

## 5. Reservoir Footprint Generation

The following parameters control the conversion of a supplied dam location into the reservoir polygon used by both SWOT processing pipelines.

These settings affect the common reservoir-identification stage before processing is delegated to either LakeSP or PIXC.

---

### 5.1 `search_radius_m`

```text
Default: 50000
Unit: metres
Valid range: > 0
```

Defines the radius of the search region constructed around the supplied dam coordinates.

The default corresponds to:

```text
50 km
```

For example:

```bash
swot-reservoir-wse config set search_radius_m 100000
```

uses a 100 km search radius.

Increasing the radius expands the area from which candidate water-body polygons can be generated.

---

### 5.2 `pekel_threshold`

```text
Default: 20
Unit: percent water occurrence
Valid range: 0–100
```

Controls the threshold applied to the JRC Global Surface Water `occurrence` layer during water-mask generation.

Each occurrence value represents the percentage of available observations in which the corresponding pixel was classified as surface water.

The current implementation retains pixels satisfying:

```text
occurrence > pekel_threshold
```

With the default:

```text
pekel_threshold = 20
```

pixels with water occurrence greater than 20% contribute to the binary water mask.

Changing this parameter can alter the shape and connectivity of the extracted water mask and therefore the reservoir footprint selected by the package.

---

### 5.3 `working_crs`

```text
Default: auto
```

Controls the projected Coordinate Reference System used for geometric operations during reservoir-footprint selection.

With:

```text
working_crs = auto
```

the package selects an appropriate projected CRS for the location being processed.

A CRS may also be supplied explicitly:

```bash
swot-reservoir-wse config set working_crs EPSG:32643
```

Most users should retain `auto` unless a particular projected coordinate system is required for their workflow.

The selected reservoir footprint is returned to geographic coordinates before downstream SWOT processing.

---

## 6. LakeSP Processing

LakeSP-specific parameters are stored under:

```text
sources.lakesp
```

These settings affect only the LakeSP processing branch.

LakeSP granule discovery and access are performed through NASA Earthdata using the collection, spatial search region, requested observation period, and configured science cycles.

---

### 6.1 `sources.lakesp.collection`

```text
Default: SWOT_L2_HR_LakeSP_Obs_D
```

Specifies the NASA Earthdata collection queried during LakeSP granule discovery.

The current implementation is designed around the Version D LakeSP Observation product.

Changing this identifier does **not** make the package automatically compatible with another SWOT product or version. Other products may expose different file structures, attributes, identifiers, or quality information and may therefore require corresponding implementation changes.

---

### 6.2 `sources.lakesp.search_buffer_degrees`

```text
Default: 0.5
Unit: degrees
Valid range: >= 0
```

Controls the geographic buffer applied around the reservoir bounds during the initial NASA Earthdata search.
By default, the reservoir bounding box is expanded by **0.5° in each geographic direction** before the product search is performed.


This parameter affects **candidate granule discovery**, not final reservoir association.

Candidate products are subsequently inspected spatially against the reservoir footprint. Increasing the buffer may therefore increase the number of products that must be inspected without increasing the number of valid reservoir observations.

---

### 6.3 `sources.lakesp.science_cycles`

Controls which SWOT science cycles are retained during LakeSP discovery.

For example:

```bash
swot-reservoir-wse config set sources.lakesp.science_cycles 045,046,047
```

Cycle numbers are normalized to three-digit identifiers:

```text
45  →  045
46  →  046
47  →  047
```

---

### 6.4 `sources.lakesp.accepted_quality_flags`

```text
Default: good, suspect, degraded
```

Controls which LakeSP observation-quality classes are allowed to contribute to reservoir WSE estimation.

Supported values are:

```text
good
suspect
degraded
bad
```

The default configuration therefore excludes `BAD` observations while retaining the other three classes.

Examples:

```bash
# GOOD observations only
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good

# GOOD and SUSPECT
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect

# Default behaviour
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded
```

At least one valid class must be selected.

Values are case-normalized and duplicate entries are removed.

#### Daily Quality Status

After screening, retained observations from the same acquisition date are aggregated.

The package assigns a representative `quality_status` to the daily observation.

The most frequent retained quality class is selected. If several classes occur equally often, the poorer class is used according to:

```text
GOOD < SUSPECT < DEGRADED < BAD
```

The reported daily status is therefore a **package-derived aggregate**, not a copy of an individual LakeSP quality flag.

---

### 6.5 `sources.lakesp.mad_threshold`

```text
Default: 3.0
Valid range: > 0
```

Controls temporal outlier removal after accepted LakeSP observations have been aggregated by acquisition date.

For daily WSE values:

```text
x₁, x₂, ..., xₙ
```

the time-series median is:

```text
M = median(x)
```

and the Median Absolute Deviation is:

```text
MAD = median(|xᵢ - M|)
```

The package evaluates each daily observation using:

```text
modified_z = 0.6745 × |xᵢ - M| / MAD
```

and retains observations satisfying:

```text
modified_z <= mad_threshold
```

With:

```text
mad_threshold = 3.0
```

daily observations with a modified Z-score greater than `3.0` are removed.

For example:

```bash
swot-reservoir-wse config set sources.lakesp.mad_threshold 2.5
```

applies a stricter threshold.

A lower threshold removes observations closer to the central WSE distribution, while a higher threshold permits larger deviations.

---

## 7. PIXC Processing

PIXC-specific parameters are stored under:

```text
sources.pixc
```

PIXC configuration is intentionally separate from LakeSP configuration because PIXC processing operates on individual pixel-cloud observations rather than LakeSP water-body vectors.

These settings affect the independent PIXC processing branch.

PIXC granule discovery and access are performed through NASA Earthdata. Candidate products are subsequently subjected to the PIXC-specific spatial and pixel-level processing stages described in [Package Architecture](architecture.md).

---

### 7.1 `sources.pixc.collection`

```text
Default: SWOT_L2_HR_PIXC_D
```

Specifies the NASA Earthdata collection queried during PIXC granule discovery.

The current implementation is designed for the Version D PIXC product.

Likewise, changing the collection identifier alone does not make the package compatible with a different product structure or version.

This setting should normally remain unchanged.

---

### 7.2 `sources.pixc.search_buffer_degrees`

```text
Default: 0.5
Unit: degrees
Valid range: >= 0
```

Controls the geographic buffer applied around the reservoir during initial PIXC metadata discovery.

This setting affects candidate discovery only.

Candidate granules are subsequently checked using their NASA CMR geographic footprint metadata before their PIXC NetCDF files are processed.

---

### 7.3 `sources.pixc.science_cycles`

Controls which SWOT science cycles are retained during PIXC discovery.

For example:

```bash
swot-reservoir-wse config set sources.pixc.science_cycles 045,046,047
```

Cycle identifiers are normalized to three digits:

```text
45 → 045
```

The configured list can be inspected with:

```bash
swot-reservoir-wse config show
```

LakeSP and PIXC cycle lists are independent and may therefore be configured differently.

---

### 7.4 `sources.pixc.water_classification`

```text
Default: 4
Valid range: >= 0
```

Defines the PIXC `classification` value retained from the `pixel_cloud` group of the product by the current pixel-processing pipeline.

With:

```text
water_classification = 4
```

only pixels satisfying:

```text
classification == 4
```

continue through this stage.

This parameter changes which PIXC pixels can contribute to the reservoir WSE estimate and should therefore be modified only when the intended PIXC classification behaviour is understood.

---

### 7.5 `sources.pixc.mad_threshold`

```text
Default: 3.0
Valid range: > 0
```

Controls temporal outlier filtering after accepted PIXC pixels have been reduced to daily reservoir-level WSE observations.

For each acquisition date, the representative reservoir WSE is obtained from the median of the accepted pixel WSE values.

The resulting daily sequence is then evaluated using the same MAD-based formulation used for LakeSP.

For example:

```bash
swot-reservoir-wse config set sources.pixc.mad_threshold 2.5
```

The LakeSP and PIXC thresholds are independent:

```text
sources.lakesp.mad_threshold
sources.pixc.mad_threshold
```

---

## 8. Parallel Execution

### 8.1 `max_workers`

```text
Default: max(1, CPU_core_count - 1)
Valid range: >= 1
```

Controls the maximum number of concurrent workers used by processing stages that support parallel execution.

Parallel work includes operations such as LakeSP granule inspection and extraction and PIXC granule processing.

```text
Granules
   │
   ├────► Worker 1
   ├────► Worker 2
   ├────► Worker 3
   └────► Worker n
              │
              ▼
        Collected Results
```

For example:

```bash
swot-reservoir-wse config set max_workers 4
```

allows up to four worker tasks to operate concurrently.

Increasing this value may reduce processing time when many products are involved, but it also increases simultaneous CPU, network, disk, and memory use.

This is particularly important for PIXC because several high-resolution pixel-cloud granules processed concurrently can consume substantial memory.

> **Note:** A larger worker count should therefore not automatically be interpreted as better performance.

---

## 9. Caching

The package maintains two independent persistent caches.

```text
Persistent Cache
│
├── Reservoir Polygon Cache
│   └── generated reservoir footprints
│
└── LakeSP Granule Cache
    └── downloaded LakeSP products
```

PIXC products are currently processed through temporary workspaces rather than a persistent PIXC product cache.

---

### 9.1 `polygon_cache_enabled`

```text
Default: true
```

Controls whether generated reservoir footprints are stored for reuse.

When enabled, the package can reuse an existing footprint for the same dam coordinates instead of repeating Google Earth Engine processing.

Disable it with:

```bash
swot-reservoir-wse config set polygon_cache_enabled false
```

Enable it again with:

```bash
swot-reservoir-wse config set polygon_cache_enabled true
```

---

### 9.2 `lakesp_cache_enabled`

```text
Default: true
```

Controls whether downloaded LakeSP products are retained for subsequent processing runs.

When enabled, a locally cached granule can be reused instead of being downloaded again.

Disable it with:

```bash
swot-reservoir-wse config set lakesp_cache_enabled false
```

Enable it again with:

```bash
swot-reservoir-wse config set lakesp_cache_enabled true
```

This setting does not apply to PIXC products.

---

### 9.3 `cache_dir`

```text
Default: cache
```

Defines the root directory for persistent package caches.

The directory contains resources such as:

```text
cache/
│
├── reservoir_polygons/
└── lakesp_granules/
```

A different location can be configured with:

```bash
swot-reservoir-wse config set cache_dir swot_cache
```

An absolute path may also be supplied.

For example, on Windows PowerShell:

```powershell
swot-reservoir-wse config set cache_dir D:\SWOT\cache
```

Relative paths are resolved from the working directory used by **swot-reservoir-wse**.

Cache information can be inspected with:

```bash
swot-reservoir-wse cache
```

---

## 10. Temporary Processing

### 10.1 `temp_download_dir`

```text
Default: downloads/temp
```

Defines the root directory used for temporary SWOT product downloads and intermediate processing files.

This directory is used by **both the LakeSP and PIXC pipelines**, although their use of temporary storage differs.

For **LakeSP**, it provides temporary workspace for product download and extraction when a granule is not being reused from or retained in the persistent LakeSP granule cache.

For **PIXC**, it provides the temporary workspace for downloading and processing PIXC NetCDF products. PIXC granules are not currently maintained in a persistent product cache because of memory constraints and are therefore processed through temporary workspaces.

Conceptually:

```text
temp_download_dir
│
├── LakeSP
│   └── temporary download / extraction workspace
│
└── PIXC
    └── temporary download / NetCDF processing workspace
```


Temporary per-product workspaces are removed after their processing stage has completed.

This directory should therefore be distinguished from:

```text
cache_dir
```

which stores persistent reusable data such as reservoir polygons and, when enabled, cached LakeSP granules.

## 11. Output Generation

### 11.1 `output_dir`

```text
Default: outputs
```

Defines the directory in which final WSE products are written.

For example:

```bash
swot-reservoir-wse config set output_dir results
```

An absolute output path can also be supplied.

For example, on Windows PowerShell:

```powershell
swot-reservoir-wse config set output_dir D:\SWOT\outputs
```

A LakeSP extraction may produce:

```text
19.69000_73.34000_lakesp_wse.csv
19.69000_73.34000_lakesp_wse.png
```

while a PIXC extraction may produce:

```text
19.69000_73.34000_pixc_wse.csv
19.69000_73.34000_pixc_wse.png
```

Relative paths are resolved from the current working directory.

---

### 11.2 `generate_plot`

```text
Default: true
```

Controls whether a PNG visualization is generated together with the CSV time series.

Disable plotting with:

```bash
swot-reservoir-wse config set generate_plot false
```

Enable it again with:

```bash
swot-reservoir-wse config set generate_plot true
```

The setting affects only plot generation.

The CSV output is still written when:

```text
generate_plot = false
```

---

## 12. Value Formats

The `config set` command converts command-line values according to the expected configuration type.

### Boolean Values

Boolean parameters accept:

```text
true
false
1
0
yes
no
on
off
```

Examples:

```bash
swot-reservoir-wse config set generate_plot false
swot-reservoir-wse config set polygon_cache_enabled yes
swot-reservoir-wse config set lakesp_cache_enabled 0
```

---

### List Values

List parameters can be supplied as comma-separated values.

For example:

```bash
swot-reservoir-wse config set sources.lakesp.science_cycles 045,046,047
```

```bash
swot-reservoir-wse config set sources.pixc.science_cycles 045,046,047
```

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded
```

JSON-style lists may also be supplied where shell quoting permits:

```text
["045","046","047"]
```

---

### Numeric Values

Integer and floating-point parameters are supplied directly:

```bash
swot-reservoir-wse config set max_workers 4
swot-reservoir-wse config set search_radius_m 50000
swot-reservoir-wse config set pekel_threshold 30
swot-reservoir-wse config set sources.lakesp.mad_threshold 2.5
swot-reservoir-wse config set sources.pixc.mad_threshold 2.5
```

---

### Null Values

Nullable parameters such as:

```text
earth_engine_project
```

can be cleared using:

```bash
swot-reservoir-wse config set earth_engine_project none
```

---

## 13. Restoring Defaults

Restore the complete configuration with:

```bash
swot-reservoir-wse config reset
```

This replaces the active configuration with the package defaults, including:

```text
Earth Engine Project ID
reservoir-footprint parameters
worker configuration
plotting behaviour
cache configuration
runtime paths
LakeSP parameters
PIXC parameters
```

The Earth Engine Project ID is therefore reset to:

```text
null
```

The restored configuration can be inspected with:

```bash
swot-reservoir-wse config show
```

Configuration reset does **not** remove authentication credentials maintained outside `config.json`.

In particular, it does not delete Google-managed Earth Engine OAuth credentials or NASA Earthdata credentials stored in the user's netrc file.

Use:

```bash
swot-reservoir-wse auth --remove
```

for authentication information managed directly by **swot-reservoir-wse**.

See [Authentication](authentication.md) for the distinction between configuration and credentials.

---

## 14. Default Configuration Reference

| Parameter | Default | Processing Role |
| --- | --- | --- |
| `earth_engine_project` | `null` | Earth Engine initialization |
| `search_radius_m` | `50000` | Reservoir search region |
| `pekel_threshold` | `20` | JRC water-mask generation |
| `working_crs` | `auto` | Reservoir geometry operations |
| `max_workers` | `max(1, CPU count - 1)` | Parallel processing |
| `generate_plot` | `true` | PNG output generation |
| `polygon_cache_enabled` | `true` | Reservoir footprint caching |
| `lakesp_cache_enabled` | `true` | LakeSP product caching |
| `cache_dir` | `cache` | Persistent cache location |
| `output_dir` | `outputs` | Final output location |
| `temp_download_dir` | `downloads/temp` | Temporary processing workspace |
| `sources.lakesp.collection` | `SWOT_L2_HR_LakeSP_Obs_D` | LakeSP product discovery |
| `sources.lakesp.search_buffer_degrees` | `0.5` | LakeSP candidate search |
| `sources.lakesp.mad_threshold` | `3.0` | LakeSP temporal filtering |
| `sources.lakesp.accepted_quality_flags` | `good, suspect, degraded` | LakeSP observation screening |
| `sources.pixc.collection` | `SWOT_L2_HR_PIXC_D` | PIXC product discovery |
| `sources.pixc.search_buffer_degrees` | `0.5` | PIXC candidate search |
| `sources.pixc.mad_threshold` | `3.0` | PIXC temporal filtering |
| `sources.pixc.water_classification` | `4` | PIXC pixel selection |

The default LakeSP and PIXC science-cycle lists are maintained by the package configuration and can be inspected with:

```bash
swot-reservoir-wse config show
```

---

## Related Documentation

For the complete processing sequence and the role of each configurable stage, see [Package Architecture](architecture.md).

For authentication and credential storage, see [Authentication](authentication.md).

For complete command syntax and CLI options, see [Command Reference](command_reference.md).

For generated CSV fields and plots, see [Outputs](outputs.md).

For a practical extraction workflow, see [Usage](usage.md).
