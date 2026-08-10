# Outputs

A successful **swot-reservoir-wse** run generates a reservoir-specific Water Surface Elevation (WSE) time series from the accepted SWOT observations.

The current LakeSP workflow produces two output products:

- a CSV file containing the processed WSE time series
- a PNG visualization of the time series when plot generation is enabled

---

# Water Surface Elevation Time Series

The CSV output contains one record for each accepted acquisition date.

The current output contains the following fields:

| Field            | Description                                                                                       |
| ---------------- | ------------------------------------------------------------------------------------------------- |
| `date`           | Date of the SWOT observation.                                                                     |
| `wse_median`     | Representative Water Surface Elevation for the reservoir on that date, expressed in metres.       |
| `quality_status` | Quality classification assigned to the daily WSE value from the contributing LakeSP observations. |

An example output is:

```text
date,wse_median,quality_status
2026-01-27,622.438,GOOD
2026-02-16,622.711,SUSPECT
2026-03-09,623.052,GOOD
2026-03-30,623.487,GOOD
```

The values shown above are illustrative. Actual observations depend on the supplied dam location, requested date range and available SWOT observations.

---

# How the Daily WSE is Obtained

A single SWOT acquisition can contain more than one LakeSP observation associated with the reservoir.

The package therefore does not necessarily treat every intersecting LakeSP polygon as a separate point in the final time series.

Before daily aggregation, LakeSP observations are screened using the quality information provided with the product.

The current LakeSP workflow retains observations satisfying:

```text
partial_f = 0
```

and:

```text
quality_f = 0 or 1
```

Observations representing partial coverage or observations outside the accepted quality classes are removed.

The remaining observations are grouped by acquisition date. The median WSE of the accepted observations is then used as the representative reservoir WSE for that date.

Conceptually:

```text
Accepted LakeSP observations
            ↓
Group observations by acquisition date
            ↓
Calculate median WSE for each date
            ↓
Daily reservoir WSE
```

The resulting value is stored in the `wse_median` field.

---

# Quality Status

Each daily WSE value is assigned a `quality_status` based on the quality classes of the LakeSP observations contributing to that date.

The current workflow uses the LakeSP `quality_f` values:

| LakeSP `quality_f` | Interpretation used by the package |
| -----------------: | ---------------------------------- |
|                `0` | Good                               |
|                `1` | Suspect                            |

For every acquisition date, the package counts the number of accepted good and suspect observations.

The daily quality status is assigned as follows:

```text
n_good >= n_suspect  →  GOOD
n_good <  n_suspect  →  SUSPECT
```

Therefore, `GOOD` and `SUSPECT` describe the quality composition of the observations contributing to the **daily aggregated WSE value**. They are not new quality flags supplied directly by the SWOT LakeSP product.

## `GOOD`

A daily value is classified as:

```text
GOOD
```

when the number of contributing observations with `quality_f = 0` is greater than or equal to the number with `quality_f = 1`.

For example:

```text
Good observations     : 3
Suspect observations  : 1

quality_status = GOOD
```

A tie is also classified as `GOOD`.

```text
Good observations     : 2
Suspect observations  : 2

quality_status = GOOD
```

## `SUSPECT`

A daily value is classified as:

```text
SUSPECT
```

when observations with `quality_f = 1` outnumber observations with `quality_f = 0`.

For example:

```text
Good observations     : 1
Suspect observations  : 3

quality_status = SUSPECT
```

A `SUSPECT` value is retained in the time series unless it is subsequently removed by the temporal outlier filtering stage.

---

# Temporal Outlier Filtering

After the daily WSE values have been calculated, the resulting time series undergoes an additional temporal screening step using the **Median Absolute Deviation (MAD)**.

For a set of daily WSE values \(x_1, x_2, \ldots, x_n\), the median is first calculated:

\[
\tilde{x} = \operatorname{median}(x)
\]

The Median Absolute Deviation is then:

\[
MAD = \operatorname{median}(|x_i-\tilde{x}|)
\]

For each daily WSE value, the package calculates a modified Z-score:

\[
z_i =
\frac{0.6745 |x_i-\tilde{x}|}{MAD}
\]

A daily observation is retained when:

\[
z_i \leq T
\]

where \(T\) is the configured MAD threshold.

The default value is:

```text
sources.lakesp.mad_threshold = 3.0
```

It can be changed using:

```bash
swot-wse config set sources.lakesp.mad_threshold 2.5
```

Only daily observations remaining after this stage are included in the final WSE time series.

---

# Processing Sequence

For the LakeSP workflow, the observations appearing in the final CSV have therefore passed through the following sequence:

```text
Reservoir-associated LakeSP observations
                  ↓
Remove partial observations
                  ↓
Retain good and suspect quality classes
                  ↓
Group observations by acquisition date
                  ↓
Calculate daily median WSE
                  ↓
Assign GOOD or SUSPECT quality status
                  ↓
Apply MAD-based temporal outlier filtering
                  ↓
Final reservoir WSE time series
```

---

# WSE Plot

When plot generation is enabled, the package also creates a PNG visualization of the final reservoir WSE time series.

Plot generation is controlled by:

```text
generate_plot
```

It can be enabled using:

```bash
swot-wse config set generate_plot true
```

or disabled using:

```bash
swot-wse config set generate_plot false
```

The visualization represents the accepted reservoir WSE observations across the requested observation period.

When documenting or demonstrating package output, an example containing both `GOOD` and `SUSPECT` observations is useful because it illustrates the quality information retained in the final time series.

---

# Output Location

By default, generated outputs are stored in the package's user-level runtime directory:

```text
~/.swot_wse/outputs/
```

On Windows, this normally corresponds to:

```text
C:\Users\<username>\.swot_wse\outputs\
```

The active output directory can be checked using:

```bash
swot-wse config show
```

The output location can be changed using:

```bash
swot-wse config set output_dir <path>
```

For example:

```bash
swot-wse config set output_dir D:\SWOT\outputs
```

Subsequent outputs will then be written to the configured directory.

---

# Related Configuration

The main configuration parameters affecting the generated outputs are:

| Parameter                      | Purpose                                                     |
| ------------------------------ | ----------------------------------------------------------- |
| `generate_plot`                | Enables or disables PNG plot generation.                    |
| `output_dir`                   | Determines where generated output files are stored.         |
| `sources.lakesp.mad_threshold` | Controls the threshold used for temporal outlier filtering. |

For a complete explanation of package configuration, see the [Configuration](configuration.md) documentation.

For the commands used to modify these values, see the [Command Reference](command_reference.md).
