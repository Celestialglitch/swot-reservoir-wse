# Command Reference

This page is the complete command-line reference for **swot-wse**.

The CLI contains four command groups:

```text
extract
auth
config
cache
```

Display the top-level help page with:

```bash
swot-wse --help
```

Command-specific help is available through:

```bash
swot-wse extract --help
swot-wse auth --help
swot-wse config --help
swot-wse cache --help
```

The `config` command also contains three subcommands:

```bash
swot-wse config show --help
swot-wse config set --help
swot-wse config reset --help
```

---

# Typical Workflows

The following examples show complete command sequences for a new working directory.

They are intended as practical examples of how the individual commands fit together. The remaining sections document each command separately.

---

## LakeSP Example

Suppose the target dam is located at:

```text
Latitude  : 19.690
Longitude : 73.340
```

and the required observation period is:

```text
2026-01-20 to 2026-07-16
```

### 1. Authenticate

Run:

```bash
swot-wse auth
```

If the Earth Engine Project ID has not yet been configured, the package asks for it.

If valid NASA Earthdata credentials are not already available, the package also requests the Earthdata Login username and password.

---

### 2. Inspect the configuration

```bash
swot-wse config show
```

The default LakeSP quality classes are:

```text
good
suspect
degraded
```

To use those defaults, no configuration change is required.

For example, if only `GOOD` and `SUSPECT` observations should be accepted:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good,suspect
```

---

### 3. Run LakeSP extraction

```bash
swot-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

With the default output directory, successful products are written under:

```text
outputs/
```

with filenames such as:

```text
19.69000_73.34000_lakesp_wse.csv
19.69000_73.34000_lakesp_wse.png
```

---

### 4. Inspect the cache

```bash
swot-wse cache
```

If the same reservoir or LakeSP products are required again, cached data can be reused when caching is enabled.

---

## PIXC Example

The same reservoir can be processed independently using PIXC.

### 1. Authenticate

If authentication has already been configured for the current working directory, this step normally does not need to be repeated.

Otherwise:

```bash
swot-wse auth
```

---

### 2. Select an appropriate worker count

PIXC products are considerably larger than LakeSP vector products.

On systems with limited memory, reducing parallel processing is recommended:

```bash
swot-wse config set max_workers 4
```

or:

```bash
swot-wse config set max_workers 2
```

---

### 3. Inspect the PIXC configuration

```bash
swot-wse config show
```

For example, processing can be restricted to selected SWOT science cycles:

```bash
swot-wse config set sources.pixc.science_cycles 045,046,047
```

---

### 4. Run PIXC extraction

```bash
swot-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
```

Successful products are written with source-specific names such as:

```text
19.69000_73.34000_pixc_wse.csv
19.69000_73.34000_pixc_wse.png
```

LakeSP and PIXC are independent processing sources. Running one does not automatically invoke the other.

---

# 1. `extract`

Generate a reservoir-specific Water Surface Elevation (WSE) time series from the selected SWOT observation source.

## Syntax

```bash
swot-wse extract \
    --lat <latitude> \
    --lon <longitude> \
    --start-date YYYY-MM-DD \
    --end-date YYYY-MM-DD \
    --source {lakesp,pixc}
```

On Windows PowerShell, the command can be entered on one line:

```powershell
swot-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
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

## LakeSP

```bash
swot-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

LakeSP-specific processing and quality-control behaviour are described in [Package Architecture](architecture.md) and [Configuration](configuration.md).

---

## PIXC

```bash
swot-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
```

PIXC-specific processing is described in [Package Architecture](architecture.md).

Because PIXC processing operates on pixel-cloud products, resource use can be considerably higher than for LakeSP. `max_workers` can be reduced when necessary.

---

# 2. `auth`

Manage Google Earth Engine and NASA Earthdata authentication.

## Syntax

```bash
swot-wse auth [options]
```

Without service-specific options:

```bash
swot-wse auth
```

the command manages both services.

---

## Options

| Option | Description |
| --- | --- |
| `--project-id <project-id>` | Supply the Google Cloud Project ID used for Earth Engine. |
| `--force` | Authenticate again instead of reusing the current authentication state. |
| `--remove` | Remove authentication information managed directly by **swot-wse**. |
| `--earth-engine-only` | Apply the operation only to Google Earth Engine. |
| `--earthdata-only` | Apply the operation only to NASA Earthdata. |

