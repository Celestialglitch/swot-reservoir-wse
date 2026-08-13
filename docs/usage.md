# Usage

This page provides a practical introduction to using **swot-reservoir-wse** to generate reservoir-specific Water Surface Elevation (WSE) time series from SWOT observations.

The package currently supports two independently selectable observation sources:

- **LakeSP**
- **PIXC**

For every command and option, see the [Command Reference](command_reference.md).

---

# Basic Workflow

A typical workflow consists of:

```text
Install swot-reservoir-wse
       │
       ▼
Configure authentication
       │
       ▼
Choose LakeSP or PIXC
       │
       ▼
Supply dam coordinates
and observation dates
       │
       ▼
Run extraction
       │
       ▼
Receive CSV and,
optionally, PNG output
```

---

# Authentication

Before the first extraction, configure the external services required by the package:

```bash
swot-reservoir-wse auth
```

The package uses:

- **Google Earth Engine** for reservoir footprint generation; and
- **NASA Earthdata** for SWOT product discovery and access.

Existing valid authentication is reused when possible.

The services can also be managed separately:

```bash
swot-reservoir-wse auth --earth-engine-only
```

```bash
swot-reservoir-wse auth --earthdata-only
```

Force reauthentication with:

```bash
swot-reservoir-wse auth --force
```

For credential removal, Project ID handling, and service-specific options, see [Authentication](authentication.md).

---

# Generate a Reservoir WSE Time Series

The extraction command is:

```bash
swot-reservoir-wse extract
```

A processing run requires:

- dam latitude;
- dam longitude;
- start date;
- end date; and
- SWOT observation source.

The general form is:

```bash
swot-reservoir-wse extract \
    --lat <latitude> \
    --lon <longitude> \
    --start-date YYYY-MM-DD \
    --end-date YYYY-MM-DD \
    --source <source>
```

The supported source values are:

```text
lakesp
pixc
```

The source must be selected explicitly.

There is no automatic source-selection or fallback mode.

---

# LakeSP Example

Generate a LakeSP WSE time series with:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

Here:

```text
--lat 19.690
--lon 73.340
```

identify the supplied dam location.

The coordinates are not treated as a predefined reservoir boundary.

Instead, **swot-reservoir-wse** derives the corresponding reservoir footprint and uses that footprint to identify relevant SWOT observations.

---

# What Happens During LakeSP Processing?

For a LakeSP run, the package performs the following high-level workflow:

```text
Dam coordinates
      │
      ▼
Reservoir footprint
      │
      ▼
LakeSP metadata search
      │
      ▼
Granule verification
      │
      ▼
Reservoir observation association
      │
      ▼
Quality screening
      │
      ▼
Daily aggregation
      │
      ▼
MAD filtering
      │
      ▼
Final LakeSP WSE time series
```

The reservoir footprint is generated using the JRC Global Surface Water dataset through Google Earth Engine unless a cached footprint is available.

Candidate LakeSP granules are discovered through NASA Earthdata.

The package then identifies LakeSP observations intersecting the reservoir footprint and uses their `lake_id` values to isolate reservoir-associated observations.

Partial observations are removed, and the remaining observations are filtered according to the configured LakeSP quality classes.

By default:

```text
GOOD
SUSPECT
DEGRADED
```

are retained, while:

```text
BAD
```

is excluded.

The retained observations are grouped by acquisition date, and their median WSE is used as the representative daily reservoir elevation.

The daily time series then undergoes temporal MAD filtering.

---

# PIXC Example

Generate a PIXC WSE time series with:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
```

PIXC is processed independently of LakeSP.

The package does not first attempt LakeSP and then fall back to PIXC.

---

# What Happens During PIXC Processing?

The PIXC workflow is:

```text
Dam coordinates
      │
      ▼
Reservoir footprint
      │
      ▼
PIXC metadata search
      │
      ▼
CMR footprint verification
      │
      ▼
PIXC granule download
      │
      ▼
Pixel-cloud extraction
      │
      ▼
Reservoir spatial intersection
      │
      ▼
Water and quality filtering
      │
      ▼
Pixel WSE calculation
      │
      ▼
Daily aggregation
      │
      ▼
MAD filtering
      │
      ▼
Final PIXC WSE time series
```

Candidate PIXC granules are first identified through NASA Earthdata.

Their NASA CMR geographic footprints are checked against the reservoir before the large PIXC NetCDF files are processed.

For verified granules, the package reads the `pixel_cloud` data and applies an initial reservoir bounding-box filter followed by exact reservoir intersection.

Accepted pixels are filtered using the configured PIXC classification and classification-quality criteria.

For each accepted pixel:

```text
WSE = height - geoid
```

The accepted pixels are grouped by acquisition date, and the median pixel WSE becomes the representative daily reservoir WSE.

---

# Choosing Between LakeSP and PIXC

LakeSP and PIXC are different SWOT products and are processed using different pipelines.

Choose LakeSP with:

```bash
--source lakesp
```

Choose PIXC with:

```bash
--source pixc
```

LakeSP provides vector observation records and associated quality information.

PIXC operates at the pixel-cloud level and therefore processes substantially more individual observations.

As a result, PIXC runs can require considerably more:

- memory;
- disk activity;
- network transfer; and
- processing time.

When processing PIXC on a machine with limited memory, reducing the worker count can help:

```bash
swot-reservoir-wse config set max_workers 4
```

or, if necessary:

```bash
swot-reservoir-wse config set max_workers 2
```

---

# Configuration

Display the active configuration with:

```bash
swot-reservoir-wse config show
```

Change an individual value with:

```bash
swot-reservoir-wse config set <key> <value>
```

---

## Change Worker Count

```bash
swot-reservoir-wse config set max_workers 4
```

The worker count affects parallel processing for both LakeSP and PIXC.

---

## Configure LakeSP Quality Classes

The default retained LakeSP quality classes are:

```text
good
suspect
degraded
```

Retain only `GOOD`:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good
```

