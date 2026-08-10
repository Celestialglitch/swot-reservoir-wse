# Usage

This page describes the basic workflow for generating a reservoir-specific Water Surface Elevation (WSE) time series using **swot-reservoir-wse**.

For a complete description of every command and command-line option, see the [Command Reference](command_reference.md).

---

## Authentication

Before using **swot-reservoir-wse** for the first time, authenticate the external services required by the package.

```bash
swot-wse auth
```

The package manages authentication for both **Google Earth Engine** and **NASA Earthdata**.

Google Earth Engine is used to derive the reservoir footprint associated with the supplied dam location. NASA Earthdata is used to discover and retrieve SWOT observation products.

Existing credentials are reused whenever possible. If valid credentials are not available, the package starts the required authentication process.

The two services can also be managed independently:

```bash
swot-wse auth --earth-engine-only
swot-wse auth --earthdata-only
```

To force reauthentication of both services:

```bash
swot-wse auth --force
```

For service-specific authentication, credential removal, reauthentication and the complete set of authentication options, see the [Authentication](authentication.md) documentation.

---

## Generate a Reservoir WSE Time Series

The package requires the geographic coordinates of a dam and the period for which SWOT observations should be processed.

The general command is:

```bash
swot-wse polygon --lat <latitude> --lon <longitude> --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

For example:

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16
```

Here, `--lat` and `--lon` specify the **dam location**, rather than a predefined reservoir boundary.

From the supplied dam coordinates, the package derives the corresponding reservoir footprint from the JRC Global Surface Water dataset. This footprint provides the spatial reference for identifying relevant SWOT observations.

For the LakeSP workflow, the package searches for LakeSP granules available for the requested location and date range. Candidate granules are spatially checked against the reservoir footprint, and the LakeSP observations intersecting the reservoir are identified. The associated WSE observations are then screened using the LakeSP quality information, aggregated by acquisition date and subjected to temporal outlier filtering before the final reservoir-specific WSE time series is generated.

---

## Observation Source Selection

The SWOT observation source can be selected using the optional `--source` argument.

For example:

```bash
swot-wse polygon --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

If `--source` is omitted, its default value is:

```text
auto
```

`auto` is the package's automatic source-selection mode. It allows the processing pipeline to select an implemented SWOT observation source without requiring the user to specify one explicitly.

In the current release, **LakeSP is the only implemented observation source**. Therefore:

```text
auto → lakesp
```

Additional SWOT observation products can be incorporated through the package's observation-source architecture, but they are not implemented in the current release.

---

## Configuration

The active package configuration can be displayed using:

```bash
swot-wse config show
```

Individual configuration values can be changed using:

```bash
swot-wse config set <key> <value>
```

For example, the maximum number of worker threads available during parallel LakeSP granule processing can be changed with:

```bash
swot-wse config set max_workers 4
```

LakeSP-specific parameters can also be modified. For example:

```bash
swot-wse config set sources.lakesp.search_buffer_degrees 0.75
```

Selected SWOT science cycles can be specified using comma-separated values:

```bash
swot-wse config set sources.lakesp.science_cycles 045,046,047
```

The configuration system controls reservoir footprint extraction, LakeSP processing, parallel execution, caching, output generation and other runtime behaviour.

The purpose, accepted values and effect of each configurable parameter are described in the [Configuration](configuration.md) documentation.

---

## Cache

The package maintains a local cache to avoid repeating reservoir footprint extraction and downloading LakeSP products that are already available.

Display the current cache status using:

```bash
swot-wse cache
```

The reservoir polygon cache can be cleared independently:

```bash
swot-wse cache --clear-polygons
```

Downloaded LakeSP granules can also be removed independently:

```bash
swot-wse cache --clear-lakesp
```

To clear both caches:

```bash
swot-wse cache --clear-all
```

Caching is enabled by default. Reservoir polygon caching and LakeSP granule caching can be enabled or disabled independently through the package configuration.

---

## Outputs

A successful processing run generates a CSV file containing the reservoir-specific Water Surface Elevation time series.

When plot generation is enabled, a PNG visualization of the time series is also generated.

The CSV contains the observation date, representative daily WSE value and associated quality status.

For the LakeSP workflow, the representative WSE for each acquisition date is obtained from the median of the accepted LakeSP observations for that date. The quality status indicates whether the daily value is predominantly supported by observations classified as `GOOD` or `SUSPECT` according to the LakeSP quality screening performed by the package.

The resulting daily series is subsequently screened for temporal outliers before being written to the final output.

Detailed descriptions of the generated files and quality-status values are provided in the [Outputs](outputs.md) documentation.

---

## Where to Go Next

After completing a basic processing run:

- [Authentication](authentication.md) explains Google Earth Engine and NASA Earthdata authentication and credential management.
- [Configuration](configuration.md) explains every configurable processing parameter and how it affects execution.
- [Command Reference](command_reference.md) lists all available CLI commands and options.
- [Package Architecture](architecture.md) explains the major processing components and data flow.
- [Outputs](outputs.md) describes the generated WSE products and quality-status information.