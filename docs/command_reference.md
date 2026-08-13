# Command Reference

This page documents the command-line interface for **swot-reservoir-wse**.

The package provides four top-level commands:

```text
extract
auth
config
cache
```

To display the top-level help page:

```bash
swot-reservoir-wse --help
```

Help for an individual command is available with:

```bash
swot-reservoir-wse extract --help
swot-reservoir-wse auth --help
swot-reservoir-wse config --help
swot-reservoir-wse cache --help
```

The `config` command provides three subcommands:

```bash
swot-reservoir-wse config show --help
swot-reservoir-wse config set --help
swot-reservoir-wse config reset --help
```

---

## 1. Typical Command Sequence

A normal processing run consists of three steps:

1. authenticate the external services used by the package;
2. inspect or modify the runtime configuration if necessary; and
3. run "extract" with the required dam location, date range, and SWOT observation source.

LakeSP and PIXC are independent observation sources. The source must be selected explicitly for each extraction.

For a complete practical walkthrough of both processing workflows, see [Usage](usage.md).

### LakeSP Example

Authenticate the required external services:

```bash
swot-reservoir-wse auth
```

Inspect the active configuration:

```bash
swot-reservoir-wse config show
```

Run the extraction:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

With the default output configuration, the generated products are written under:

```text
outputs/
```

with filenames such as:

```text
19.69000_73.34000_lakesp_wse.csv
19.69000_73.34000_lakesp_wse.png
```

The PNG product is generated only when plot generation is enabled.

### PIXC Example

The same reservoir and observation period can be processed independently using the SWOT PIXC product:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
```

Successful products use source-specific filenames such as:

```text
19.69000_73.34000_pixc_wse.csv
19.69000_73.34000_pixc_wse.png
```

Running the PIXC source does not invoke LakeSP, and running LakeSP does not invoke PIXC.

---

## 2. extract

The "extract" command generates a reservoir-specific Water Surface Elevation (WSE) time series from the selected SWOT observation source.

### Syntax

```bash
swot-reservoir-wse extract --lat <latitude> --lon <longitude> --start-date YYYY-MM-DD --end-date YYYY-MM-DD --source {lakesp,pixc}
```

On Windows PowerShell, the command can be entered on a single line:

```powershell
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

### Arguments

| Argument | Required | Description |
| --- | :---: | --- |
| `--lat` | Yes | Latitude of the dam location. |
| `--lon` | Yes | Longitude of the dam location. |
| `--start-date` | Yes | Beginning of the requested observation period in `YYYY-MM-DD` format. |
| `--end-date` | Yes | End of the requested observation period in `YYYY-MM-DD` format. |
| `--source` | Yes | SWOT observation source. Supported values are `lakesp` and `pixc`. |

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

The observation source is mandatory. There is no automatic source selection or fallback between LakeSP and PIXC.

### LakeSP

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

For the LakeSP processing design, see [Package Architecture](architecture.md).

For configurable LakeSP parameters, see [Configuration](configuration.md).

