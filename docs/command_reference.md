# Command Reference

This document provides a complete reference for the command-line interface (CLI) of **swot-reservoir-wse**, including the available commands, command-line options, configuration controls, and usage examples.

---

# Display Available Commands

Display all available command groups:

```bash
swot-wse --help
```

Each command group also provides its own help page:

```bash
swot-wse polygon --help
swot-wse auth --help
swot-wse config --help
swot-wse cache --help
```

---

# 1. Reservoir WSE Extraction

Generate a reservoir-specific Water Surface Elevation (WSE) time series from a supplied dam location and date range.

```bash
swot-wse polygon --lat <latitude> --lon <longitude> --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--source <source>]
```

Example:

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16
```

## Arguments

| Argument | Required | Description |
|----------|:--------:|-------------|
| `--lat` | Yes | Latitude of the dam location. |
| `--lon` | Yes | Longitude of the dam location. |
| `--start-date` | Yes | Start date in `YYYY-MM-DD` format. |
| `--end-date` | Yes | End date in `YYYY-MM-DD` format. |
| `--source` | No | SWOT observation source. Default: `auto`. |

If `--source` is not specified, the package uses:

```text
auto
```

`auto` is the automatic source-selection mode. In the current release, LakeSP is the only implemented observation source, so:

```text
auto → lakesp
```

LakeSP can also be selected explicitly:

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

---

# 2. Authentication

The `auth` command manages authentication for both **Google Earth Engine** and **NASA Earthdata**.

Google Earth Engine is required for reservoir footprint generation, while NASA Earthdata is required for discovering and retrieving SWOT observation products.

## Authenticate Both Services

```bash
swot-wse auth
```

Existing credentials are reused whenever possible. If authentication is required, the package starts the corresponding authentication process.

---

## Google Earth Engine Only

Manage only Google Earth Engine authentication:

```bash
swot-wse auth --earth-engine-only
```

If a Google Earth Engine Project ID has not already been configured, the package prompts for one.

A Project ID can also be supplied directly:

```bash
swot-wse auth --earth-engine-only --project-id <project-id>
```

Example:

```bash
swot-wse auth --earth-engine-only --project-id my-earth-engine-project
```

The selected Project ID is stored in the package configuration for subsequent use.

---

## NASA Earthdata Only

Manage only NASA Earthdata authentication:

```bash
swot-wse auth --earthdata-only
```

Existing Earthdata credentials are reused when available. Otherwise, the package requests the user's Earthdata Login username and password.

---

## Force Reauthentication

Force reauthentication for both services:

```bash
swot-wse auth --force
```

Force Google Earth Engine reauthentication only:

```bash
swot-wse auth --earth-engine-only --force
```

Force NASA Earthdata reauthentication only:

```bash
swot-wse auth --earthdata-only --force
```

A Google Earth Engine Project ID can also be supplied while forcing reauthentication:

```bash
swot-wse auth --earth-engine-only --force --project-id <project-id>
```

Example:

```bash
swot-wse auth --earth-engine-only --force --project-id another-earth-engine-project
```

For NASA Earthdata, `--force` removes the existing Earthdata Login credentials managed by the package before requesting new credentials.

---

## Remove Authentication Information

Remove authentication information managed by the package for both services:

```bash
swot-wse auth --remove
```

Remove only the stored Google Earth Engine Project ID:

```bash
swot-wse auth --earth-engine-only --remove
```

Remove only the stored NASA Earthdata credentials:

```bash
swot-wse auth --earthdata-only --remove
```

Removing the Google Earth Engine configuration clears the Project ID stored by **swot-reservoir-wse**. Google-managed OAuth credentials are not deleted.

Removing NASA Earthdata authentication removes the Earthdata Login entry from the user's netrc credential file while preserving unrelated entries.

---

## Authentication Arguments

| Argument | Required | Description |
|----------|:--------:|-------------|
| `--project-id <project-id>` | No | Supplies the Google Earth Engine Project ID directly. |
| `--force` | No | Forces reauthentication instead of reusing existing credentials. |
| `--remove` | No | Removes stored authentication information managed by the package. |
| `--earth-engine-only` | No | Applies the authentication operation only to Google Earth Engine. |
| `--earthdata-only` | No | Applies the authentication operation only to NASA Earthdata. |

`--earth-engine-only` and `--earthdata-only` cannot be used together.

For additional information about credential storage and authentication behaviour, see the [Authentication](authentication.md) documentation.

---

# 3. Display Configuration

Display the complete active runtime configuration:

```bash
swot-wse config show
```

The displayed values include general processing parameters, reservoir footprint settings, LakeSP parameters, cache locations, output locations, and the configured Google Earth Engine Project ID.

---

# 4. Modify Configuration

Update an individual configuration parameter without modifying the package source code:

```bash
swot-wse config set <key> <value>
```

## General Parameters

Change the maximum number of worker threads available for parallel processing:

```bash
swot-wse config set max_workers 4
```

Enable plot generation:

```bash
swot-wse config set generate_plot true
```

Disable plot generation:

```bash
swot-wse config set generate_plot false
```

---

## Google Earth Engine

Set the Google Earth Engine Project ID:

```bash
swot-wse config set earth_engine_project my-earth-engine-project
```

Clear the stored Project ID:

```bash
swot-wse config set earth_engine_project none
```

Changing `earth_engine_project` modifies the package configuration but does not itself perform Google Earth Engine authentication.

Authentication should normally be managed through:

```bash
swot-wse auth
```

---

## Reservoir Footprint Parameters

Change the search radius used when deriving the reservoir footprint from the supplied dam location:

```bash
swot-wse config set search_radius_m 100000
```

Change the JRC Global Surface Water occurrence threshold:

```bash
swot-wse config set pekel_threshold 30
```

Use automatic projected coordinate reference system selection:

```bash
swot-wse config set working_crs auto
```

Specify a projected coordinate reference system explicitly:

```bash
swot-wse config set working_crs EPSG:32643
```

---

## LakeSP Parameters

LakeSP-specific configuration values are stored under:

```text
sources.lakesp
```

These parameters can be modified using the same `config set` command.

### LakeSP Collection

Change the NASA Earthdata collection used for LakeSP discovery:

```bash
swot-wse config set sources.lakesp.collection SWOT_L2_HR_LakeSP_Obs_D
```

### Search Buffer

Change the geographic search buffer used during LakeSP granule discovery:

```bash
swot-wse config set sources.lakesp.search_buffer_degrees 0.75
```

### Science Cycles

Restrict processing to selected SWOT science cycles:

```bash
swot-wse config set sources.lakesp.science_cycles 045,046,047
```

Science cycles are supplied as comma-separated values.

For example:

```text
045,046,047
```

### MAD Threshold

Change the Median Absolute Deviation (MAD) threshold used during temporal outlier filtering:

```bash
swot-wse config set sources.lakesp.mad_threshold 2.5
```

For a detailed explanation of these parameters and how they affect processing, see the [Configuration](configuration.md) documentation.

---

## Cache Parameters

Enable reservoir polygon caching:

```bash
swot-wse config set polygon_cache_enabled true
```

Disable reservoir polygon caching:

```bash
swot-wse config set polygon_cache_enabled false
```

Enable LakeSP granule caching:

```bash
swot-wse config set lakesp_cache_enabled true
```

Disable LakeSP granule caching:

```bash
swot-wse config set lakesp_cache_enabled false
```

Change the cache directory:

```bash
swot-wse config set cache_dir <path>
```

Example:

```bash
swot-wse config set cache_dir D:\swot-data\cache
```

Change the temporary download directory:

```bash
swot-wse config set temp_download_dir <path>
```

Example:

```bash
swot-wse config set temp_download_dir D:\swot-data\temp
```

---

## Output Parameters

Change the output directory:

```bash
swot-wse config set output_dir <path>
```

Example:

```bash
swot-wse config set output_dir D:\swot-data\outputs
```

---

## Accepted Boolean Values

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

---

# 5. Reset Configuration

Restore all configuration parameters to their default values:

```bash
swot-wse config reset
```

This also clears the Google Earth Engine Project ID stored in the package configuration.

Authentication credentials maintained separately by Google Earth Engine and NASA Earthdata are not removed by `config reset`.

Use the `auth --remove` commands when authentication information must be removed.

---

# 6. Display Cache Summary

Display the cache location together with the number of cached reservoir polygons and LakeSP granules:

```bash
swot-wse cache
```

---

# 7. Clear Reservoir Polygon Cache

Remove all cached reservoir footprints:

```bash
swot-wse cache --clear-polygons
```

The reservoir footprints will be generated again when they are required by a subsequent processing run.

---

# 8. Clear LakeSP Granule Cache

Remove all cached LakeSP granules:

```bash
swot-wse cache --clear-lakesp
```

Required granules will be downloaded again from NASA Earthdata during subsequent processing.

---

# 9. Clear All Cached Data

Remove both the reservoir polygon cache and the LakeSP granule cache:

```bash
swot-wse cache --clear-all
```

This does not remove package configuration, authentication credentials, or generated outputs.