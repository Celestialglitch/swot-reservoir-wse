# Package Architecture

This document provides a high-level overview of how **swot-wse** transforms a user-supplied dam location into a reservoir-specific Water Surface Elevation (WSE) time series using observations from the Surface Water and Ocean Topography (SWOT) mission.

The document describes the processing architecture and data flow of the package rather than the organization of individual Python modules.

---

# Architecture Overview

**swot-wse** follows a modular observation-source architecture.

The package separates three major responsibilities:

1. identifying the reservoir associated with a supplied dam location;
2. processing observations from a selected SWOT data product; and
3. producing a standardized reservoir-level WSE time series.

Reservoir footprint generation and output handling are shared across observation sources, while product-specific discovery, extraction, quality screening, and aggregation are handled by independent source pipelines.

The current release supports:

- **SWOT Level-2 Lake Single Pass (LakeSP) Vector Data Product, Version D**
- **SWOT Level-2 High Rate Pixel Cloud (PIXC) Data Product, Version D**

The observation source is selected explicitly by the user when running the extraction command.

---

# Processing Architecture

## 1. Reservoir Footprint Generation

The workflow begins with the latitude and longitude of a dam supplied by the user.

SWOT observations describe water surfaces rather than dam locations. The package therefore first derives a reservoir footprint associated with the supplied coordinates.

Reservoir extraction uses the **JRC Global Surface Water** dataset through **Google Earth Engine**.

A search region is constructed around the supplied dam location, and surface-water occurrence is used to identify candidate water-body polygons. If the dam lies within one or more candidate polygons, the largest containing polygon is selected. Otherwise, the nearest candidate polygon is used.

The resulting reservoir footprint is transformed to geographic coordinates and becomes the common spatial reference for the selected SWOT observation pipeline.

Generated reservoir footprints may be cached locally and reused in later executions.

---

## 2. Observation-Source Selection

After obtaining the reservoir footprint, processing is delegated to the observation source selected by the user.

The currently supported source pipelines are:

```text
                    Reservoir Footprint
                            │
                            ▼
                    Observation Source
                      ┌─────┴─────┐
                      │           │
                      ▼           ▼
                   LakeSP        PIXC
                   Pipeline      Pipeline