### PIXC

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
```

For the PIXC processing design, see [Package Architecture](architecture.md).

PIXC processing operates directly on pixel-cloud products and may require a lower "max_workers" value on systems with limited memory.

---

## 3. auth

The `auth` command manages authentication for the two external services used by the package:

- Google Earth Engine, used during reservoir-footprint generation;
- NASA Earthdata, used for SWOT product discovery and access.

### Syntax

```bash
swot-reservoir-wse auth [options]
```

Running:

```bash
swot-reservoir-wse auth
```

manages authentication for both services.

### Options

| Option | Description |
| --- | --- |
| `--project-id <project-id>` | Supply the Google Cloud Project ID used for Earth Engine. |
| `--force` | Start authentication again instead of reusing the current authentication state. |
| `--remove` | Remove authentication information managed directly by the package. |
| `--earth-engine-only` | Apply the requested operation only to Google Earth Engine. |
| `--earthdata-only` | Apply the requested operation only to NASA Earthdata. |

The following combinations are invalid:

```text
--force + --remove
--earth-engine-only + --earthdata-only
--earthdata-only + --project-id
```

### Authenticate Both Services

```bash
swot-reservoir-wse auth
```

Existing authentication information is reused when it is available and valid.

### Google Earth Engine Only

```bash
swot-reservoir-wse auth --earth-engine-only
```

A Project ID can be supplied directly:

```bash
swot-reservoir-wse auth --earth-engine-only --project-id my-earth-engine-project
```

If no Project ID is supplied and none is stored in the active configuration, the package prompts for one.

### NASA Earthdata Only

```bash
swot-reservoir-wse auth --earthdata-only
```

If valid Earthdata credentials are already available, they are reused. Otherwise, the package requests the Earthdata Login username and password.

### Force Reauthentication

Reauthenticate both services:

```bash
swot-reservoir-wse auth --force
```

Reauthenticate Google Earth Engine only:

```bash
swot-reservoir-wse auth --earth-engine-only --force
```

Reauthenticate NASA Earthdata only:

```bash
swot-reservoir-wse auth --earthdata-only --force
```

A different Earth Engine Project ID can be supplied while reauthenticating:

```bash
swot-reservoir-wse auth --earth-engine-only --force --project-id another-earth-engine-project
```

or:

```bash
swot-reservoir-wse auth --force --project-id another-earth-engine-project
```

### Remove Authentication Information

Remove authentication information managed directly by the package for both services:

```bash
swot-reservoir-wse auth --remove
```

Remove only the stored Earth Engine Project ID:

```bash
swot-reservoir-wse auth --earth-engine-only --remove
```

Remove only the NASA Earthdata credentials managed through the user's netrc file:

```bash
swot-reservoir-wse auth --earthdata-only --remove
```

Removing the Earth Engine configuration does not delete Google-managed OAuth credentials.

Removing Earthdata authentication removes the "urs.earthdata.nasa.gov" entry managed by the package while preserving unrelated netrc entries.

For detailed authentication behaviour, credential storage, credential reuse, and service-specific setup, see [Authentication](authentication.md).

---

## 4. config

The "config" command displays, modifies, or restores the runtime configuration used by **swot-reservoir-wse**.

### Syntax

```bash
swot-reservoir-wse config {show,set,reset}
```

The active configuration is stored in:

```text
config.json
```

in the current working directory.

The repository also provides:

```text
config.example.json
```

as a reference configuration.

### config show

Display the complete active configuration:

```bash
swot-reservoir-wse config show
```

The output includes common package settings and source-specific configuration under:

```text
sources.lakesp
sources.pixc
```

### config set

Modify an individual configuration value.

#### Syntax

```bash
swot-reservoir-wse config set <key> <value>
```

Nested configuration keys use dotted notation.

For example:

```bash
swot-reservoir-wse config set sources.lakesp.mad_threshold 2.5
```

The following sections provide the supported configuration keys and their command-line forms. For detailed explanations of how each parameter affects processing, see [Configuration](configuration.md).

---

## 5. General Configuration

### max_workers

Default:

```text
max(1, CPU count - 1)
```

Valid range:

```text
>= 1
```

Set the maximum number of concurrent worker tasks:

```bash
swot-reservoir-wse config set max_workers 4
```

Reducing this value may be useful during PIXC processing on systems with limited memory.

### generate_plot

Default:

```text
true
```

Enable PNG output generation:

```bash
swot-reservoir-wse config set generate_plot true
```

Disable PNG output generation:

```bash
swot-reservoir-wse config set generate_plot false
```

CSV output generation is unaffected.

---

## 6. Earth Engine Configuration

### earth_engine_project

Default:

```text
null
```

Set the Google Cloud Project ID used for Earth Engine:

```bash
swot-reservoir-wse config set earth_engine_project my-earth-engine-project
```

Clear the configured Project ID:

```bash
swot-reservoir-wse config set earth_engine_project none
```

Changing this value modifies the package configuration only. It does not itself perform Google Earth Engine authentication.

For detailed authentication behaviour, see [Authentication](authentication.md).

---

## 7. Reservoir Footprint Configuration

### search_radius_m

Default:

```text
50000
```

Unit:

```text
metres
```

Valid range:

```text
> 0
```

Set the reservoir search radius:

```bash
swot-reservoir-wse config set search_radius_m 100000
```

For example:

```text
50000 metres = 50 km
100000 metres = 100 km
```

### pekel_threshold

Default:

```text
20
```

Unit:

```text
percent water occurrence
```

Valid range:

```text
0-100
```

Set the JRC Global Surface Water occurrence threshold used during reservoir-footprint generation:

```bash
swot-reservoir-wse config set pekel_threshold 30
```

### working_crs

Default:

```text
auto
```

Use automatic projected CRS selection:

```bash
swot-reservoir-wse config set working_crs auto
```

Or specify a projected CRS explicitly:

```bash
swot-reservoir-wse config set working_crs EPSG:32643
```

For the effect of these parameters on reservoir-footprint generation, see [Configuration](configuration.md).

---

## 8. LakeSP Configuration

LakeSP-specific settings are stored under:

```text
sources.lakesp
```

### sources.lakesp.collection

Default:

```text
SWOT_L2_HR_LakeSP_Obs_D
```

Set the NASA Earthdata collection used by the LakeSP source:

```bash
swot-reservoir-wse config set sources.lakesp.collection SWOT_L2_HR_LakeSP_Obs_D
```

Changing the collection identifier does not automatically make an incompatible LakeSP version or another SWOT product compatible with the package.

### sources.lakesp.search_buffer_degrees

Default:

```text
0.5
```

Unit:

```text
degrees
```

Valid range:

```text
>= 0
```

Set the geographic search buffer used during LakeSP product discovery:

```bash
swot-reservoir-wse config set sources.lakesp.search_buffer_degrees 0.75
```

The value represents an angular geographic buffer rather than a fixed distance in kilometres.

### sources.lakesp.science_cycles

Default:

```text
001 through 052
```

Restrict LakeSP processing to selected SWOT science cycles:

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

### sources.lakesp.mad_threshold

Default:

```text
3.0
```

Valid range:

```text
> 0
```

Set the LakeSP temporal Median Absolute Deviation threshold:

```bash
swot-reservoir-wse config set sources.lakesp.mad_threshold 2.5
```

### sources.lakesp.accepted_quality_flags

Default:

```text
good,suspect,degraded
```

Supported values are:

```text
good
suspect
degraded
bad
```

Retain only "GOOD" observations:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good
```

