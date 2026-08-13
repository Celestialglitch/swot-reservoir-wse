# Outputs

A successful **swot-reservoir-wse** extraction generates a reservoir-specific Water Surface Elevation (WSE) time series from the selected SWOT observation source.

The current release supports two independent processing sources:

- **LakeSP**
- **PIXC**

Both sources generate a CSV time series. When plot generation is enabled, a PNG visualization is generated alongside the CSV.

Because LakeSP and PIXC contain different source-level information, their CSV schemas are not identical.

---

## Output Files

Output filenames contain:

- the supplied latitude,
- the supplied longitude,
- the selected SWOT source, and
- the output type.

For example, a LakeSP run may generate:

    19.69000_73.34000_lakesp_wse.csv
    19.69000_73.34000_lakesp_wse.png

while a PIXC run for the same location may generate:

    19.69000_73.34000_pixc_wse.csv
    19.69000_73.34000_pixc_wse.png

This allows outputs produced from different SWOT products to coexist without overwriting one another.

---

## LakeSP Output

The LakeSP CSV contains one record for each acquisition date remaining after quality screening, daily aggregation, and temporal outlier filtering.

The final LakeSP output contains:

| Field | Description |
| --- | --- |
| date | Acquisition date associated with the daily reservoir observation. |
| wse_median | Median WSE of the retained LakeSP observations contributing to that date, in metres. |
| quality_status | Package-derived representative quality class for the daily observation. |

An illustrative output is:

    date,wse_median,quality_status
    2026-01-27 00:00:00+00:00,130.0410,SUSPECT
    2026-02-09 00:00:00+00:00,129.4380,SUSPECT
    2026-03-02 00:00:00+00:00,129.0610,SUSPECT
    2026-07-05 00:00:00+00:00,126.3205,DEGRADED

The values above are illustrative. Actual results depend on the supplied location, date range, active quality configuration, and available SWOT observations.

### LakeSP Observation Screening

Before daily aggregation, reservoir-associated LakeSP observations are screened using the LakeSP product fields used by the package.

Partial observations are removed:

    partial_f = 0

must be satisfied.

The remaining observations are filtered according to:

    sources.lakesp.accepted_quality_flags

The supported quality classes are:

    good
    suspect
    degraded
    bad

The default configuration retains:

    good
    suspect
    degraded

and excludes:

    bad

The accepted classes can be changed through the configuration system.

For example, retain only GOOD observations:

    swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good

Retain GOOD and SUSPECT:

    swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect

Retain all supported classes:

    swot-reservoir-wse config set sources.lakesp.accepted_quality_flags good,suspect,degraded,bad

---

### LakeSP Daily WSE

A single acquisition date can contain more than one retained LakeSP observation associated with the reservoir.

The package therefore groups observations by acquisition date and calculates:

    wse_median = median of retained WSE observations on that date

Conceptually:

    Reservoir-associated LakeSP observations
                      │
                      ▼
              Remove partial data
                      │
                      ▼
           Apply configured quality
                 class filter
                      │
                      ▼
           Group by acquisition date
                      │
                      ▼
              Calculate median WSE
                      │
                      ▼
              Daily reservoir WSE

The resulting value is written to:

    wse_median

---

### LakeSP Daily Quality Status

The quality_status field is a **package-derived daily status**. It is not a new quality flag contained directly in the original SWOT product.

The package uses the retained LakeSP quality classes contributing to each acquisition date.

The mapping used by the current implementation is:

| LakeSP quality value | Package label |
| ---: | --- |
| 0 | GOOD |
| 1 | SUSPECT |
| 2 | DEGRADED |
| 3 | BAD |

The most frequent retained quality class on a date becomes the daily quality_status.

For example:

    GOOD      : 3
    SUSPECT   : 1
    DEGRADED  : 0

    quality_status = GOOD

If multiple classes have the same frequency, the poorer quality class is selected.

The ordering used for tie resolution is:

    GOOD < SUSPECT < DEGRADED < BAD

For example:

    GOOD      : 2
    SUSPECT   : 2

    quality_status = SUSPECT

and:

    SUSPECT   : 1
    DEGRADED  : 1

    quality_status = DEGRADED

Only classes that passed the configured observation-level quality filter can contribute to the daily status.

---

### LakeSP Temporal Outlier Filtering

After daily WSE aggregation, the LakeSP time series undergoes temporal screening using the **Median Absolute Deviation (MAD)**.

For daily WSE values:

    x1, x2, ..., xn

the median is:

    median(WSE)

The Median Absolute Deviation is:

    MAD = median(|WSE - median(WSE)|)

The modified Z-score is:

    modified_z =
    0.6745 × |WSE - median(WSE)| / MAD

A daily observation is retained when:

    modified_z <= sources.lakesp.mad_threshold

The default threshold is:

    3.0

It can be changed with:

    swot-reservoir-wse config set sources.lakesp.mad_threshold 2.5

Only observations remaining after this stage appear in the final LakeSP CSV and PNG.

---

### LakeSP Processing Sequence

The final LakeSP output therefore follows:

    Reservoir-associated LakeSP observations
                      │
                      ▼
           Remove partial observations
                      │
                      ▼
        Apply configured quality classes
                      │
                      ▼
           Group by acquisition date
                      │
                      ▼
            Calculate median WSE
                      │
                      ▼
       Derive representative quality status
                      │
                      ▼
           Apply temporal MAD filter
                      │
                      ▼
            Final LakeSP time series

