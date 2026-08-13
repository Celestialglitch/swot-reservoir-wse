# Command Reference

This document provides the complete command-line reference for **swot-wse**, including extraction, authentication, configuration, and cache-management commands.

---

# Display Available Commands

Display the top-level command groups:

```bash
swot-wse --help
```

The current command groups are:

```text
extract
auth
config
cache
```

Display help for an individual command:

```bash
swot-wse extract --help
swot-wse auth --help
swot-wse config --help
swot-wse cache --help
```

Configuration subcommands also provide their own help pages:

```bash
swot-wse config show --help
swot-wse config set --help
swot-wse config reset --help
```

---

# 1. Reservoir WSE Extraction

The `extract` command generates a reservoir-specific Water Surface Elevation (WSE) time series from a supplied dam location, date range, and SWOT observation source.

```bash
swot-wse extract \
    --lat <latitude> \
    --lon <longitude> \
    --start-date YYYY-MM-DD \
    --end-date YYYY-MM-DD \
    --source <source>
```

On Windows PowerShell, the same command may be written on one line:

```bash
swot-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

## Arguments

| Argument | Required | Description |
| --- | :---: | --- |
| `--lat` | Yes | Latitude of the dam location. Must be between `-90` and `90`. |
| `--lon` | Yes | Longitude of the dam location. Must be between `-180` and `180`. |
| `--start-date` | Yes | Start date in `YYYY-MM-DD` format. |
| `--end-date` | Yes | End date in `YYYY-MM-DD` format. |
| `--source` | Yes | SWOT observation source. Supported values: `lakesp`, `pixc`. |

The start date must not be later than the end date.

There is no automatic source-selection or fallback mode. The source is selected explicitly for each run.

---

## LakeSP Extraction

Use the SWOT LakeSP pipeline with:

```bash
swot-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

The LakeSP workflow performs:

1. reservoir footprint generation or cache retrieval;
2. LakeSP metadata search;
3. granule-level spatial verification;
4. reservoir observation association using intersecting LakeSP observations;
5. configured quality-class filtering;
6. acquisition-day aggregation;
7. temporal MAD filtering; and
8. CSV and optional PNG output generation.

---

## PIXC Extraction

Use the SWOT PIXC pipeline with:

```bash
swot-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
```

The PIXC workflow performs:

1. reservoir footprint generation or cache retrieval;
2. PIXC metadata search;
3. CMR footprint verification;
4. PIXC NetCDF download and pixel-cloud extraction;
5. reservoir intersection and pixel filtering;
6. WSE calculation;
7. acquisition-day aggregation;
8. temporal MAD filtering; and
9. CSV and optional PNG output generation.

PIXC processing can require substantially more memory, disk I/O, and processing time than LakeSP because individual pixel-cloud granules are processed directly.

---

# 2. Authentication

The `auth` command manages authentication for:

- **Google Earth Engine**, used for reservoir footprint generation; and
- **NASA Earthdata**, used for SWOT product discovery and access.

---

## Authenticate Both Services

```bash
swot-wse auth
```

Existing credentials are reused when they are available and valid.

If the Google Earth Engine Project ID has not yet been stored, the package prompts for one.

If Earthdata credentials are unavailable or invalid, the package prompts for the Earthdata Login username and password.

---

## Google Earth Engine Only

```bash
swot-wse auth --earth-engine-only
```

Supply the Project ID directly:

```bash
swot-wse auth --earth-engine-only --project-id my-earth-engine-project
```

If no Project ID is supplied and none is stored, the package prompts for one.

The selected Project ID is stored in the active `config.json`.

---

## NASA Earthdata Only

```bash
swot-wse auth --earthdata-only
```

If valid Earthdata credentials are already present in the user's netrc file, they are reused.

Otherwise, the package prompts for:

```text
Earthdata Login username:
Earthdata password:
```

---

## Force Reauthentication

Force both services to authenticate again:

```bash
swot-wse auth --force
```

Force only Google Earth Engine:

```bash
swot-wse auth --earth-engine-only --force
```

Force only NASA Earthdata:

```bash
swot-wse auth --earthdata-only --force
```

A Project ID can also be supplied while forcing Earth Engine authentication:

```bash
swot-wse auth --earth-engine-only --force --project-id another-earth-engine-project
```

or while reauthenticating both services:

```bash
swot-wse auth --force --project-id another-earth-engine-project
```

---

## Remove Authentication Information

Remove authentication information managed directly by **swot-wse** for both services:

```bash
swot-wse auth --remove
```

Remove only the stored Earth Engine Project ID:

```bash
swot-wse auth --earth-engine-only --remove
```

Remove only the NASA Earthdata netrc entry:

```bash
swot-wse auth --earthdata-only --remove
```

Removing the Earth Engine configuration does not delete Google-managed OAuth credentials.

Removing Earthdata authentication removes the `urs.earthdata.nasa.gov` entry from the user's netrc file while preserving unrelated entries.

---

## Authentication Options