The following option combinations are invalid:

```text
--force + --remove

--earth-engine-only + --earthdata-only

--earthdata-only + --project-id
```

---

## Authenticate Both Services

```bash
swot-wse auth
```

---

## Google Earth Engine Only

```bash
swot-wse auth --earth-engine-only
```

Supply the Project ID directly:

```bash
swot-wse auth --earth-engine-only --project-id my-earth-engine-project
```

---

## NASA Earthdata Only

```bash
swot-wse auth --earthdata-only
```

---

## Force Reauthentication

Both services:

```bash
swot-wse auth --force
```

Earth Engine only:

```bash
swot-wse auth --earth-engine-only --force
```

Earthdata only:

```bash
swot-wse auth --earthdata-only --force
```

Earth Engine with a different project:

```bash
swot-wse auth --earth-engine-only --force --project-id another-earth-engine-project
```

The Project ID can also be supplied while forcing both services:

```bash
swot-wse auth --force --project-id another-earth-engine-project
```

---

## Remove Authentication Information

Both services:

```bash
swot-wse auth --remove
```

Earth Engine configuration only:

```bash
swot-wse auth --earth-engine-only --remove
```

Earthdata credentials only:

```bash
swot-wse auth --earthdata-only --remove
```

`--earth-engine-only --remove` removes the Project ID stored in the active `config.json`. It does not delete Google-managed OAuth credentials.

`--earthdata-only --remove` removes the `urs.earthdata.nasa.gov` entry managed by the package from the user's netrc file.

For authentication storage and behaviour, see [Authentication](authentication.md).

---

# 3. `config`

View, modify, or restore runtime configuration.

## Syntax

```bash
swot-wse config {show,set,reset}
```

The active runtime configuration is stored in:

```text
config.json
```

in the current **swot-wse working directory**.

---

# 3.1 `config show`

Display the complete active configuration.

```bash
swot-wse config show
```

This includes common settings and source-specific configuration under:

```text
sources.lakesp
sources.pixc
```

---

# 3.2 `config set`

Modify one configuration value.

## Syntax

```bash
swot-wse config set <key> <value>
```

Nested keys use dotted notation.

Example:

```bash
swot-wse config set sources.lakesp.mad_threshold 2.5
```

The following sections list the supported configuration keys.

---

# 4. General Configuration

## `max_workers`

Set the maximum number of concurrent worker tasks:

```bash
swot-wse config set max_workers 4
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
swot-wse config set generate_plot true
```

Disable it:

```bash
swot-wse config set generate_plot false
```

Disabling plot generation does not disable CSV generation.

---

# 5. Reservoir Footprint Configuration

## `search_radius_m`

```bash
swot-wse config set search_radius_m 100000
```

The value must be greater than `0`.

---

## `pekel_threshold`

```bash
swot-wse config set pekel_threshold 30
```

Accepted values are between:

```text
0
```

and:

```text
100
```

---

## `working_crs`

Use automatic projected CRS selection:

```bash
swot-wse config set working_crs auto
```

Or provide an explicit CRS:

```bash
swot-wse config set working_crs EPSG:32643
```

A supplied CRS string is stored as configuration and is subsequently interpreted by the geospatial processing stack.

For guidance on changing reservoir-footprint parameters, see [Configuration](configuration.md).

---

# 6. Earth Engine Configuration

## `earth_engine_project`

Set the Project ID:

```bash
swot-wse config set earth_engine_project my-earth-engine-project
```

Clear it:

```bash
swot-wse config set earth_engine_project none
```

Changing this value does not authenticate Google Earth Engine.

Authentication should normally be configured through:

```bash
swot-wse auth --earth-engine-only
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
swot-wse config set sources.lakesp.collection SWOT_L2_HR_LakeSP_Obs_D
```

Changing the collection string does not automatically make an incompatible LakeSP or other SWOT product supported by the package.

---

## `sources.lakesp.search_buffer_degrees`

```bash
swot-wse config set sources.lakesp.search_buffer_degrees 0.75
```

The value cannot be negative.

---

## `sources.lakesp.science_cycles`

Restrict the source to selected science cycles:

