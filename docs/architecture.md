# Package Architecture

This document provides a high-level overview of how **swot-reservoir-wse** transforms user-supplied dam coordinates into reservoir-specific Water Surface Elevation (WSE) time series from SWOT observations. It focuses on the processing workflow implemented by the package rather than its internal source-code organization.

---

# Architecture Overview

The package follows a modular observation-source architecture in which each supported SWOT observation product is processed through a common workflow while retaining its own product-specific processing logic.

This design separates the overall processing pipeline from individual SWOT products, allowing new observation products to be integrated without changing the user interface or the overall workflow.

The current release supports the **SWOT Level-2 Lake Single Pass (LakeSP) Vector Data Product (Version D)**.

---

# Processing Architecture

The package implements the following processing stages.

## Reservoir Footprint Generation

The workflow begins with the geographic location of a dam supplied by the user.

Since SWOT observations describe water bodies rather than dam locations, the package first derives the corresponding reservoir footprint using the **Joint Research Centre (JRC) Global Surface Water** dataset through **Google Earth Engine**. The generated reservoir footprint provides the spatial reference required for all subsequent processing.

---

## LakeSP Granule Identification

Using the generated reservoir footprint together with the requested observation period, the package identifies the subset of SWOT LakeSP granules that may contain observations of the target reservoir.

Granule discovery is performed through **NASA Earthdata**, ensuring that only relevant SWOT LakeSP granules are processed.

---

## Reservoir Observation Association

Each LakeSP granule contains observations for numerous lakes, reservoirs, rivers, and other inland water bodies. Consequently, only a subset of the observations within a granule correspond to the requested reservoir.

The package spatially intersects the generated reservoir footprint with the LakeSP observation polygons to identify all observations belonging to the target reservoir. The corresponding LakeSP identifiers are then used to isolate only the relevant observations for subsequent processing.

This transforms the original LakeSP granules into a reservoir-specific observation dataset.

---

## Observation Screening and Time-Series Generation

The extracted LakeSP observations are processed through a multi-stage workflow before constructing the final Water Surface Elevation (WSE) time series.

Individual observations are first screened using the official LakeSP quality and partial-coverage indicators. The accepted observations are then aggregated on an acquisition-day basis, where the median WSE is adopted as the representative daily elevation. Finally, the resulting daily time series is evaluated using the Median Absolute Deviation (MAD) to identify and remove temporal outliers.

The remaining observations constitute the final reservoir-specific Water Surface Elevation time series.

---

## Output Generation

The package currently generates:

- a CSV file containing the reservoir-specific Water Surface Elevation time series; and
- a PNG visualization of the generated time series.

Output locations are configurable through the package configuration system.

---

## Configuration System

The package provides a centralized configuration system that controls runtime behaviour without requiring changes to the source code.

Configuration options include processing parameters, output locations, cache locations, observation-source parameters and other execution settings.

---

## Cache Management

To reduce repeated processing, the package maintains local caches for generated reservoir footprints and downloaded SWOT observation products.

Cached data are reused automatically whenever possible, reducing processing time for subsequent executions.

---

# External Services

The package integrates several external platforms throughout the processing workflow.

| Service                              | Purpose                                                                                    |
| ------------------------------------ | ------------------------------------------------------------------------------------------ |
| **Google Earth Engine (GEE)**        | Executes large-scale geospatial processing for reservoir footprint generation.             |
| **JRC Global Surface Water Dataset** | Provides historical global surface-water observations used to derive reservoir footprints. |
| **NASA Earthdata**                   | Provides discovery and access to SWOT observation products.                                |

---

# Processing Flow

```text
  User-supplied Dam Coordinates
                │
                ▼
 Reservoir Footprint Generation
                │
                ▼
 LakeSP Granule Identification
                │
                ▼
Reservoir Observation Association
                │
                ▼
        Quality Control
                │
                ▼
  Reservoir-level WSE Generation
                │
                ▼
    Reservoir WSE Time Series
                │
        ┌───────┴────────┐
        ▼                ▼
      CSV              PNG
```

---

# Extensibility

The modular observation-source architecture allows additional SWOT observation products to be integrated while preserving the same processing workflow and command-line interface.

Each observation product is responsible for implementing its own observation discovery, reservoir association, quality-control and WSE generation procedures while producing a standardized reservoir-specific Water Surface Elevation time series. This allows future SWOT products to be integrated without changing the command-line interface or the overall processing workflow.
