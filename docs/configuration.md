# Configuration

**swot-wse** provides a centralized configuration system for controlling reservoir footprint generation, LakeSP and PIXC processing, parallel execution, caching, temporary storage, and output generation.

The default configuration is intended to provide a usable starting point for normal processing. Individual parameters can be changed without modifying the package source code.

Configuration should be changed deliberately when a workflow requires different:

- reservoir search settings;
- SWOT science cycles;
- observation-quality criteria;
- temporal outlier thresholds;
- processing concurrency;
- cache behaviour; or
- output and temporary-file locations.

---

# Configuration File

The active configuration is stored in:

```text
config.json
```

in the directory from which **swot-wse** is being used.

For example, if the command is run from:

```text
D:\reservoir-analysis
```

the runtime structure may contain:

```text
D:\reservoir-analysis
│
├── config.json
├── cache
├── downloads
└── outputs
```

The repository also contains:

```text
config.example.json
```

which provides an example configuration without user-specific values such as the Google Earth Engine Project ID.

`config.json` is runtime-specific and should not normally be committed to the repository.

---

# Viewing the Active Configuration

Display the complete active configuration with:

```bash
swot-wse config show
```

A configuration has the following general structure:

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

The exact Project ID, worker count, paths, and science-cycle list depend on the active configuration.

---

# Modifying Configuration

Change an individual parameter with:

```bash
swot-wse config set <key> <value>
```

For example:

```bash
swot-wse config set max_workers 4
```

Nested parameters use dotted notation:

```bash
swot-wse config set sources.lakesp.mad_threshold 2.5
```

or:

```bash
swot-wse config set sources.pixc.mad_threshold 2.5
```

Changes are written to `config.json` and used by subsequent executions.

---

# General Processing Parameters

## `max_workers`

```text
Default: max(1, CPU count - 1)
```

`max_workers` controls the maximum number of concurrent worker tasks used by processing stages that support parallel execution.

It is used during operations such as:

- LakeSP granule verification;
- LakeSP observation extraction; and
- PIXC granule processing.

For example:

```bash
swot-wse config set max_workers 4
```

allows up to four worker tasks to execute concurrently.

The value must be at least:

```text
1
```

Increasing the worker count can reduce runtime when multiple granules need to be processed, but it also increases simultaneous CPU, memory, network, and disk activity.

This is particularly important for PIXC processing because individual PIXC granules may contain large pixel-cloud datasets. A smaller worker count can substantially reduce memory pressure.

A larger value therefore does not necessarily produce faster execution.

---

## `generate_plot`

```text
Default: true
```

Controls whether a PNG visualization is produced together with the final CSV time series.

Disable plot generation:

```bash
swot-wse config set generate_plot false
```

Enable it again:

```bash
swot-wse config set generate_plot true
```

This setting affects only PNG generation. The CSV time series is still written when plotting is disabled.

---

# Google Earth Engine Configuration

## `earth_engine_project`

```text
Default: null
```

Stores the Google Cloud Project ID used when initializing Google Earth Engine.

The recommended way to configure the Project ID is:

```bash
swot-wse auth
```

or:

```bash
swot-wse auth --earth-engine-only
```

It can also be changed directly:

```bash
swot-wse config set earth_engine_project my-earth-engine-project
```

Clear the configured Project ID with:

```bash
swot-wse config set earth_engine_project none
```

Changing this value directly does **not** authenticate a Google account. It only changes the Project ID stored by the package.

For authentication behaviour, see [Authentication](authentication.md).

---

# Reservoir Footprint Configuration

These parameters control how the reservoir footprint is derived from the supplied dam coordinates using the JRC Global Surface Water dataset.

---

## `search_radius_m`

```text
Default: 50000
Unit: metres
```

Defines the radius around the supplied dam location within which candidate water-body polygons are generated.

The default value corresponds to:

```text
50 km
```

For example:

```bash
swot-wse config set search_radius_m 100000
```

changes the search radius to 100 km.

The value must be greater than `0`.

Increasing the radius allows more distant water bodies to be considered, but also expands the region processed during reservoir identification.

---

## `pekel_threshold`

```text
Default: 20
Unit: percent water occurrence
```

Controls the threshold applied to the JRC Global Surface Water `occurrence` layer.

Each occurrence value represents the percentage of available observations in which a pixel was classified as water.

The current implementation retains pixels satisfying:

```text
occurrence > pekel_threshold
```

With the default:

```text
pekel_threshold = 20
```

