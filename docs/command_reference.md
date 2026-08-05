# Overview

This document lists all commands currently supported by **swot-reservoir-wse**.

## General Help

```
swot-wse --help
```

Displays all available command groups.

---

## 1. Reservoir WSE Extraction

```
swot-wse polygon --lat <latitude> --lon <longitude> --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--source <source>]
```

Example:

```
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16
```

Arguments:

| Argument       | Required | Description                               |
| -------------- | :------: | ----------------------------------------- |
| `--lat`        |    Yes   | Reservoir or dam latitude.                |
| `--lon`        |    Yes   | Reservoir or dam longitude.               |
| `--start-date` |    Yes   | Start date in `YYYY-MM-DD` format.        |
| `--end-date`   |    Yes   | End date in `YYYY-MM-DD` format.          |
| `--source`     |    No    | SWOT observation source. Default: `auto`. |

The current release resolves:
```
auto → lakesp
```

Explicit LakeSP selection:

```
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

---

## 2. Google Earth Engine Authentication

### A. Standard authentication

```
swot-wse auth
```

Prompts for the Google Earth Engine Project ID, checks for existing credentials, starts authentication when required, and saves the selected Project ID.

### B. Supply the Project ID directly

```
swot-wse auth --project-id <project-id>
```

Example:

```
swot-wse auth --project-id my-earth-engine-project
```

This avoids the interactive Project ID prompt.

### C. Force a new authentication flow

```
swot-wse auth --force
```

Forces Google Earth Engine to start a new browser-based authentication flow instead of reusing the currently stored credentials.

Use this command when:

* changing the Google account;
* replacing expired or invalid credentials;
* reauthorizing Earth Engine access.

### D. Change both account and Project ID

```
swot-wse auth --force --project-id <project-id>
```

Example:

```
swot-wse auth --force --project-id another-earth-engine-project
```

Authentication arguments:

| Argument       | Required | Description                                                             |
| -------------- | :------: | ----------------------------------------------------------------------- |
| `--project-id` |    No    | Google Earth Engine Project ID. If omitted, the package prompts for it. |
| `--force`      |    No    | Forces a new Earth Engine authentication flow.                          |

---

## 3. Display Configuration

```
swot-wse config show
```

Displays the complete active configuration.

---

## 4. Modify Configuration

```
swot-wse config set <key> <value>
```

### A. Reservoir extraction parameters

Change the search radius:

```
swot-wse config set search_radius_m 100000
```

Change the JRC water-occurrence threshold:

```
swot-wse config set pekel_threshold 30
```

Use automatic projected CRS selection:

```
swot-wse config set working_crs auto
```

Use a specific CRS:

```
swot-wse config set working_crs EPSG:32643
```

### B. Processing parameters

Change the number of worker threads:

```
swot-wse config set max_workers 4
```

Enable or disable plot generation:

```
swot-wse config set generate_plot true
swot-wse config set generate_plot false
```

### C. Cache parameters

Enable or disable reservoir polygon caching:

```
swot-wse config set polygon_cache_enabled true
swot-wse config set polygon_cache_enabled false
```

Enable or disable LakeSP granule caching:

```
swot-wse config set lakesp_cache_enabled true
swot-wse config set lakesp_cache_enabled false
```

Change the cache directory:

```
swot-wse config set cache_dir cache
```

Change the temporary download directory:

```bash
swot-wse config set temp_download_dir downloads/temp
```

### D. Output parameters

Change the output directory:

```bash
swot-wse config set output_dir outputs
```

### E. Earth Engine project

Set the Earth Engine Project ID directly:

```bash
swot-wse config set earth_engine_project my-earth-engine-project
```

Clear the saved Project ID:

```bash
swot-wse config set earth_engine_project none
```

Changing this value alone does not perform authentication. Use `swot-wse auth` when credentials must also be verified or renewed.

### F. LakeSP source parameters

Change the LakeSP collection:

```bash
swot-wse config set sources.lakesp.collection SWOT_L2_HR_LakeSP_Obs_D
```

Change the granule search buffer:

```bash
swot-wse config set sources.lakesp.search_buffer_degrees 0.75
```

Restrict processing to selected SWOT science cycles:

```bash
swot-wse config set sources.lakesp.science_cycles '["045","046","047"]'
```

Change the MAD filtering threshold:

```bash
swot-wse config set sources.lakesp.mad_threshold 2.5
```

Boolean values accept:

```text
true, false, 1, 0, yes, no, on, off
```

List values must use JSON list syntax.

---

## 5. Reset Configuration

```bash
swot-wse config reset
```

Restores all configuration values to their defaults.

This also resets the saved Earth Engine Project ID.

---

## 6. Display Cache Summary

```bash
swot-wse cache
```

Displays the number of cached reservoir polygons, cached LakeSP granules, and the cache location.

---

## 7. Clear Reservoir Polygon Cache

```bash
swot-wse cache --clear-polygons
```

Removes all cached reservoir polygons.

---

## 8. Clear LakeSP Granule Cache

```bash
swot-wse cache --clear-lakesp
```

Removes all cached LakeSP granules.

---

## 9. Clear All Cached Data

```bash
swot-wse cache --clear-all
```

Removes both reservoir polygon and LakeSP granule caches.

---

## Complete Command List

```text
swot-wse --help

swot-wse polygon
swot-wse polygon --help
swot-wse polygon --lat <latitude> --lon <longitude> --start-date YYYY-MM-DD --end-date YYYY-MM-DD
swot-wse polygon --lat <latitude> --lon <longitude> --start-date YYYY-MM-DD --end-date YYYY-MM-DD --source lakesp

swot-wse auth
swot-wse auth --help
swot-wse auth --project-id <project-id>
swot-wse auth --force
swot-wse auth --force --project-id <project-id>

swot-wse config
swot-wse config --help
swot-wse config show
swot-wse config set <key> <value>
swot-wse config reset

swot-wse cache
swot-wse cache --help
swot-wse cache --clear-polygons
swot-wse cache --clear-lakesp
swot-wse cache --clear-all
```
