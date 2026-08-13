# Command Reference

This document provides the complete command-line reference for **swot-reservoir-wse**, including extraction, authentication, configuration, and cache-management commands.

---

# Display Available Commands

Display the top-level command groups:

```bash
swot-reservoir-wse --help
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
swot-reservoir-wse extract --help
swot-reservoir-wse auth --help
swot-reservoir-wse config --help
swot-reservoir-wse cache --help
```

Configuration subcommands also provide their own help pages:

```bash
swot-reservoir-wse config show --help
swot-reservoir-wse config set --help
swot-reservoir-wse config reset --help
```

---

# 1. Reservoir WSE Extraction

The `extract` command generates a reservoir-specific Water Surface Elevation (WSE) time series from a supplied dam location, date range, and SWOT observation source.

```bash
swot-reservoir-wse extract \
    --lat <latitude> \
    --lon <longitude> \
    --start-date YYYY-MM-DD \
    --end-date YYYY-MM-DD \
    --source {lakesp,pixc}
```

On Windows PowerShell, the command can be entered on one line:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

---

## Arguments

| Argument | Required | Description |
| --- | :---: | --- |
| `--lat` | Yes | Latitude of the dam location. |
| `--lon` | Yes | Longitude of the dam location. |
| `--start-date` | Yes | Beginning of the observation period in `YYYY-MM-DD` format. |
| `--end-date` | Yes | End of the observation period in `YYYY-MM-DD` format. |
| `--source` | Yes | SWOT observation source: `lakesp` or `pixc`. |

Latitude must satisfy:

```text
-90 <= latitude <= 90
```

Longitude must satisfy:

```text
-180 <= longitude <= 180
```

Both coordinates must be finite numeric values.

The start date must not be later than the end date.

The observation source is mandatory. There is no `auto` source and no automatic fallback between LakeSP and PIXC.

---

## LakeSP Extraction

