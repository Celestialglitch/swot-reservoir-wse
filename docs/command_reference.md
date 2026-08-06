# Command Reference

This document provides a complete reference for the command-line interface (CLI) of **swot-reservoir-wse**, including all supported commands, command-line options, configurable parameters, and usage examples.

---

# Display Available Commands

Display the available command groups.

```bash
swot-wse --help
```

Each command group also provides its own help page.

```bash
swot-wse polygon --help
swot-wse auth --help
swot-wse config --help
swot-wse cache --help
```

---

# 1. Reservoir WSE Extraction

Generate a reservoir-specific Water Surface Elevation (WSE) time series.

```bash
swot-wse polygon --lat <latitude> --lon <longitude> --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--source <source>]
```

Example

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16
```

### Arguments

| Argument | Required | Description |
|----------|:--------:|-------------|
| `--lat` | Yes | Latitude of the dam location. |
| `--lon` | Yes | Longitude of the dam location. |
| `--start-date` | Yes | Start date in `YYYY-MM-DD` format. |
| `--end-date` | Yes | End date in `YYYY-MM-DD` format. |
| `--source` | No | SWOT observation source. Default: `auto`. |

In the current release,

```text
auto → LakeSP
```

LakeSP may also be selected explicitly.

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

---

# 2. Google Earth Engine Authentication

### Standard authentication

```bash
swot-wse auth
```

Prompts for the Google Earth Engine Project ID, verifies existing credentials, performs authentication when required, and stores the selected Project ID for future use.

---

### Supply the Project ID directly

```bash
swot-wse auth --project-id <project-id>
```

Example

```bash
swot-wse auth --project-id my-earth-engine-project
```

This bypasses the interactive Project ID prompt.

---

### Force a new authentication

```bash
swot-wse auth --force
```

Starts a new Google Earth Engine authentication flow instead of reusing existing credentials.

Use this command when

- changing the Google account
- replacing expired or invalid credentials
- reauthorizing Earth Engine access.

---

### Specify both Project ID and force authentication

```bash
swot-wse auth --force --project-id <project-id>
```

Example

```bash
swot-wse auth --force --project-id another-earth-engine-project
```

### Arguments

| Argument | Required | Description |
|----------|:--------:|-------------|
| `--project-id` | No | Google Earth Engine Project ID. If omitted, the package prompts for it. |
| `--force` | No | Forces a new Google Earth Engine authentication flow. |

---

# 3. Display Configuration

Display the active runtime configuration.

```bash
swot-wse config show
```

---

# 4. Modify Configuration

Update a single configuration parameter without modifying the package source code.

```bash
swot-wse config set <key> <value>
```

---

## General Parameters

Change the number of worker threads.

```bash
swot-wse config set max_workers 4
```

Enable or disable plot generation.

```bash
swot-wse config set generate_plot true
swot-wse config set generate_plot false
```

---

## Google Earth Engine

Set the Google Earth Engine Project ID.

```bash
swot-wse config set earth_engine_project my-earth-engine-project
```

Clear the stored Project ID.

```bash
swot-wse config set earth_engine_project none
```

Changing this value does not authenticate Google Earth Engine. Run

```bash
swot-wse auth
```


---

## Reservoir Footprint Parameters

Change the search radius.

```bash
swot-wse config set search_radius_m 100000
```

Change the JRC Global Surface Water occurrence threshold.

```bash
swot-wse config set pekel_threshold 30
```

Use automatic projected CRS selection.

```bash
swot-wse config set working_crs auto
```

Specify a projected CRS.

```bash
swot-wse config set working_crs EPSG:32643
```

---

## LakeSP Parameters

Change the LakeSP collection.

```bash
swot-wse config set sources.lakesp.collection SWOT_L2_HR_LakeSP_Obs_D
```

Change the search buffer.

```bash
swot-wse config set sources.lakesp.search_buffer_degrees 0.75
```

Restrict processing to selected SWOT science cycles.

```bash
swot-wse config set sources.lakesp.science_cycles 045,046,047
```

Change the MAD filtering threshold.

```bash
swot-wse config set sources.lakesp.mad_threshold 2.5
```

---

## Cache Parameters

Enable or disable reservoir polygon caching.

```bash
swot-wse config set polygon_cache_enabled true
swot-wse config set polygon_cache_enabled false
```

Enable or disable LakeSP granule caching.

```bash
swot-wse config set lakesp_cache_enabled true
swot-wse config set lakesp_cache_enabled false
```

Change the cache directory.

```bash
swot-wse config set cache_dir cache
```

Change the temporary download directory.

```bash
swot-wse config set temp_download_dir downloads/temp
```

---

## Output Parameters

Change the output directory.

```bash
swot-wse config set output_dir outputs
```

---

### Accepted Boolean Values

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

### Science Cycle Values

Science cycles are manipulated as a comma-separated list.

Example

```bash
swot-wse config set sources.lakesp.science_cycles 045,046,047
```

---

# 5. Reset Configuration

Restore all configuration parameters to their default values.

```bash
swot-wse config reset
```

This also clears the stored Google Earth Engine Project ID.

---

# 6. Display Cache Summary

Display the cache location together with the number of cached reservoir polygons and LakeSP granules.

```bash
swot-wse cache
```

---

# 7. Clear Reservoir Polygon Cache

Remove all cached reservoir polygons.

```bash
swot-wse cache --clear-polygons
```

---

# 8. Clear LakeSP Granule Cache

Remove all cached LakeSP granules.

```bash
swot-wse cache --clear-lakesp
```

---

# 9. Clear All Cached Data

Remove all cached reservoir polygons and LakeSP granules.

```bash
swot-wse cache --clear-all
```
