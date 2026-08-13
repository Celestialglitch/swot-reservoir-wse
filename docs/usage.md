# Usage

This page provides a practical first-use workflow for **swot-reservoir-wse**.

It assumes that the package has already been installed. If not, begin with [Installation](installation.md).

The package supports two independently selectable SWOT observation sources:

- **LakeSP** — reservoir observations derived from the SWOT Lake Single-Pass vector product.
- **PIXC** — reservoir observations derived directly from the SWOT high-rate pixel-cloud product.

A typical session consists of:

```text
Authenticate
     │
     ▼
Inspect configuration
     │
     ▼
Choose LakeSP or PIXC
     │
     ▼
Run extraction
     │
     ▼
Inspect generated outputs
```

For the internal processing performed by each source, see [Package Architecture](architecture.md).

---

## 1. Authenticate the Required Services

Before the first extraction, configure access to the external services used by the package:

```bash
swot-reservoir-wse auth
```

This configures the two services required by the processing pipeline:

```text
Google Earth Engine
        │
        └── JRC Global Surface Water
            reservoir-footprint generation

NASA Earthdata
        │
        └── SWOT LakeSP and PIXC
            product discovery and access
```

If valid authentication information already exists, it is reused where possible.

The services can also be configured independently:

```bash
swot-reservoir-wse auth --earth-engine-only
```

```bash
swot-reservoir-wse auth --earthdata-only
```

For Project ID handling, credential storage, forced reauthentication, and credential removal, see [Authentication](authentication.md).

---

## 2. Inspect the Active Configuration

Before processing, the active runtime configuration can be inspected with:

```bash
swot-reservoir-wse config show
```

The default settings are suitable for a normal first run, so configuration changes are not required simply to begin processing.

The configuration controls parameters including:

```text
reservoir-footprint generation
LakeSP processing
PIXC processing
quality filtering
science-cycle selection
parallel workers
persistent caching
temporary storage
output location
plot generation
```

For the complete parameter reference, see [Configuration](configuration.md).

---

## 3. Choose an Observation Source

Every extraction must explicitly select either:

```text
lakesp
```

or:

```text
pixc
```

using the `--source` argument.

For example:

```bash
--source lakesp
```

selects the LakeSP processing pipeline, while:

```bash
--source pixc
```

selects the PIXC processing pipeline.

The two sources are processed independently.

There is no automatic source selection and no automatic fallback from one source to the other.

LakeSP is generally the simpler source for reservoir-level WSE extraction because the product already contains vectorized lake observations.

PIXC operates on individual pixel-cloud measurements and can therefore require substantially greater download volume, memory, disk activity, and processing time.

---

## 4. Run a LakeSP Extraction

Suppose the target dam is located at:

```text
Latitude  : 19.690
Longitude : 73.340
```

and the required observation period is:

```text
2026-01-20 to 2026-07-16
```

Run:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

The supplied coordinates identify the dam associated with the target reservoir.

They are **not** treated as the reservoir boundary itself.

During processing, **swot-reservoir-wse** first obtains the reservoir footprint corresponding to the supplied location and then uses that footprint to identify relevant LakeSP observations.

At a high level:

```text
Dam location
     │
     ▼
Reservoir footprint
     │
     ▼
LakeSP observations
     │
     ▼
Reservoir WSE time series
     │
     ▼
CSV + optional PNG
```

The complete scientific and computational processing sequence is documented in [Package Architecture](architecture.md).

---

## 5. Run a PIXC Extraction

The same reservoir and observation period can be processed independently from PIXC:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
```

The initial reservoir-identification stage is shared with LakeSP, but the subsequent PIXC processing pipeline is different.

At a high level:

```text
Dam location
     │
     ▼
Reservoir footprint
     │
     ▼
PIXC pixel-cloud observations
     │
     ▼
Reservoir WSE time series
     │
     ▼
CSV + optional PNG
```

PIXC products contain large collections of individual pixel measurements. Processing can therefore require considerably more resources than LakeSP.

On a machine with limited memory, the maximum number of concurrent workers can be reduced before running PIXC:

```bash
swot-reservoir-wse config set max_workers 2
```

The appropriate value depends on the available hardware and the products being processed.

---

## 6. Locate the Generated Outputs

By default, successful extraction products are written to:

```text
outputs/
```

relative to the directory from which the package is being used.

For example, if processing is run from:

```text
D:\reservoir-analysis
```

the default output location is:

```text
D:\reservoir-analysis\outputs
```

A LakeSP run produces a CSV with a source-specific filename such as:

```text
19.69000_73.34000_lakesp_wse.csv
```

and, when plot generation is enabled:

```text
19.69000_73.34000_lakesp_wse.png
```

A PIXC run similarly produces:

```text
19.69000_73.34000_pixc_wse.csv
```

and optionally:

```text
19.69000_73.34000_pixc_wse.png
```

LakeSP and PIXC results are written separately. Running both sources for the same reservoir does not merge their observations into a single time series.

For CSV fields and plotting behaviour, see [Outputs](outputs.md).

---

## 7. Change the Output Directory

The active output location can be changed through the configuration system.

For example:

```bash
swot-reservoir-wse config set output_dir results
```

Subsequent outputs will then be written under:

```text
results/
```

An absolute path can also be supplied.

For example, in Windows PowerShell:

```powershell
swot-reservoir-wse config set output_dir D:\swot-output-test
```

The configured value can be confirmed with:

```bash
swot-reservoir-wse config show
```

---

## 8. Disable Plot Generation

CSV generation is always part of a successful extraction.

If the PNG visualization is not required, disable it with:

```bash
swot-reservoir-wse config set generate_plot false
```

Run the extraction normally:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

Only the CSV output will be generated.

Plot generation can be restored with:

```bash
swot-reservoir-wse config set generate_plot true
```

---

## 9. Reusing Cached Data

The package can reuse previously generated reservoir footprints and downloaded LakeSP products.

Inspect the current persistent cache with:

```bash
swot-reservoir-wse cache
```

A typical workflow therefore does not require manually clearing cached data between runs.

If the same dam location is processed again, the cached reservoir footprint can be reused when reservoir-polygon caching is enabled.

Similarly, previously downloaded LakeSP products can be reused when LakeSP caching is enabled.

PIXC products are currently processed through temporary workspaces and are not retained in a persistent PIXC granule cache.

Cache contents can be cleared only when there is a specific reason to force regeneration or redownload.

For example:

```bash
swot-reservoir-wse cache --clear-polygons
```

removes cached reservoir footprints, while:

```bash
swot-reservoir-wse cache --clear-lakesp
```

removes cached LakeSP products.

To clear all persistent package caches:

```bash
swot-reservoir-wse cache --clear-all
```

---

## 10. Example: Complete LakeSP Session

For a first LakeSP extraction, the complete command sequence can be as simple as:

```bash
# Authenticate Google Earth Engine and NASA Earthdata
swot-reservoir-wse auth