Retain `GOOD` and `SUSPECT`:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect
```

Retain all supported classes:

```bash
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded,bad
```

---

## Restrict LakeSP Science Cycles

```bash
swot-reservoir-wse config set sources.lakesp.science_cycles 045,046,047
```

---

## Restrict PIXC Science Cycles

```bash
swot-reservoir-wse config set sources.pixc.science_cycles 045,046,047
```

---

## Change LakeSP MAD Threshold

```bash
swot-reservoir-wse config set sources.lakesp.mad_threshold 2.5
```

---

## Change PIXC MAD Threshold

```bash
swot-reservoir-wse config set sources.pixc.mad_threshold 2.5
```

LakeSP and PIXC thresholds are independent.

For every supported setting, see [Configuration](configuration.md).

---

# Cache

The package maintains persistent caches for:

- generated reservoir polygons; and
- downloaded LakeSP granules.

Display the cache summary:

```bash
swot-reservoir-wse cache
```

Clear reservoir footprints:

```bash
swot-reservoir-wse cache --clear-polygons
```

Clear LakeSP granules:

```bash
swot-reservoir-wse cache --clear-lakesp
```

Clear both:

```bash
swot-reservoir-wse cache --clear-all
```

PIXC granules are currently processed in temporary working directories and are not retained in a persistent PIXC granule cache.

Reservoir and LakeSP caching can be controlled independently:

```bash
swot-reservoir-wse config set polygon_cache_enabled false
```

```bash
swot-reservoir-wse config set lakesp_cache_enabled false
```

---

# Outputs

A successful extraction always produces a CSV time series.

When:

```text
generate_plot = true
```

the package also produces a PNG visualization.

---

## LakeSP Outputs

Example filenames:

```text
19.69000_73.34000_lakesp_wse.csv
19.69000_73.34000_lakesp_wse.png
```

The final LakeSP CSV contains:

```text
date
wse_median
quality_status
```

The plot uses quality-dependent markers for:

```text
GOOD
SUSPECT
DEGRADED
BAD
```

and connects the observations with a grey line.

---

## PIXC Outputs

Example filenames:

```text
19.69000_73.34000_pixc_wse.csv
19.69000_73.34000_pixc_wse.png
```

The PIXC CSV contains the daily median WSE together with additional statistics describing the accepted pixel population.

For the complete output schemas and plotting behavior, see [Outputs](outputs.md).

---

# Output Location

The default output directory is:

```text
outputs
```

relative to the directory from which **swot-reservoir-wse** is being used.

For example:

```text
D:\reservoir-analysis
```

produces outputs under:

```text
D:\reservoir-analysis\outputs
```

unless `output_dir` has been changed.

Inspect the active location with:

```bash
swot-reservoir-wse config show
```

Change it with:

```bash
swot-reservoir-wse config set output_dir results
```

---

# Disable Plot Generation

If only CSV output is required:

```bash
swot-reservoir-wse config set generate_plot false
```

Re-enable plotting with:

```bash
swot-reservoir-wse config set generate_plot true
```

---

# Example LakeSP Workflow

A complete basic LakeSP session may look like:

```bash
swot-reservoir-wse auth
```

```bash
swot-reservoir-wse config show
```

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

The resulting files are written to the configured output directory.

---

# Example PIXC Workflow

For PIXC:

```bash
swot-reservoir-wse auth
```

Optionally reduce parallel processing:

```bash
swot-reservoir-wse config set max_workers 4
```

Then run:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
```

PIXC processing can take longer than LakeSP because the package downloads and processes individual pixel-cloud observations.

---

# Restoring Default Configuration

If configuration has been changed during experimentation:

```bash
swot-reservoir-wse config reset
```

Inspect the restored configuration:

```bash
swot-reservoir-wse config show
```

Remember that resetting the configuration also clears the Earth Engine Project ID stored in `config.json`.

If needed, configure authentication again:

```bash
swot-reservoir-wse auth
```

---

# Where to Go Next

For more detailed information:

- [Authentication](authentication.md) explains Google Earth Engine and NASA Earthdata authentication.
- [Configuration](configuration.md) documents every configurable parameter.
- [Command Reference](command_reference.md) lists all CLI commands and options.
- [Package Architecture](architecture.md) explains the LakeSP and PIXC processing pipelines.
- [Outputs](outputs.md) describes the generated CSV and PNG products.