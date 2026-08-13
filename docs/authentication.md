# Authentication

**swot-reservoir-wse** uses two external services that require authentication:

- **Google Earth Engine (GEE)** — used to derive reservoir footprints from the JRC Global Surface Water dataset.
- **NASA Earthdata** — used to discover and retrieve SWOT observation products.

Authentication for both services is managed through the `swot-reservoir-wse auth` command.

---

## Authenticate

To configure both Google Earth Engine and NASA Earthdata, run:

```bash
swot-reservoir-wse auth
```

The command checks each service independently.

Existing credentials are reused when possible. If authentication cannot be established from existing credentials, **swot-wse** starts the appropriate authentication procedure.

You can also configure either service separately:

```bash
swot-wse auth --earth-engine-only
swot-wse auth --earthdata-only
```

---

# Google Earth Engine

Google Earth Engine authentication requires both:

1. valid Google Earth Engine credentials; and
2. a Google Cloud Project ID with access to Earth Engine.

The Project ID used by **swot-reservoir-wse** is stored in the package runtime configuration.

## Standard Authentication

To manage only Google Earth Engine authentication, run:

```bash
swot-reservoir-wse auth --earth-engine-only
```

If no Earth Engine Project ID is configured, you will be prompted for one:

```text
Google Earth Engine project ID:
```

Enter the **Project ID**, not the project name or project number.

You can provide it directly instead:

```bash
swot-reservoir-wse auth --earth-engine-only --project-id my-earth-engine-project
```

The package first attempts to initialize Earth Engine using the available Google credentials. If authentication is required, the standard Earth Engine authentication flow is started.

After successful initialization, the Project ID is saved in the active `config.json` and reused for subsequent runs from that working directory.

---

## Change Account or Project

To explicitly run the Earth Engine authentication flow again:

```bash
swot-reservoir-wse auth --earth-engine-only --force
```

This is useful when changing the Google account used for Earth Engine.

A different project can be selected at the same time:

```bash
swot-reservoir-wse auth --earth-engine-only --force --project-id another-earth-engine-project
```

The successfully initialized Project ID becomes the Earth Engine project stored in the active configuration.

---

## Remove the Configured Project

To remove the Earth Engine Project ID stored by **swot-wse**:

```bash
swot-reservoir-wse auth --earth-engine-only --remove
```

This sets the Earth Engine Project ID stored by **swot-reservoir-wse** to `null`.

The command does **not** delete Google-managed OAuth credentials. Those credentials are managed by the Google Earth Engine authentication system rather than by **swot-reservoir-wse**.

As a result, authenticating again may still reuse the previously authenticated Google account. The `--remove` operation only removes authentication information that **swot-wse** manages itself.

---

# NASA Earthdata

Access to SWOT products requires a NASA Earthdata Login account.

**swot-reservoir-wse** uses the Earthdata Login machine entry:

```text
urs.earthdata.nasa.gov
```

---

## Configure Earthdata

Run:

```bash
swot-reservoir-wse auth --earthdata-only
```

If an Earthdata entry already exists, **swot-wse** attempts to validate and reuse it.

Otherwise, you will be prompted for your Earthdata Login credentials:

```text
Earthdata Login username:
Earthdata password:
```

Password input is hidden while typing.

Credentials are validated before they are stored. After writing the netrc entry, **swot-wse** verifies that the stored credentials can be used successfully.

---

## Credential File

Earthdata credentials are stored in the user's standard netrc file.

### Windows

```text
%USERPROFILE%\_netrc
```

### Linux and macOS

```text
~/.netrc
```

On POSIX systems, **swot-reservoir-wse** restricts the credential file permissions to:

```text
0600
```

so that the file is readable and writable only by its owner.

> **Security note**
>
> Netrc stores credentials as plain text. Do not use persistent netrc credentials on a shared or untrusted machine.

---

## Replace Earthdata Credentials

To discard the existing Earthdata entry and authenticate again:

```bash
swot-reservoir-wse auth --earthdata-only --force
```

The existing `urs.earthdata.nasa.gov` entry is removed before new credentials are requested.

The replacement credentials are validated before being written to the netrc file.

Use this when changing Earthdata accounts or replacing invalid credentials.

---

## Remove Earthdata Credentials