```bash
swot-wse config set sources.lakesp.science_cycles 045,046,047
```

Cycle numbers are normalized to three digits.

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

The list must contain at least one valid positive cycle number.

---

## `sources.lakesp.mad_threshold`

```bash
swot-wse config set sources.lakesp.mad_threshold 2.5
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

Retain only `GOOD` observations:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good
```

Retain `GOOD` and `SUSPECT`:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good,suspect
```

Retain the default three classes:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded
```

Retain all supported classes:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded,bad
```

At least one valid quality class must be supplied.

Duplicate values are removed automatically.

For the meaning and effect of these classes, see [Configuration](configuration.md) and [Outputs](outputs.md).

---

# 8. PIXC Configuration

PIXC settings are located under:

```text
sources.pixc
```

---

## `sources.pixc.collection`

```bash
swot-wse config set sources.pixc.collection SWOT_L2_HR_PIXC_D
```

---

## `sources.pixc.search_buffer_degrees`

```bash
swot-wse config set sources.pixc.search_buffer_degrees 0.75
```

The value cannot be negative.

---

## `sources.pixc.science_cycles`

```bash
swot-wse config set sources.pixc.science_cycles 045,046,047
```

Cycle numbers use the same normalization rules as LakeSP science cycles.

---

## `sources.pixc.mad_threshold`

```bash
swot-wse config set sources.pixc.mad_threshold 2.5
```

The value must be greater than `0`.

---

## `sources.pixc.water_classification`

```bash
swot-wse config set sources.pixc.water_classification 4
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
swot-wse config set polygon_cache_enabled true
```

Disable it:

```bash
swot-wse config set polygon_cache_enabled false
```

---

## `lakesp_cache_enabled`

Enable persistent LakeSP granule caching:

```bash
swot-wse config set lakesp_cache_enabled true
```

Disable it:

```bash
swot-wse config set lakesp_cache_enabled false
```

PIXC granules are currently processed through temporary working directories and are not retained in a persistent PIXC granule cache.

---

## `cache_dir`

```bash
swot-wse config set cache_dir cache
```

An absolute path can also be supplied:

```powershell
swot-wse config set cache_dir D:\SWOT\cache
```

Relative paths are resolved from the working directory.

---

## `temp_download_dir`

```bash
swot-wse config set temp_download_dir downloads/temp
```

An absolute path can also be supplied.

---

# 10. Output Configuration

## `output_dir`

```bash
swot-wse config set output_dir outputs
```

Example with an absolute path:

```powershell
swot-wse config set output_dir D:\SWOT\outputs
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
swot-wse config set generate_plot yes
swot-wse config set polygon_cache_enabled 0
swot-wse config set lakesp_cache_enabled on
```

---

## List Values

List-based configuration values can be supplied as comma-separated values:

```bash
swot-wse config set sources.lakesp.science_cycles 045,046,047
```

and:

```bash
swot-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded
```

JSON-style lists are also accepted when correctly quoted for the user's shell.

---

## Numeric Values

Examples:

```bash
swot-wse config set max_workers 4
swot-wse config set search_radius_m 50000
swot-wse config set pekel_threshold 20
swot-wse config set sources.lakesp.mad_threshold 3.0
swot-wse config set sources.pixc.mad_threshold 3.0
```

---

# 12. `config reset`

Restore all configuration values to package defaults:

```bash
swot-wse config reset
```

This includes resetting:

```text
earth_engine_project
```

to:

```text
null
```

The operation does **not** remove:

- Google-managed Earth Engine OAuth credentials;
- NASA Earthdata credentials stored in the user's netrc file;
- generated output files.

If authentication information also needs to be removed, use:

```bash
swot-wse auth --remove
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
swot-wse cache [option]
```

Running the command without an option displays a cache summary:

```bash
swot-wse cache
```

Example:

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
swot-wse cache --clear-polygons
```

They will be regenerated when required by a later extraction.

---

## `--clear-lakesp`

Remove cached LakeSP granules:

```bash
swot-wse cache --clear-lakesp
```

Required LakeSP products will be downloaded again when necessary.

---

## `--clear-all`

Remove all persistent cache data currently managed by the cache command:

```bash
swot-wse cache --clear-all
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
