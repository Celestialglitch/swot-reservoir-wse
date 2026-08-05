# Package Architecture

This document provides a high-level overview of the internal architecture of **swot-reservoir-wse** and explains how the major software components interact to generate reservoir-specific Water Surface Elevation (WSE) time series from SWOT observations.

---

# Architecture Overview

The package is organized around a modular SWOT-source architecture. Instead of coupling the processing pipeline to a single SWOT science product, all supported observation products implement a common processing interface. This design allows new SWOT products to be integrated without changing the command-line interface or the overall workflow.

The current release supports the **SWOT Level-2 Lake Single Pass (LakeSP) Vector Data Product (Version D)**.


---

# Major Components

The package consists of several independent components that work together during execution.

## Command-Line Interface (CLI)

The CLI serves as the entry point to the package. It validates user input, loads the package configuration, and starts the requested workflow.

Supported command groups include:

* reservoir WSE extraction;
* Google Earth Engine authentication;
* configuration management; and
* cache management.

---

## Configuration System

The configuration system stores runtime parameters that control package behaviour.

Examples include:

* search radius;
* projected coordinate system;
* cache locations;
* output locations;
* processing options; and
* observation-source parameters.

These settings can be viewed or modified without changing the source code.

---

## Reservoir Footprint Extraction

The first processing stage identifies the reservoir footprint polygon of the requested dam location.

This step uses **Google Earth Engine (GEE)** together with the **Joint Research Centre (JRC) Global Surface Water** dataset.

The user supplies dam coordinates, while the package automatically extracts a representative reservoir polygon surrounding that location.

If enabled, extracted polygons are cached locally to avoid repeated processing.

---

## Observation Granule Discovery

Once the reservoir footprint has been determined, the package searches for SWOT observation granules covering both the requested time interval and the reservoir location.

Product discovery is performed through **NASA Earthdata**, which provides access to publicly available SWOT science products.

---

## Observation Processing

Each supported SWOT observation product is processed by its own dedicated source module.

Although different products may contain different variables or internal structures, each source module follows the same general responsibilities:

* identify observations intersecting the reservoir polygon;
* extract Water Surface Elevation measurements;
* perform product-specific quality control;
* generate a standardized time series.

This abstraction allows multiple SWOT products to share a common downstream workflow.

---

## Quality Filtering and Outlier removal

Raw observations frequently contain measurements that should not be included in the final time series.

Each observation source therefore applies its own filtering procedure before producing the final output.

For the current LakeSP implementation, filtering includes quality screening with both good and suspect options followed by statistical outlier removal.

---

## Output Generation

After filtering is complete, the package generates the final products.

The current release produces:

* a CSV file containing the Water Surface Elevation time series; and
* a PNG visualization of the extracted observations.

Output locations are configurable through the package configuration system.

---

## Cache Management

To reduce repeated downloads and computational overhead, the package maintains local caches.

The current implementation supports caching of:

* extracted reservoir polygons; and
* downloaded LakeSP observation products.

Cached data are reused automatically whenever possible.

---

# External Services

The package relies on several external platforms throughout the processing workflow.

| Service                              | Purpose                                                                                 |
| ------------------------------------ | --------------------------------------------------------------------------------------- |
| **Google Earth Engine (GEE)**        | Reservoir footprint extraction using satellite-derived surface-water data.              |
| **JRC Global Surface Water Dataset** | Provides the global water-occurrence dataset used for identifying reservoir boundaries. |
| **NASA Earthdata**                   | Discovery and download of SWOT observation product granules.                            |

---

# Data Flow

A typical execution follows the sequence below.

```text
User Coordinates
        │
        ▼
Google Earth Engine
        │
        ▼
JRC Global Surface Water
        │
        ▼
Reservoir Footprint
        │
        ▼
NASA Earthdata Search
        │
        ▼
SWOT Observation Products
        │
        ▼
Observation Extraction
        │
        ▼
Quality Filtering
        │
        ▼
Water Surface Elevation Time Series
        │
        ├────────► CSV Output
        │
        └────────► PNG Visualization
```

---

# Extensibility

The package has been designed to support additional SWOT observation products without modifying the user interface.

Adding support for a new observation product generally requires implementing a new source module that performs:

* granule search;
* observation discovery;
* wse extraction and calculation;
* quality filtering; and
* conversion to the package's standardized Water Surface Elevation time-series format.

Once implemented, the new source can be integrated into the existing processing framework while preserving the same command-line workflow.