pixels with water occurrence greater than 20% contribute to the water mask used for candidate reservoir-polygon generation.

Change the threshold with:

```bash
swot-wse config set pekel_threshold 30
```

Accepted values range from:

```text
0 to 100
```

Changing this parameter directly alters the water mask and may therefore change the reservoir footprint generated by the package.

---

## `working_crs`

```text
Default: auto
```

Controls the projected Coordinate Reference System used for geometric calculations during reservoir-footprint selection.

With:

```text
working_crs = auto
```

the package estimates a suitable projected CRS for the generated geometries.

A CRS can also be supplied explicitly:

```bash
swot-wse config set working_crs EPSG:32643
```

Most users should retain:

```text
auto
```

unless a specific projected CRS is required.

---

# LakeSP Configuration

LakeSP-specific parameters are stored under:

```text
sources.lakesp
```

For example:

```text
sources.lakesp.mad_threshold
```

refers only to the LakeSP processing pipeline.

---

## `sources.lakesp.collection`

```text
Default: SWOT_L2_HR_LakeSP_Obs_D
```

Specifies the NASA Earthdata collection queried during LakeSP discovery.

The current LakeSP implementation is designed for the Version D LakeSP Observation product used by the package.

The value can be changed with:

```bash
swot-wse config set sources.lakesp.collection SWOT_L2_HR_LakeSP_Obs_D
```

This parameter should normally remain unchanged.

Changing the collection identifier does **not** automatically make the package compatible with another SWOT product or product version. Different products may use different files, fields, quality indicators, or structures and therefore require corresponding implementation support.

---

## `sources.lakesp.search_buffer_degrees`

```text
Default: 0.5
Unit: degrees
```

Controls the geographic buffer applied around the reservoir footprint during the initial NASA Earthdata LakeSP search.

For example:

```bash
swot-wse config set sources.lakesp.search_buffer_degrees 0.75
```

expands the search region.

The value cannot be negative.

This setting affects candidate discovery only. Candidate LakeSP granules are subsequently inspected against the reservoir footprint before their observations are accepted.

A larger buffer can therefore increase the number of candidate granules that need to be processed without necessarily increasing the number of valid reservoir observations.

---

## `sources.lakesp.science_cycles`

Controls which SWOT science cycles are accepted during LakeSP granule search.

The default configuration contains the package's current science-cycle list.

Restrict processing to selected cycles with:

```bash
swot-wse config set sources.lakesp.science_cycles 045,046,047
```

Values are normalized to three-digit cycle identifiers.

For example:

```bash
swot-wse config set sources.lakesp.science_cycles 45,46,47
```

is stored as:

```text
045
046
047
```

The active list can be inspected with:

```bash
swot-wse config show
```

Restricting science cycles can be useful when an analysis requires observations from only a particular period of the mission.

---

## `sources.lakesp.accepted_quality_flags`

```text
Default:
good
suspect
degraded
```

Controls which LakeSP quality classes are retained during observation-level filtering.

Supported values are:

```text
good
suspect
degraded
bad
```

By default, `BAD` observations are excluded.

Retain only `GOOD` observations:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good
```

Retain `GOOD` and `SUSPECT` observations:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good,suspect
```

Use the default three classes:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded
```

Retain all four classes:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded,bad
```

At least one valid quality class must be selected.

The configured names are case-normalized by the package, and duplicate values are removed.

LakeSP observations marked as partial are removed independently of this configuration.

After observation-level screening, retained observations are aggregated by acquisition date.

The daily `quality_status` reported by **swot-wse** is a package-derived representative status:

1. the most frequent retained quality class on that date is selected;
2. if two or more classes occur equally often, the poorer class is selected.

The ordering used for tie resolution is:

```text
GOOD < SUSPECT < DEGRADED < BAD
```

The daily quality status is therefore an aggregated package output rather than a direct copy of one individual LakeSP observation flag.

---

## `sources.lakesp.mad_threshold`

```text
Default: 3.0
```

Controls temporal outlier filtering after LakeSP observations have been quality-filtered and aggregated by acquisition date.

For each date, the median accepted WSE is used as the representative daily WSE.

The package calculates:

```text
MAD = median(|WSE - median(WSE)|)
```

and then the modified Z-score:

```text
modified_z = 0.6745 × |WSE - median(WSE)| / MAD
```

A daily observation is retained when:

```text
modified_z <= mad_threshold
```

With the default:

```text
mad_threshold = 3.0
```

observations with a modified Z-score greater than `3.0` are removed.