---

### LakeSP Plot

When plotting is enabled, LakeSP observations are displayed using quality-dependent circular markers.

The current visualization uses:

| Quality status | Marker colour |
| --- | --- |
| GOOD | Green |
| SUSPECT | Orange |
| DEGRADED | Red |
| BAD | Black |

The daily observations are connected by a grey line to show the temporal progression of reservoir WSE.

The quality-status legend is placed outside the plotting area so that it does not cover the data.

The legend lists all supported LakeSP quality classes. A class does not need to be present in a particular time series for its meaning to remain visible in the figure.

---

## PIXC Output

The PIXC pipeline operates on reservoir-intersecting PIXC water pixels and produces one aggregated reservoir observation per acquisition date.

The final PIXC CSV contains:

| Field | Description |
| --- | --- |
| date | Acquisition date of the aggregated PIXC observation. |
| wse_median | Median WSE of accepted reservoir pixels on that date. |
| wse_mean | Mean WSE of accepted reservoir pixels. |
| wse_std | Standard deviation of accepted pixel WSE values. |
| wse_min | Minimum accepted pixel WSE. |
| wse_max | Maximum accepted pixel WSE. |
| pixel_count | Number of accepted PIXC pixels contributing to the daily observation. |
| mean_water_frac | Mean water_frac value of the retained pixels. |
| mean_phase_noise | Mean phase_noise_std value of the retained pixels. |

An illustrative PIXC output is:

    date,wse_median,wse_mean,wse_std,wse_min,wse_max,pixel_count,mean_water_frac,mean_phase_noise
    2026-02-09,129.480713,129.512650,1.017850,121.815918,163.244461,10024,0.956371,0.027555
    2026-03-02,129.146469,129.168106,0.615328,123.090378,165.105972,10641,0.982236,0.027686
    2026-03-09,128.553986,128.561295,0.275325,125.510323,132.760345,9780,0.997505,0.035850

Actual values depend on the reservoir, observation period, available PIXC granules, and active processing configuration.

### PIXC Water Surface Elevation

For every accepted PIXC reservoir pixel, the package calculates:

    WSE = height - geoid

Only pixels that pass the reservoir-intersection, water-classification, quality-bit, and finite-value checks contribute to daily aggregation.

The accepted pixels are grouped by acquisition date.

The median pixel WSE becomes the representative reservoir WSE:

    wse_median

Additional statistics are retained in the CSV to provide information about the distribution and quantity of contributing PIXC pixels.

---

### PIXC Temporal Outlier Filtering

After daily PIXC aggregation, the wse_median series undergoes temporal MAD filtering.

The same modified Z-score formulation used for LakeSP is applied:

    MAD = median(|WSE - median(WSE)|)

    modified_z =
    0.6745 × |WSE - median(WSE)| / MAD

A daily observation is retained when:

    modified_z <= sources.pixc.mad_threshold

The default PIXC threshold is:

    3.0

It can be changed independently of the LakeSP threshold:

    swot-reservoir-wse config set sources.pixc.mad_threshold 2.5

---

### PIXC Processing Sequence

    Reservoir-intersecting PIXC pixels
                      │
                      ▼
          Retain configured water class
                      │
                      ▼
       Apply classification-quality filter
                      │
                      ▼
             Remove invalid values
                      │
                      ▼
              Calculate pixel WSE
                      │
                      ▼
           Group by acquisition date
                      │
                      ▼
       Calculate daily WSE statistics
                      │
                      ▼
           Apply temporal MAD filter
                      │
                      ▼
             Final PIXC time series

---

### PIXC Plot

When plotting is enabled, the package produces a PNG time-series visualization of the final PIXC wse_median values.

PIXC does not use the LakeSP quality_status field, so the quality-coloured LakeSP marker scheme is not applied to PIXC plots.

---

## Output Location

By default:

    output_dir = outputs

Relative output paths are resolved from the directory in which **swot-reservoir-wse** is being used.

For example, if the command is run from:

    D:\reservoir-analysis

the default output location is:

    D:\reservoir-analysis\outputs

The active setting can be inspected with:

    swot-reservoir-wse config show

Change the output location with:

    swot-reservoir-wse config set output_dir <path>

For example:

    swot-reservoir-wse config set output_dir results

or with an absolute path:

    swot-reservoir-wse config set output_dir D:\SWOT\outputs

---

## Plot Generation

Plot generation is controlled by:

    generate_plot

Enable plots:

    swot-reservoir-wse config set generate_plot true

Disable plots:

    swot-reservoir-wse config set generate_plot false

Disabling plots does not disable CSV generation.

---

## Related Configuration

The main configuration parameters affecting final outputs include:

| Parameter | Purpose |
| --- | --- |
| generate_plot | Enables or disables PNG generation. |
| output_dir | Controls where output files are written. |
| sources.lakesp.accepted_quality_flags | Controls which LakeSP quality classes contribute to processing. |
| sources.lakesp.mad_threshold | Controls LakeSP temporal outlier filtering. |
| sources.pixc.water_classification | Controls which PIXC classification value is retained. |
| sources.pixc.mad_threshold | Controls PIXC temporal outlier filtering. |

For complete configuration details, see [Configuration](configuration.md).

For the commands used to modify these parameters, see the [Command Reference](command_reference.md).

For the complete processing design, see [Package Architecture](architecture.md).