| Option | Description |
| --- | --- |
| `--project-id <project-id>` | Supplies the Google Earth Engine Project ID directly. |
| `--force` | Forces reauthentication instead of reusing existing credentials. |
| `--remove` | Removes authentication information managed by the package. |
| `--earth-engine-only` | Applies the operation only to Google Earth Engine. |
| `--earthdata-only` | Applies the operation only to NASA Earthdata. |

`--force` and `--remove` are mutually exclusive.

`--earth-engine-only` and `--earthdata-only` are mutually exclusive.

`--project-id` cannot be used with `--earthdata-only`.

For credential-storage details, see [Authentication](authentication.md).

---

# 3. Configuration

The `config` command manages runtime configuration.

The active configuration is stored in:

```text
config.json
```

in the directory from which `swot-wse` is being used.

The repository also provides:

```text
config.example.json
```

as a reference configuration.

---

## Display Configuration

```bash
swot-wse config show
```

This displays the complete active configuration, including:

- Earth Engine Project ID;
- reservoir-footprint parameters;
- worker count;
- plotting behavior;
- cache and output directories;
- LakeSP parameters; and
- PIXC parameters.

---

## Modify a Configuration Value

```bash
swot-wse config set <key> <value>
```

Nested configuration values use dotted notation.

Example:

```bash
swot-wse config set sources.lakesp.mad_threshold 2.5
```

---

# 4. General Configuration Parameters

## Maximum Worker Count

```bash
swot-wse config set max_workers 4
```

`max_workers` controls parallel granule processing.

The value must be at least `1`.

For PIXC processing, a smaller worker count may reduce memory pressure.

---

## Plot Generation

Enable plot generation:

```bash
swot-wse config set generate_plot true
```

Disable plot generation:

```bash
swot-wse config set generate_plot false
```

Accepted boolean forms are documented later in this reference.

---

# 5. Google Earth Engine Configuration

## Set the Project ID

```bash
swot-wse config set earth_engine_project my-earth-engine-project
```

## Clear the Project ID

```bash
swot-wse config set earth_engine_project none
```

Changing `earth_engine_project` only modifies configuration.

It does not itself perform Earth Engine authentication.

Authentication should normally be managed with:

```bash
swot-wse auth
```

or:

```bash
swot-wse auth --earth-engine-only
```

---

# 6. Reservoir Footprint Configuration

## Search Radius

```bash
swot-wse config set search_radius_m 100000
```

This controls the search radius used during reservoir-footprint generation.

The value must be greater than `0`.

---

## JRC Surface-Water Occurrence Threshold

```bash
swot-wse config set pekel_threshold 30
```

The accepted range is:

```text
0 to 100
```

---

## Working CRS

Use automatic projected CRS selection:

```bash
swot-wse config set working_crs auto
```

Specify a projected CRS explicitly:

```bash
swot-wse config set working_crs EPSG:32643
```

---

# 7. LakeSP Configuration

LakeSP parameters are located under:

```text
sources.lakesp
```

---

## LakeSP Collection

```bash
swot-wse config set sources.lakesp.collection SWOT_L2_HR_LakeSP_Obs_D
```

---

## LakeSP Search Buffer

```bash
swot-wse config set sources.lakesp.search_buffer_degrees 0.75
```

The search buffer cannot be negative.

---

## LakeSP Science Cycles

Restrict processing to selected science cycles:

```bash
swot-wse config set sources.lakesp.science_cycles 045,046,047
```

List values may be supplied as comma-separated values.

The configuration command normalizes cycle numbers to three-digit strings.

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

A JSON-style list may also be supplied where supported by the shell:

```text
["045","046","047"]
```

---

## LakeSP MAD Threshold

```bash
swot-wse config set sources.lakesp.mad_threshold 2.5
```

The value must be greater than `0`.

---

## LakeSP Accepted Quality Classes

The LakeSP pipeline can retain any combination of:

```text
good
suspect
degraded
bad
```

The default configuration is:

```text
good,suspect,degraded
```

Set the accepted classes with:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded
```

Retain only `GOOD` observations:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good
```

Retain `GOOD` and `SUSPECT`:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good,suspect
```

Retain all four classes:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded,bad
```

At least one valid LakeSP quality class must be selected.

Duplicate values are removed when the configuration is saved.

The final LakeSP daily `quality_status` is derived from the most frequent retained quality class contributing to that acquisition date. If multiple classes are equally frequent, the poorer quality class is selected.

---

# 8. PIXC Configuration

PIXC parameters are located under:

```text
sources.pixc
```

---

## PIXC Collection

```bash
swot-wse config set sources.pixc.collection SWOT_L2_HR_PIXC_D
```

---

## PIXC Search Buffer

```bash
swot-wse config set sources.pixc.search_buffer_degrees 0.75
```

The search buffer cannot be negative.

---

## PIXC Science Cycles

```bash
swot-wse config set sources.pixc.science_cycles 045,046,047
```

The same list and normalization rules used for LakeSP science cycles apply to PIXC.

---

## PIXC MAD Threshold

```bash
swot-wse config set sources.pixc.mad_threshold 2.5
```