Retain "GOOD" and "SUSPECT" observations:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect
```

Retain the default three classes:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded
```

Retain all supported classes:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded,bad
```

At least one valid quality class must be supplied.

Duplicate values are removed automatically.

For the scientific meaning and processing effect of these classes, see [Configuration](configuration.md).

For their representation in the generated time series, see [Outputs](outputs.md).

---

## 9. PIXC Configuration

PIXC-specific settings are stored under:

```text
sources.pixc
```

### sources.pixc.collection

Default:

```text
SWOT_L2_HR_PIXC_D
```

Set the NASA Earthdata collection used by the PIXC source:

```bash
swot-reservoir-wse config set sources.pixc.collection SWOT_L2_HR_PIXC_D
```

Changing the collection identifier does not make an otherwise incompatible SWOT product compatible with the PIXC processing implementation.

### sources.pixc.search_buffer_degrees

Default:

```text
0.5
```

Unit:

```text
degrees
```

Valid range:

```text
>= 0
```

Set the geographic search buffer used during PIXC granule discovery:

```bash
swot-reservoir-wse config set sources.pixc.search_buffer_degrees 0.75
```

### sources.pixc.science_cycles

Default:

```text
001 through 052
```

Restrict PIXC processing to selected SWOT science cycles:

```bash
swot-reservoir-wse config set sources.pixc.science_cycles 045,046,047
```

Cycle numbers use the same normalization rules as LakeSP science cycles.

### sources.pixc.mad_threshold

Default:

```text
3.0
```

Valid range:

```text
> 0
```

Set the PIXC temporal Median Absolute Deviation (MAD) threshold:

```bash
swot-reservoir-wse config set sources.pixc.mad_threshold 2.5
```

### sources.pixc.water_classification

Default:

```text
4
```

Valid range:

```text
>= 0
```

Set the PIXC classification value retained for quality screening:

```bash
swot-reservoir-wse config set sources.pixc.water_classification 4
```

Negative values are rejected.

For the scientific meaning of this parameter and its effect on pixel selection, see [Configuration](configuration.md).

---

## 10. Cache and Temporary Storage Configuration

### polygon_cache_enabled

Default:

```text
true
```

Enable persistent reservoir-footprint caching:

```bash
swot-reservoir-wse config set polygon_cache_enabled true
```

Disable it:

```bash
swot-reservoir-wse config set polygon_cache_enabled false
```

### lakesp_cache_enabled

Default:

```text
true
```

Enable persistent LakeSP granule caching:

```bash
swot-reservoir-wse config set lakesp_cache_enabled true
```

Disable it:

```bash
swot-reservoir-wse config set lakesp_cache_enabled false
```

PIXC granules are currently processed through temporary working directories and are not retained in a persistent PIXC granule cache.

### cache_dir

Default:

```text
cache
```

Set the persistent cache directory:

```bash
swot-reservoir-wse config set cache_dir cache
```

An absolute path can also be supplied.

For example, on Windows:

```powershell
swot-reservoir-wse config set cache_dir D:\SWOT\cache
```

Relative paths are resolved from the current working directory.

### temp_download_dir

Default:

```text
downloads/temp
```

Set the directory used for temporary download and processing data:

```bash
swot-reservoir-wse config set temp_download_dir downloads/temp
```

An absolute path can also be supplied:

```powershell
swot-reservoir-wse config set temp_download_dir D:\SWOT\temp
```

The directory is used by both source pipelines when temporary files are required.

For LakeSP, it is used for temporary downloads and non-cached processing.

For PIXC, downloaded granules and NetCDF processing workspaces are placed here because PIXC products are not currently retained in a persistent granule cache.

---

## 11. Output Configuration

### output_dir

Default:

```text
outputs
```

Set the output directory:

```bash
swot-reservoir-wse config set output_dir outputs
```

An absolute path can also be used.

For example, on Windows:

```powershell
swot-reservoir-wse config set output_dir D:\swot-output-test
```

Relative paths are resolved from the current working directory.

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
```