Use the SWOT LakeSP pipeline with:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
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
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
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
swot-reservoir-wse auth
```

---

## Google Earth Engine Only

```bash
swot-reservoir-wse auth --earth-engine-only
```

Supply the Project ID directly:

```bash
swot-reservoir-wse auth --earth-engine-only --project-id my-earth-engine-project
```

---

## NASA Earthdata Only

```bash
swot-reservoir-wse auth --earthdata-only
```

If valid Earthdata credentials are already present in the user's netrc file, they are reused.

Otherwise, the package prompts for:

```text
Earthdata Login username:
Earthdata password:
```

---

## Force Reauthentication

Both services:

```bash
swot-reservoir-wse auth --force
```

Earth Engine only:

```bash
swot-reservoir-wse auth --earth-engine-only --force
```

Earthdata only:

```bash
swot-reservoir-wse auth --earthdata-only --force
```

Earth Engine with a different project:

```bash
swot-reservoir-wse auth --earth-engine-only --force --project-id another-earth-engine-project
```

The Project ID can also be supplied while forcing both services:

```bash
swot-reservoir-wse auth --force --project-id another-earth-engine-project
```

---

## Remove Authentication Information

Remove authentication information managed directly by **swot-reservoir-wse** for both services:

```bash
swot-reservoir-wse auth --remove
```

Earth Engine configuration only:

```bash
swot-reservoir-wse auth --earth-engine-only --remove
```

Earthdata credentials only:

```bash
swot-reservoir-wse auth --earthdata-only --remove
```

`--earth-engine-only --remove` removes the Project ID stored in the active `config.json`. It does not delete Google-managed OAuth credentials.

`--earthdata-only --remove` removes the `urs.earthdata.nasa.gov` entry managed by the package from the user's netrc file.

For authentication storage and behaviour, see [Authentication](authentication.md).

---

# 3. `config`

View, modify, or restore runtime configuration.

The active configuration is stored in:

```text
config.json
```

in the directory from which `swot-reservoir-wse` is being used.

The repository also provides:

```text
config.json
```

in the current **swot-wse working directory**.

---

# 3.1 `config show`

Display the complete active configuration.

```bash
swot-reservoir-wse config show
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
swot-reservoir-wse config set <key> <value>
```

Nested keys use dotted notation.

Example:

```bash
swot-reservoir-wse config set sources.lakesp.mad_threshold 2.5
```

The following sections list the supported configuration keys.

---

# 4. General Configuration

## `max_workers`

Set the maximum number of concurrent worker tasks:

```bash
swot-reservoir-wse config set max_workers 4
```

The value must be at least:

```text
1
```

The default is determined from the host CPU count:

```text
max(1, CPU count - 1)
```

A lower value may be preferable for PIXC processing when memory is limited.

---

## `generate_plot`

Enable PNG generation:

```bash
swot-reservoir-wse config set generate_plot true
```

Disable it:

```bash
swot-reservoir-wse config set generate_plot false
```

Disabling plot generation does not disable CSV generation.

---

# 5. Reservoir Footprint Configuration

## `search_radius_m`

```bash
swot-reservoir-wse config set earth_engine_project my-earth-engine-project
```

The value must be greater than `0`.

---

## `pekel_threshold`

```bash
swot-reservoir-wse config set earth_engine_project none
```

Accepted values are between:

```bash
swot-reservoir-wse auth
```

and:

```bash
swot-reservoir-wse auth --earth-engine-only
```

---

## `working_crs`

Use automatic projected CRS selection:

```bash
swot-reservoir-wse config set search_radius_m 100000
```

Or provide an explicit CRS:

```bash
swot-reservoir-wse config set pekel_threshold 30
```

A supplied CRS string is stored as configuration and is subsequently interpreted by the geospatial processing stack.

For guidance on changing reservoir-footprint parameters, see [Configuration](configuration.md).

---

# 6. Earth Engine Configuration

## `earth_engine_project`

Set the Project ID:

```bash
swot-reservoir-wse config set working_crs auto
```

Clear it:

```bash
swot-reservoir-wse config set working_crs EPSG:32643
```

---

# 7. LakeSP Configuration

LakeSP settings are located under:

```text
sources.lakesp
```

---

## `sources.lakesp.collection`

```bash
swot-reservoir-wse config set sources.lakesp.collection SWOT_L2_HR_LakeSP_Obs_D
```

Changing the collection string does not automatically make an incompatible LakeSP or other SWOT product supported by the package.

---

## `sources.lakesp.search_buffer_degrees`

```bash
swot-reservoir-wse config set sources.lakesp.search_buffer_degrees 0.75
```

The value cannot be negative.

---

## `sources.lakesp.science_cycles`

Restrict the source to selected science cycles:

```bash
swot-reservoir-wse config set sources.lakesp.science_cycles 045,046,047
```

Cycle numbers are normalized to three digits.

For example:

```bash
swot-reservoir-wse config set sources.lakesp.science_cycles 45,46,47
```

is stored as:

```text
045
046
047
```

The list must contain at least one valid positive cycle number.

---

## `sources.lakesp.mad_threshold`

```bash
swot-reservoir-wse config set sources.lakesp.mad_threshold 2.5
```

The value must be greater than `0`.

---

## `sources.lakesp.accepted_quality_flags`

Supported values are:

```text
good
suspect
degraded
bad
```

Default:

```text
good,suspect,degraded
```

Set the accepted classes with:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded
```

Retain only `GOOD` observations:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good
```

Retain `GOOD` and `SUSPECT`:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect
```