# Inspect the active configuration
swot-reservoir-wse config show

# Generate the LakeSP reservoir WSE time series
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp

# Inspect the persistent cache after processing
swot-reservoir-wse cache
```

With the default configuration, the resulting products are written under:

```text
outputs/
```

No additional configuration changes are required for a normal first LakeSP run.

---

## 11. Example: Complete PIXC Session

A corresponding PIXC session is:

```bash
# Authenticate Google Earth Engine and NASA Earthdata
swot-reservoir-wse auth

# Inspect the active configuration
swot-reservoir-wse config show

# Reduce concurrency if required by the available memory
swot-reservoir-wse config set max_workers 2

# Generate the PIXC reservoir WSE time series
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
```

The worker-count change is optional.

PIXC processing may take substantially longer than LakeSP because the package downloads and processes pixel-cloud products rather than working only with vectorized lake observations.

---

## 12. Example: Run Both Sources

LakeSP and PIXC can also be processed independently for the same reservoir and observation period.

For example:

```bash
# LakeSP
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp

# PIXC
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source pixc
```

The result is two independently derived reservoir WSE time series:

```text
outputs/
│
├── 19.69000_73.34000_lakesp_wse.csv
├── 19.69000_73.34000_lakesp_wse.png
├── 19.69000_73.34000_pixc_wse.csv
└── 19.69000_73.34000_pixc_wse.png
```

The package does not automatically compare, combine, or reconcile the LakeSP and PIXC results.

---

## 13. Common Configuration Changes

Most processing behaviour can be changed through:

```bash
swot-reservoir-wse config set <key> <value>
```

Some common examples are:

```bash
# Change parallel worker count
swot-reservoir-wse config set max_workers 4

# Retain only GOOD and SUSPECT LakeSP observations
swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect

# Restrict LakeSP processing to selected science cycles
swot-reservoir-wse config set sources.lakesp.science_cycles 045,046,047

# Restrict PIXC processing to selected science cycles
swot-reservoir-wse config set sources.pixc.science_cycles 045,046,047

# Change LakeSP temporal MAD threshold
swot-reservoir-wse config set sources.lakesp.mad_threshold 2.5

# Change PIXC temporal MAD threshold
swot-reservoir-wse config set sources.pixc.mad_threshold 2.5

# Change output directory
swot-reservoir-wse config set output_dir results

# Disable PNG generation
swot-reservoir-wse config set generate_plot false
```

Their definitions and effects are documented in [Configuration](configuration.md).

---

## 14. Restore the Default Configuration

If configuration values have been changed during testing or experimentation, restore the package defaults with:

```bash
swot-reservoir-wse config reset
```

Then inspect the resulting configuration:

```bash
swot-reservoir-wse config show
```

The reset also restores:

```text
earth_engine_project = null
```

because the Earth Engine Project ID is part of `config.json`.

Google-managed Earth Engine OAuth credentials and NASA Earthdata credentials stored outside `config.json` are not removed by `config reset`.

If necessary, configure the required authentication state again with:

```bash
swot-reservoir-wse auth
```

---

## 15. Command Help

The CLI provides built-in help commands at every major command level.

Display the available commands:

```bash
swot-reservoir-wse --help
```

Extraction options:

```bash
swot-reservoir-wse extract --help
```

Authentication options:

```bash
swot-reservoir-wse auth --help
```

Configuration commands:

```bash
swot-reservoir-wse config --help
```

Cache commands:

```bash
swot-reservoir-wse cache --help
```

For the complete CLI reference, see [Command Reference](command_reference.md).

---

## Related Documentation

After this first-use guide, the documentation is divided by purpose:

- [Package Architecture](architecture.md) — how reservoir identification, LakeSP processing, and PIXC processing work internally.
- [Authentication](authentication.md) — Google Earth Engine and NASA Earthdata authentication and credential handling.
- [Configuration](configuration.md) — every configurable processing parameter and its effect.
- [Command Reference](command_reference.md) — complete CLI syntax, options, and command behaviour.
- [Outputs](outputs.md) — generated CSV fields and PNG visualizations.