and:

```text
19.69000_73.34000_pixc_wse.csv
19.69000_73.34000_pixc_wse.png
```

For the complete output schemas, see [Outputs](outputs.md).

---

## 12. Accepted Configuration Value Forms

### Boolean Values

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

### List Values

List-based configuration values can be supplied as comma-separated values.

For example:

```bash
swot-reservoir-wse config set sources.lakesp.science_cycles 045,046,047
```

and:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded
```

JSON-style lists may also be supplied when correctly quoted for the user's shell.

### Numeric Values

Examples include:

```bash
swot-reservoir-wse config set max_workers 4
swot-reservoir-wse config set search_radius_m 50000
swot-reservoir-wse config set pekel_threshold 20
swot-reservoir-wse config set sources.lakesp.mad_threshold 3.0
swot-reservoir-wse config set sources.pixc.mad_threshold 3.0
```

---

## 13. config reset

Restore all configuration values to their package defaults:

```bash
swot-reservoir-wse config reset
```

This also resets:

```text
earth_engine_project
```

to:

```text
null
```

The command does not remove:

- Google-managed Earth Engine OAuth credentials,
- NASA Earthdata credentials stored in the user's netrc file,
- generated output files,
- cached data.

If authentication information managed by the package should also be removed, use:

```bash
swot-reservoir-wse auth --remove
```

After resetting, inspect the resulting configuration with:

```bash
swot-reservoir-wse config show
```

---

## 14. cache

The "cache" command inspects or clears persistent cache data.

### Syntax

```bash
swot-reservoir-wse cache [option]
```

Running the command without an option displays the current cache summary:

```bash
swot-reservoir-wse cache
```

An example summary is:

```text
Cache Summary
-------------
Reservoir polygons : 1
LakeSP granules    : 21