Retain all four classes:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded,bad
```

At least one valid quality class must be supplied.

Duplicate values are removed when the configuration is saved.

The final LakeSP daily `quality_status` is derived from the most frequent retained quality class contributing to that acquisition date. If multiple classes are equally frequent, the poorer quality class is selected.

---

# 8. PIXC Configuration

PIXC settings are located under:

```text
sources.pixc
```

---

## `sources.pixc.collection`

```bash
swot-reservoir-wse config set sources.pixc.collection SWOT_L2_HR_PIXC_D
```

---

## `sources.pixc.search_buffer_degrees`

```bash
swot-reservoir-wse config set sources.pixc.search_buffer_degrees 0.75
```

The value cannot be negative.

---

## `sources.pixc.science_cycles`

```bash
swot-reservoir-wse config set sources.pixc.science_cycles 045,046,047
```

Cycle numbers use the same normalization rules as LakeSP science cycles.

---

## `sources.pixc.mad_threshold`

```bash
swot-reservoir-wse config set sources.pixc.mad_threshold 2.5
```

The value must be greater than `0`.

---

## `sources.pixc.water_classification`

```bash
swot-reservoir-wse config set sources.pixc.water_classification 4
```

Default:

```text
4
```

Negative values are rejected.

For the scientific meaning of this setting, see [Configuration](configuration.md).

---

# 9. Cache Configuration

## `polygon_cache_enabled`

Enable reservoir polygon caching:

```bash
swot-reservoir-wse config set polygon_cache_enabled true
```

Disable it:

```bash
swot-reservoir-wse config set polygon_cache_enabled false
```

---

## `lakesp_cache_enabled`

Enable persistent LakeSP granule caching:

```bash
swot-reservoir-wse config set lakesp_cache_enabled true
```

Disable it:

```bash
swot-reservoir-wse config set lakesp_cache_enabled false
```

PIXC granules are currently processed through temporary working directories and are not retained in a persistent PIXC granule cache.

---

## `cache_dir`

```bash
swot-reservoir-wse config set cache_dir <path>
```

An absolute path can also be supplied:

```bash
swot-reservoir-wse config set cache_dir swot_cache
```

Relative paths are resolved from the working directory.

---

## Temporary Download Directory

```bash
swot-reservoir-wse config set temp_download_dir <path>
```

Example:

```bash
swot-reservoir-wse config set temp_download_dir downloads/temp
```

An absolute path can also be supplied.

---

# 10. Output Configuration

## `output_dir`

```bash
swot-reservoir-wse config set output_dir <path>
```

Example with an absolute path:

```bash
swot-reservoir-wse config set output_dir outputs
```

Relative paths are resolved from the working directory.

Source-specific output filenames follow the form:

```text
<latitude>_<longitude>_<source>_wse.csv
```

and, when plotting is enabled:

```text
<latitude>_<longitude>_<source>_wse.png
```

For example:

```text
19.69000_73.34000_lakesp_wse.csv
19.69000_73.34000_lakesp_wse.png

19.69000_73.34000_pixc_wse.csv
19.69000_73.34000_pixc_wse.png
```

---

# 11. Accepted Configuration Value Forms

## Boolean Values

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
swot-reservoir-wse config set generate_plot yes
swot-reservoir-wse config set polygon_cache_enabled 0
swot-reservoir-wse config set lakesp_cache_enabled on
```

---

# 12. Reset Configuration

Restore the package defaults:

```bash
swot-reservoir-wse config reset
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

The operation does **not** remove:

- Google-managed Earth Engine OAuth credentials;
- NASA Earthdata credentials stored in the user's netrc file;
- generated output files.

If authentication information also needs to be removed, use:

```bash
swot-reservoir-wse auth --remove
```

After resetting, the resulting configuration can be inspected with:

```bash
swot-wse config show
```

---

# 13. `cache`

Inspect or clear persistent cache data.

## Syntax

```bash
swot-reservoir-wse cache
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

The reported persistent cache currently contains reservoir polygons and LakeSP granules.

PIXC products are not included because the current PIXC pipeline does not persist downloaded granules.

---

## `--clear-polygons`

Remove cached reservoir footprints:

```bash
swot-reservoir-wse cache --clear-polygons
```

They will be regenerated when required by a later extraction.

---

## `--clear-lakesp`

Remove cached LakeSP granules:

```bash
swot-reservoir-wse cache --clear-lakesp
```

Required LakeSP products will be downloaded again when necessary.

---

## `--clear-all`

Remove all persistent cache data currently managed by the cache command:

```bash
swot-reservoir-wse cache --clear-all
```

This currently clears:

```text
reservoir polygon cache
LakeSP granule cache
```

It does not remove:

```text
config.json
authentication credentials
CSV outputs
PNG outputs
```

The cache-clearing options are mutually exclusive.

---

# Configuration Key Summary

| Key | Default |
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
| `sources.lakesp.science_cycles` | `001` through `052` |
| `sources.lakesp.mad_threshold` | `3.0` |
| `sources.lakesp.accepted_quality_flags` | `good,suspect,degraded` |
| `sources.pixc.collection` | `SWOT_L2_HR_PIXC_D` |
| `sources.pixc.search_buffer_degrees` | `0.5` |
| `sources.pixc.science_cycles` | `001` through `052` |
| `sources.pixc.mad_threshold` | `3.0` |
| `sources.pixc.water_classification` | `4` |

---

# Related Documentation

This page documents **what commands exist and how to invoke them**.

For the meaning of processing parameters, see:

[Configuration](configuration.md)

For credential storage and authentication behaviour, see:

[Authentication](authentication.md)

For the LakeSP and PIXC processing design, see:

[Package Architecture](architecture.md)

For generated files and output fields, see:

[Outputs](outputs.md)

For a guided first-use walkthrough, see:

[Usage](usage.md)