The value must be greater than `0`.

---

## PIXC Water Classification

Set the PIXC classification value retained by the extraction pipeline:

```bash
swot-wse config set sources.pixc.water_classification 4
```

The default value is:

```text
4
```

Negative values are rejected.

---

# 9. Cache Configuration

## Reservoir Polygon Cache

Enable:

```bash
swot-wse config set polygon_cache_enabled true
```

Disable:

```bash
swot-wse config set polygon_cache_enabled false
```

---

## LakeSP Granule Cache

Enable:

```bash
swot-wse config set lakesp_cache_enabled true
```

Disable:

```bash
swot-wse config set lakesp_cache_enabled false
```

PIXC granules are currently processed in temporary working directories and are not retained in a persistent PIXC granule cache.

---

## Cache Directory

```bash
swot-wse config set cache_dir <path>
```

Example:

```bash
swot-wse config set cache_dir swot_cache
```

Absolute paths are also accepted.

---

## Temporary Download Directory

```bash
swot-wse config set temp_download_dir <path>
```

Example:

```bash
swot-wse config set temp_download_dir downloads/temp
```

This directory is used for temporary processing workspaces, including PIXC granule processing and temporary LakeSP extraction.

---

# 10. Output Configuration

## Output Directory

```bash
swot-wse config set output_dir <path>
```

Example:

```bash
swot-wse config set output_dir outputs
```

Relative paths are resolved from the current working directory.

Successful runs create source-specific filenames such as:

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

# 11. Accepted Boolean Values

Boolean configuration values accept:

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
swot-wse config set generate_plot yes
swot-wse config set polygon_cache_enabled 0
swot-wse config set lakesp_cache_enabled on
```

---

# 12. Reset Configuration

Restore the package defaults:

```bash
swot-wse config reset
```

This resets all configuration values, including:

- Earth Engine Project ID;
- reservoir-footprint settings;
- worker count;
- plotting behavior;
- cache paths;
- output paths;
- LakeSP parameters; and
- PIXC parameters.

The Earth Engine Project ID therefore becomes:

```text
null
```

`config reset` does not delete:

- Google-managed Earth Engine OAuth credentials; or
- NASA Earthdata credentials stored in the user's netrc file.

Use:

```bash
swot-wse auth --remove
```

when authentication information managed by the package must also be removed.

---

# 13. Cache Summary

Display the current cache status:

```bash
swot-wse cache
```

The command reports:

- the number of cached reservoir polygons;
- the number of cached LakeSP granules; and
- the active cache location.

Example structure:

```text
Cache Summary
-------------
Reservoir polygons : 1
LakeSP granules    : 21

Location : <cache-directory>
```

PIXC granules are not included because the current PIXC pipeline does not maintain a persistent granule cache.

---

# 14. Clear Reservoir Polygon Cache

```bash
swot-wse cache --clear-polygons
```

All cached reservoir footprints are removed.

A required footprint will be generated again during a later extraction run.

---

# 15. Clear LakeSP Granule Cache

```bash
swot-wse cache --clear-lakesp
```

Cached LakeSP granules are removed.

Required LakeSP granules will be downloaded again when needed.

---

# 16. Clear All Cached Data

```bash
swot-wse cache --clear-all
```

This clears:

- the reservoir polygon cache; and
- the LakeSP granule cache.

It does not remove:

- `config.json`;
- Earth Engine OAuth credentials;
- NASA Earthdata credentials;
- generated CSV files; or
- generated PNG files.

The cache-clearing options are mutually exclusive.

---

# Configuration Key Summary

| Key | Default |
| --- | --- |
| `earth_engine_project` | `null` |
| `search_radius_m` | `50000` |
| `pekel_threshold` | `20` |
| `working_crs` | `auto` |
| `max_workers` | System-dependent, capped by package defaults |
| `generate_plot` | `true` |
| `polygon_cache_enabled` | `true` |
| `lakesp_cache_enabled` | `true` |
| `cache_dir` | `cache` |
| `output_dir` | `outputs` |
| `temp_download_dir` | `downloads/temp` |
| `sources.lakesp.collection` | `SWOT_L2_HR_LakeSP_Obs_D` |
| `sources.lakesp.search_buffer_degrees` | `0.5` |
| `sources.lakesp.science_cycles` | `001` onward through the configured default cycle list |
| `sources.lakesp.mad_threshold` | `3.0` |
| `sources.lakesp.accepted_quality_flags` | `good,suspect,degraded` |
| `sources.pixc.collection` | `SWOT_L2_HR_PIXC_D` |
| `sources.pixc.search_buffer_degrees` | `0.5` |
| `sources.pixc.science_cycles` | `001` onward through the configured default cycle list |
| `sources.pixc.mad_threshold` | `3.0` |
| `sources.pixc.water_classification` | `4` |

For detailed explanations of individual processing parameters, see [Configuration](configuration.md).

For authentication and credential-storage behavior, see [Authentication](authentication.md).

For the end-to-end processing design, see [Package Architecture](architecture.md).