Location : <cache-directory>
```

The persistent cache currently contains reservoir footprints and LakeSP granules.

PIXC products are not included because downloaded PIXC granules are not currently retained in a persistent cache.

### --clear-polygons

Remove cached reservoir footprints:

```bash
swot-reservoir-wse cache --clear-polygons
```

A required reservoir footprint will be generated again during a later extraction.

### --clear-lakesp

Remove cached LakeSP granules:

```bash
swot-reservoir-wse cache --clear-lakesp
```

Required LakeSP products will be downloaded again when necessary.

### --clear-all

Remove all persistent cache data currently managed by the package:

```bash
swot-reservoir-wse cache --clear-all
```

This currently removes:

```text
reservoir polygon cache
LakeSP granule cache
```

It does not remove:

```text
config.json
Earth Engine OAuth credentials
NASA Earthdata credentials
CSV outputs
PNG outputs
```

The cache-clearing options are mutually exclusive.

---

## 15. Configuration Key Summary

| Key | Default | Valid Value / Type |
| --- | --- | --- |
| earth_engine_project | null | Project ID or null |
| search_radius_m | 50000 | Number > 0, metres |
| pekel_threshold | 20 | Number from 0 to 100 |
| working_crs | auto | auto or supported CRS |
| max_workers | max(1, CPU count - 1) | Integer >= 1 |
| generate_plot | true | Boolean |
| polygon_cache_enabled | true | Boolean |
| lakesp_cache_enabled | true | Boolean |
| cache_dir | cache | Filesystem path |
| output_dir | outputs | Filesystem path |
| temp_download_dir | downloads/temp | Filesystem path |
| sources.lakesp.collection | SWOT_L2_HR_LakeSP_Obs_D | Collection identifier |
| sources.lakesp.search_buffer_degrees | 0.5 | Number >= 0, degrees |
| sources.lakesp.science_cycles | 001 through 052 | Positive cycle identifiers |
| sources.lakesp.mad_threshold | 3.0 | Number > 0 |
| sources.lakesp.accepted_quality_flags | good,suspect,degraded | One or more supported quality classes |
| sources.pixc.collection | SWOT_L2_HR_PIXC_D | Collection identifier |
| sources.pixc.search_buffer_degrees | 0.5 | Number >= 0, degrees |
| sources.pixc.science_cycles | 001 through 052 | Positive cycle identifiers |
| sources.pixc.mad_threshold | 3.0 | Number > 0 |
| sources.pixc.water_classification | 4 | Integer >= 0 |

---

## Related Documentation

This page is intended as the reference for **command syntax, arguments, options, and configuration keys**.

For a guided installation and initial setup, see [Installation](installation.md).

For a practical first extraction and complete LakeSP and PIXC workflows, see [Usage](usage.md).

For authentication behaviour and credential storage, see [Authentication](authentication.md).

For detailed explanations of configuration parameters and their effects on processing, see [Configuration](configuration.md).

For the LakeSP and PIXC processing architecture, see [Package Architecture](architecture.md).

For generated files, CSV fields, and plots, see [Outputs](outputs.md).
