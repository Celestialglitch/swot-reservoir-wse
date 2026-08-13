# Authentication

**swot-wse** uses two external services that require authentication:

- **Google Earth Engine** for reservoir footprint generation using the JRC Global Surface Water dataset.
- **NASA Earthdata** for discovering and accessing SWOT observation products.

Authentication for both services is managed through the `swot-wse auth` command.

---

# Authenticate Both Services

Run:

```bash
swot-wse auth
```

The package checks authentication for Google Earth Engine and NASA Earthdata.

Existing credentials are reused when they are available and valid. If valid credentials cannot be reused, the corresponding authentication procedure is started.

---

# Google Earth Engine

Google Earth Engine authentication requires both:

1. valid Google Earth Engine credentials; and
2. a Google Cloud Project ID with access to Earth Engine.

The Project ID used by **swot-wse** is stored in the package runtime configuration.

## Standard Authentication

To manage only Google Earth Engine authentication, run:

```bash
swot-wse auth --earth-engine-only
```

If an Earth Engine Project ID has not already been configured, the package prompts for one:

```text
Google Earth Engine project ID:
```

If valid Earth Engine credentials are already available, they are reused.

Otherwise, the Google Earth Engine authentication flow is started. After successful authentication, the selected Project ID is saved in `config.json` and reused during future executions from the same working directory.

A Project ID can also be supplied directly:

```bash
swot-wse auth --earth-engine-only --project-id my-earth-engine-project
```

---

## Force Earth Engine Reauthentication

To explicitly start a new Google Earth Engine authentication flow, run:

```bash
swot-wse auth --earth-engine-only --force
```

A Project ID may also be supplied:

```bash
swot-wse auth --earth-engine-only --force --project-id another-earth-engine-project
```

This can be used when changing the authenticated Google account or switching to another Earth Engine project.

After successful initialization, the selected Project ID is stored in the active `config.json`.

---

## Remove the Stored Earth Engine Project

Run:

```bash
swot-wse auth --earth-engine-only --remove
```

This sets the Earth Engine Project ID stored by **swot-wse** to `null`.

The command does **not** delete Google-managed OAuth credentials. Those credentials are managed by the Google Earth Engine authentication system rather than by **swot-wse**.

Consequently, running the authentication command again may still reuse existing Google credentials if they remain valid.

---

# NASA Earthdata

NASA Earthdata credentials are stored in the standard user-level netrc credential file.

**swot-wse** uses the Earthdata Login machine entry:

```text
urs.earthdata.nasa.gov
```

## Standard Authentication

To manage only NASA Earthdata authentication, run:

```bash
swot-wse auth --earthdata-only
```

If stored Earthdata credentials are found, the package first attempts to validate and reuse them.

If valid credentials are unavailable, the package prompts for an Earthdata Login username and password:

```text
Earthdata Login username:
Earthdata password:
```

The password is entered through a non-echoing password prompt and is not displayed in the terminal.

The supplied credentials are validated before being written to the netrc file.

After storage, the package verifies that the saved credentials can be reused successfully.

---

## Earthdata Credential Location

On Windows, the credentials are stored in:

```text
%USERPROFILE%\_netrc
```

On Linux and macOS, they are stored in:

```text
~/.netrc
```

On POSIX systems, **swot-wse** restricts the credential file permissions to:

```text
0600
```

This limits access to the current user.

---

## Force Earthdata Reauthentication

To remove the existing Earthdata entry and authenticate again, run:

```bash
swot-wse auth --earthdata-only --force
```

The existing `urs.earthdata.nasa.gov` entry is removed before new credentials are requested.

The new credentials are validated and, if authentication succeeds, stored in the user's netrc file.

This is useful when changing Earthdata accounts or replacing credentials that are no longer valid.

---

## Remove Earthdata Credentials

Run:

```bash
swot-wse auth --earthdata-only --remove
```

This removes the `urs.earthdata.nasa.gov` credential entry from the user's netrc file.

Other machine entries in the same file are preserved.

If no Earthdata credentials are present, the package reports that no stored credentials were found.

> **Security**
>
> Netrc files contain credentials in plain text. Do not use persistent Earthdata credential storage on shared or untrusted systems.

---

# Reauthenticate Both Services

To force reauthentication for both services, run:

```bash
swot-wse auth --force
```

For Google Earth Engine, this explicitly starts a new Earth Engine authentication flow.

For NASA Earthdata, the existing Earthdata netrc entry is removed and the package requests new credentials.

If an Earth Engine Project ID is already stored in `config.json`, it is reused unless another Project ID is supplied.

A different Earth Engine Project ID can therefore be selected while reauthenticating both services:

```bash
swot-wse auth --force --project-id another-earth-engine-project
```

---

# Remove Stored Authentication Information

To remove authentication information managed directly by **swot-wse** for both services, run:

```bash
swot-wse auth --remove
```

This performs two operations:

- sets the Google Earth Engine Project ID in `config.json` to `null`;
- removes the `urs.earthdata.nasa.gov` credentials from the user's netrc file.

Google Earth Engine OAuth credentials managed by Google's authentication system are **not** deleted.

---

# Authentication Options

| Option | Description |
| --- | --- |
| `--project-id <project-id>` | Supplies the Google Earth Engine Project ID directly. |
| `--force` | Forces reauthentication instead of reusing existing credentials. |
| `--remove` | Removes authentication information managed directly by **swot-wse**. |
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

If the required authentication is unavailable or invalid, processing stops with an error directing the user to run the appropriate `swot-wse auth` command.

This avoids unexpectedly starting an interactive authentication flow in the middle of an extraction run.

---

# Credential Storage Summary

| Information | Storage Location | Managed by `swot-wse auth --remove` |
| --- | --- | --- |
| Earth Engine Project ID | Working-directory `config.json` | Yes |
| Earth Engine OAuth credentials | Google/Earth Engine authentication system | No |
| Earthdata username and password | User netrc file | Yes |

The Earth Engine Project ID is configuration information rather than a password or authentication token. Nevertheless, `config.json` is runtime-specific and should not be committed to the repository.

For the complete command-line interface, see the [Command Reference](command_reference.md).