Change the threshold with:

```bash
swot-wse config set sources.lakesp.mad_threshold 2.5
```

The value must be greater than `0`.

A lower value applies stricter temporal filtering, while a larger value permits greater deviation from the median.

Because this setting can directly alter the final WSE time series, non-default values should be recorded when results are used for scientific analysis.

---

# PIXC Configuration

PIXC-specific parameters are stored under:

```text
sources.pixc
```

LakeSP and PIXC are independent observation sources. Changing PIXC parameters does not alter LakeSP processing and vice versa.

---

## `sources.pixc.collection`

```text
Default: SWOT_L2_HR_PIXC_D
```

Specifies the NASA Earthdata collection queried during PIXC metadata discovery.

Change it with:

```bash
swot-wse config set sources.pixc.collection SWOT_L2_HR_PIXC_D
```

The current implementation is designed around the Version D PIXC structure processed by **swot-wse**.

Changing the collection name alone does not provide compatibility with another product or product version.

---

## `sources.pixc.search_buffer_degrees`

```text
Default: 0.5
Unit: degrees
```

Controls the geographic buffer applied around the reservoir footprint during the initial PIXC metadata search.

For example:

```bash
swot-wse config set sources.pixc.search_buffer_degrees 0.75
```

The value cannot be negative.

This setting affects initial candidate discovery.

Candidate granules are subsequently checked using their NASA CMR geographic footprint metadata before their PIXC NetCDF files are processed.

---

## `sources.pixc.science_cycles`

Controls the SWOT science cycles retained during PIXC metadata search.

Restrict processing to selected cycles with:

```bash
swot-wse config set sources.pixc.science_cycles 045,046,047
```

Cycle values are normalized to three-digit strings in the same manner as LakeSP cycles.

For example:

```text
45 → 045
```

The active list can be displayed with:

```bash
swot-wse config show
```

---

## `sources.pixc.water_classification`

```text
Default: 4
```

Defines the PIXC `classification` value retained by the current PIXC extraction pipeline.

With the default:

```text
water_classification = 4
```

only PIXC points whose classification equals `4` proceed through the classification stage of the current pipeline.

Change the value with:

```bash
swot-wse config set sources.pixc.water_classification 4
```

Negative values are rejected.

This parameter directly affects which PIXC pixels contribute to reservoir WSE estimation and should therefore be changed only when the intended PIXC classification behaviour is understood.

---

## `sources.pixc.mad_threshold`

```text
Default: 3.0
```

Controls temporal outlier filtering for the daily PIXC reservoir WSE series.

Before MAD filtering, accepted PIXC pixels are grouped by acquisition date and the median pixel WSE is used as the representative daily reservoir elevation.

The same modified Z-score formulation used by the LakeSP pipeline is then applied:

```text
MAD = median(|WSE - median(WSE)|)
```

```text
modified_z = 0.6745 × |WSE - median(WSE)| / MAD
```

Daily observations are retained when:

```text
modified_z <= mad_threshold
```

Change the PIXC threshold with:

```bash
swot-wse config set sources.pixc.mad_threshold 2.5
```

The value must be greater than `0`.

The LakeSP and PIXC MAD thresholds are configured independently.

---

# Cache Configuration

## `polygon_cache_enabled`

```text
Default: true
```

Controls whether generated reservoir footprints are retained for reuse.

Disable reservoir-footprint caching:

```bash
swot-wse config set polygon_cache_enabled false
```

Enable it:

```bash
swot-wse config set polygon_cache_enabled true
```

When caching is enabled, an existing footprint for the same dam coordinates can be reused rather than generated again.

---

## `lakesp_cache_enabled`

```text
Default: true
```

Controls whether downloaded LakeSP granules are retained for later reuse.

Disable LakeSP caching:

```bash
swot-wse config set lakesp_cache_enabled false
```

Enable it:

```bash
swot-wse config set lakesp_cache_enabled true
```

When enabled, previously downloaded LakeSP granules can be reused during later runs.

PIXC granules are not currently maintained in a persistent PIXC granule cache. They are processed in temporary working directories and removed after processing.

---

## `cache_dir`

```text
Default: cache
```

Defines the root directory used for persistent package caches.

Change it with:

```bash
swot-wse config set cache_dir <path>
```

Example:

```bash
swot-wse config set cache_dir swot_cache
```

Relative paths are resolved from the working directory used by **swot-wse**.

The cache contains subdirectories for resources such as:

```text
reservoir_polygons
lakesp_granules
```