To remove the Earthdata credentials stored by **swot-wse**:

```bash
swot-reservoir-wse auth --earthdata-only --remove
```

Only the entry for:

```text
urs.earthdata.nasa.gov
```

is removed. Other machine entries in the same netrc file are preserved.

---

# Reauthentication

To force authentication for both services:

```bash
swot-reservoir-wse auth --force
```

For Earth Engine, this starts a new Earth Engine authentication flow.

For Earthdata, the existing Earthdata netrc entry is removed and replacement credentials are requested.

If an Earth Engine Project ID is already configured, it continues to be used unless another one is supplied:

```bash
swot-reservoir-wse auth --force --project-id another-earth-engine-project
```

---

# Removing Authentication Information

To remove authentication information managed directly by **swot-reservoir-wse** for both services, run:

```bash
swot-reservoir-wse auth --remove
```

This:

- removes the Earth Engine Project ID from the active `config.json`;
- removes the `urs.earthdata.nasa.gov` entry from the user's netrc file.

Google Earth Engine OAuth credentials managed by Google's authentication system are **not** deleted.

---

# Authentication Options

| Option | Description |
| --- | --- |
| `--project-id <project-id>` | Supplies the Google Earth Engine Project ID directly. |
| `--force` | Forces reauthentication instead of reusing existing credentials. |
| `--remove` | Removes authentication information managed directly by **swot-reservoir-wse**. |
| `--earth-engine-only` | Applies the requested authentication operation only to Google Earth Engine. |
| `--earthdata-only` | Applies the requested authentication operation only to NASA Earthdata. |

`--force` and `--remove` are mutually exclusive.

`--earth-engine-only` and `--earthdata-only` are also mutually exclusive.

`--project-id` cannot be used together with `--earthdata-only`.

---

# Authentication During Processing

Authentication setup and normal data processing are intentionally separated.

During reservoir processing:

- Google Earth Engine initialization uses the Project ID stored in the active configuration and existing Earth Engine credentials.
- NASA Earthdata initialization attempts to authenticate using the Earthdata credentials stored in the user's netrc file.

If the required authentication is unavailable or invalid, processing stops with an error directing the user to run the appropriate `swot-reservoir-wse auth` command.

This avoids unexpectedly starting an interactive authentication flow in the middle of an extraction run.

---

# Credential Storage Summary

| Information | Storage Location | Managed by `swot-reservoir-wse auth --remove` |
| --- | --- | --- |
| Earth Engine Project ID | Working-directory `config.json` | Yes |
| Earth Engine authentication credentials | Google/Earth Engine authentication system | No |
| Earthdata username and password | User netrc file | Yes |

The Earth Engine Project ID is configuration rather than a secret. The runtime `config.json` should nevertheless remain local to the working directory and should not be committed to the repository.

---

# Command Options

The `auth` command supports:

| Option | Purpose |
| --- | --- |
| `--project-id <project-id>` | Specify the Google Cloud Project ID used for Earth Engine |
| `--force` | Authenticate again instead of reusing the current authentication state |
| `--remove` | Remove authentication information managed by **swot-wse** |
| `--earth-engine-only` | Apply the operation only to Google Earth Engine |
| `--earthdata-only` | Apply the operation only to NASA Earthdata |

Some combinations are intentionally invalid:

```text
--force              + --remove
--earth-engine-only  + --earthdata-only
--earthdata-only     + --project-id
```

For the complete CLI syntax, see the [Command Reference](command_reference.md).

---

# Authentication During Extraction

The `auth` command is responsible for interactive authentication. Extraction is not.

When:

```bash
swot-wse extract ...
```

is executed, the package attempts to initialize the external service required by the selected processing path using the authentication state already available on the system.

For Google Earth Engine, this means using:

```text
stored Project ID
        +
existing Earth Engine credentials
```

For NASA Earthdata, this means using:

```text
stored netrc credentials
```

If authentication cannot be established, extraction stops and reports the authentication problem rather than launching an interactive login procedure in the middle of processing.

The user can then repair the relevant authentication state explicitly:

```bash
swot-wse auth --earth-engine-only
```

or:

```bash
swot-wse auth --earthdata-only
```

This separation keeps extraction commands predictable and makes **swot-wse** suitable for scripts and other non-interactive workflows.