The current cache location and cache contents can also be inspected with:

```bash
swot-wse cache
```

---

# Temporary Processing Directory

## `temp_download_dir`

```text
Default: downloads/temp
```

Defines the workspace used for temporary processing files.

Change it with:

```bash
swot-wse config set temp_download_dir <path>
```

Example:

```bash
swot-wse config set temp_download_dir downloads/temp
```

This directory is used during operations such as:

- temporary LakeSP downloads and extraction;
- non-cached LakeSP processing; and
- PIXC granule download and NetCDF processing.

Temporary workspaces are removed when their processing stage finishes.

---

# Output Configuration

## `output_dir`

```text
Default: outputs
```

Defines the directory in which generated WSE products are written.

Change it with:

```bash
swot-wse config set output_dir <path>
```

Example:

```bash
swot-wse config set output_dir results
```

Relative paths are resolved from the current working directory.

Successful runs generate source-specific files such as:

```text
19.69000_73.34000_lakesp_wse.csv
19.69000_73.34000_lakesp_wse.png
```

or:

```text
19.69000_73.34000_pixc_wse.csv
19.69000_73.34000_pixc_wse.png
```

The PNG file is generated only when:

```text
generate_plot = true
```

---

# Accepted Value Formats

## Boolean Values

Boolean configuration parameters accept:

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

For example:

```bash
swot-wse config set generate_plot false
swot-wse config set polygon_cache_enabled yes
swot-wse config set lakesp_cache_enabled 0
```

---

## List Values

List configuration values may be supplied as comma-separated values.

For example:

```bash
swot-wse config set sources.lakesp.science_cycles 045,046,047
```

and:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded
```

JSON-style lists may also be supplied where shell quoting permits:

```text
["045","046","047"]
```

---

## Numeric Values

Numeric values are supplied directly:

```bash
swot-wse config set max_workers 4
swot-wse config set search_radius_m 50000
swot-wse config set pekel_threshold 30
swot-wse config set sources.lakesp.mad_threshold 2.5
swot-wse config set sources.pixc.mad_threshold 2.5
```

---

## Null Values

Configuration parameters whose default value is `null`, such as `earth_engine_project`, can be cleared with:

```bash
swot-wse config set earth_engine_project none
```

---

# Restoring the Default Configuration

Restore all configuration parameters with:

```bash
swot-wse config reset
```

This replaces the active configuration with the package defaults.

The reset includes:

- `earth_engine_project`;
- reservoir-footprint parameters;
- worker count;
- plotting behaviour;
- cache settings;
- runtime paths;
- LakeSP parameters; and
- PIXC parameters.

The Earth Engine Project ID is therefore restored to:

```text
null
```

The reset configuration can be inspected with:

```bash
swot-wse config show
```

`config reset` does **not** delete external authentication credentials.

In particular, it does not remove:

- Google-managed Earth Engine OAuth credentials; or
- NASA Earthdata credentials stored in the user's netrc file.

Authentication information managed by **swot-wse** can instead be removed with:

```bash
swot-wse auth --remove
```

See [Authentication](authentication.md) for details.

---

# Default Configuration Summary

| Parameter | Default |
| --- | --- |
| `earth_engine_project` | `null` |
| `search_radius_m` | `50000` |
| `pekel_threshold` | `20` |
| `working_crs` | `auto` |
| `max_workers` | `max(1, CPU count - 1)` |
| `generate_plot` | `true` |
| `polygon_cache_enabled` | `true` |
| `lakesp_cache_enabled` | `true` |
| `cache_dir` | `cache` |
| `output_dir` | `outputs` |
| `temp_download_dir` | `downloads/temp` |
| `sources.lakesp.collection` | `SWOT_L2_HR_LakeSP_Obs_D` |
| `sources.lakesp.search_buffer_degrees` | `0.5` |
| `sources.lakesp.mad_threshold` | `3.0` |
| `sources.lakesp.accepted_quality_flags` | `good, suspect, degraded` |
| `sources.pixc.collection` | `SWOT_L2_HR_PIXC_D` |
| `sources.pixc.search_buffer_degrees` | `0.5` |
| `sources.pixc.mad_threshold` | `3.0` |
| `sources.pixc.water_classification` | `4` |

The default science-cycle lists are defined by the package configuration and can be inspected with:

```bash
swot-wse config show
```

For all CLI forms and examples, see the [Command Reference](command_reference.md).

For the role of these settings in the complete processing pipeline, see [Package Architecture](architecture.md).