# Authentication

**swot-reservoir-wse** uses two authenticated external services:

- **Google Earth Engine** to access the JRC Global Surface Water dataset used during reservoir footprint generation.
- **NASA Earthdata** to discover and access SWOT observation products.

Authentication for both services can be configured through:

```bash
swot-reservoir-wse auth
```

The package keeps authentication setup separate from normal extraction. Once the required credentials have been configured, subsequent processing runs reuse them without starting an interactive login unless reauthentication is explicitly requested.

---

## Before Authentication

Before running the authentication command, the corresponding accounts must already exist.

For Google Earth Engine, you need:

- a Google account with access to Google Earth Engine;
- a Google Cloud project configured for Earth Engine use; and
- the **Project ID** of that Google Cloud project.

For NASA Earthdata, you need:

- an active NASA Earthdata Login account.

Account creation and external-service setup are covered in [Installation](installation.md).

---

## Authenticate Both Services

For a normal first-time setup, run:

```bash
swot-reservoir-wse auth
```

The package checks Google Earth Engine and NASA Earthdata in sequence.

If an existing authentication state is valid, it is reused. If the required authentication information is missing or cannot be reused, the package starts the corresponding setup procedure.

In most cases, this is the only authentication command required before the first extraction.

---

## Google Earth Engine

Google Earth Engine requires two separate pieces of information:

1. Google-managed authentication credentials; and
2. a Google Cloud Project ID through which Earth Engine is initialized.

These serve different purposes and are stored separately.

The OAuth authentication state is managed by the Google Earth Engine authentication system. The Project ID selected for **swot-reservoir-wse** is stored in the active "config.json".

---

### Authenticate Earth Engine Only

To configure only Google Earth Engine, run:

```bash
swot-reservoir-wse auth --earth-engine-only
```

If an Earth Engine Project ID is not already present in the active configuration, the package prompts for one:

```text
Google Earth Engine project ID:
```

The value must be the Google Cloud **Project ID**, not the project display name or project number.

If valid Google Earth Engine credentials are already available, the package attempts to reuse them. Otherwise, the standard Earth Engine authentication flow is started.

After Earth Engine has been initialized successfully, the Project ID is stored in the current working directory's "config.json" and reused by later runs from that working directory.

---

### Supply the Project ID Directly

The Project ID can be supplied directly instead of entering it interactively:

```bash
swot-reservoir-wse auth --earth-engine-only --project-id my-earth-engine-project
```

For example, if the Google Cloud Project ID is:

```text
swot-processing-123456
```

the command would be:

```bash
swot-reservoir-wse auth --earth-engine-only --project-id swot-processing-123456
```

After successful initialization, the selected Project ID becomes the active Earth Engine project for that working directory.

---

### Force Earth Engine Reauthentication

To explicitly start a new Earth Engine authentication flow:

```bash
swot-reservoir-wse auth --earth-engine-only --force
```

A Project ID can also be supplied at the same time:

```bash
swot-reservoir-wse auth --earth-engine-only --force --project-id another-earth-engine-project
```

This is useful when:

- changing the Google account used for Earth Engine,
- switching to another Google Cloud project,
- replacing an authentication state that is no longer valid, or
- deliberately requesting a fresh Earth Engine login.

After successful initialization, the selected Project ID is stored in the active "config.json".

---

### Remove the Stored Earth Engine Project

To remove the Earth Engine Project ID stored by **swot-reservoir-wse**:

```bash
swot-reservoir-wse auth --earth-engine-only --remove
```

This resets the configured Project ID to:

```text
null
```

It does **not** delete Google-managed OAuth credentials.

The distinction is important:

```text
Earth Engine Project ID
        │
        └── stored by swot-reservoir-wse in config.json

Google OAuth credentials
        │
        └── managed by the Google/Earth Engine authentication system
```

Because the Google credentials are not deleted, a later authentication command may still be able to reuse them.

---

## NASA Earthdata

NASA Earthdata authentication is used when searching for and accessing SWOT products.

**swot-reservoir-wse** stores Earthdata Login credentials using the standard user-level netrc credential file.

The Earthdata Login machine entry is:

```text
urs.earthdata.nasa.gov
```

---

### Authenticate Earthdata Only

To configure only NASA Earthdata authentication:

```bash
swot-reservoir-wse auth --earthdata-only
```

If an Earthdata credential entry already exists, the package first attempts to validate and reuse it.

If usable credentials are not available, the package prompts for:

```text
Earthdata Login username:
Earthdata password:
```

The password is entered through a non-echoing prompt and is therefore not displayed in the terminal while it is being typed.

The supplied credentials are validated before being stored.

After storage, the package verifies that the saved credentials can subsequently be reused.

---

### Earthdata Credential Location

On Windows, the netrc file is:

```text
%USERPROFILE%\_netrc
```

A typical location therefore resembles:

```text
C:\Users\<username>\_netrc
```

On Linux and macOS, the file is:

```text
~/.netrc
```

The Earthdata entry is associated with:

```text
urs.earthdata.nasa.gov
```


> **Security**
>
> Netrc files store credentials as plain text. Persistent credential storage should therefore not be used on shared, public, or otherwise untrusted systems.

---

### Force Earthdata Reauthentication

To discard the currently stored Earthdata entry and authenticate again:

```bash
swot-reservoir-wse auth --earthdata-only --force
```

The existing:

```text
urs.earthdata.nasa.gov
```

entry is removed before new credentials are requested.

The replacement credentials are validated before being stored in the user's netrc file.

This is useful when changing Earthdata accounts or replacing credentials that are no longer valid.

---

### Remove Earthdata Credentials

To remove the Earthdata credentials managed by the package:

```bash
swot-reservoir-wse auth --earthdata-only --remove
```

This removes the:

```text
urs.earthdata.nasa.gov
```

entry from the user's netrc file.

Other machine entries in the same netrc file are preserved.

If no corresponding Earthdata credentials are present, the package reports that no stored credentials were found.

---

## Force Reauthentication for Both Services

To explicitly reauthenticate both Google Earth Engine and NASA Earthdata:

```bash
swot-reservoir-wse auth --force
```

For Google Earth Engine, this starts a new Earth Engine authentication flow.

For NASA Earthdata, the existing Earthdata netrc entry is removed before new credentials are requested.

If an Earth Engine Project ID is already stored in the active "config.json", that Project ID is reused unless another one is supplied.

To select another project while reauthenticating:

```bash
swot-reservoir-wse auth --force --project-id another-earth-engine-project
```

---

## Remove Authentication Information

To remove the authentication information managed directly by **swot-reservoir-wse** for both services:

```bash
swot-reservoir-wse auth --remove
```

This performs two operations:

1. the Earth Engine Project ID in the active "config.json" is reset to "null";
2. the "urs.earthdata.nasa.gov" entry is removed from the user's netrc file.

Google-managed Earth Engine OAuth credentials are not deleted.

The resulting state is therefore:

| Authentication component | Removed |
| --- | :---: |
| Earth Engine Project ID in config.json | Yes |
| Google-managed Earth Engine OAuth credentials | No |
| Earthdata credentials in the user's netrc file | Yes |

---

## Authentication Options

The "auth" command supports the following options:

| Option | Purpose |
| --- | --- |
| --project-id <project-id> | Supply the Google Cloud Project ID used for Earth Engine. |
| --force | Reauthenticate instead of attempting to reuse the current authentication state. |
| --remove | Remove authentication information managed directly by **swot-reservoir-wse**. |
| --earth-engine-only | Apply the requested operation only to Google Earth Engine. |
| --earthdata-only | Apply the requested operation only to NASA Earthdata. |

Some options cannot be combined.

The following combinations are invalid:

```text
--force + --remove
--earth-engine-only + --earthdata-only
--earthdata-only + --project-id
```

For the complete CLI syntax, see the [Command Reference](command_reference.md).

---

## Authentication During Extraction

Interactive authentication and data processing are intentionally separated.

When an extraction is started with a command such as:

```bash
swot-reservoir-wse extract --lat 19.690 --lon 73.340 --start-date 2026-01-20 --end-date 2026-07-16 --source lakesp
```

the package expects the required authentication state to already exist.

During processing:

- Google Earth Engine is initialized using the Project ID stored in the active configuration together with the available Earth Engine credentials.
- NASA Earthdata access uses the Earthdata credentials available through the user's netrc file.

If the required authentication state is unavailable or invalid, extraction stops rather than unexpectedly starting an interactive authentication procedure in the middle of the processing workflow.

The user can then configure the affected service explicitly with:

```bash
swot-reservoir-wse auth --earth-engine-only
```

or:

```bash
swot-reservoir-wse auth --earthdata-only
```

---

## Authentication and Working Directories

The Earth Engine Project ID and Earthdata credentials have different scopes.

The Earth Engine Project ID is stored in the active:

```text
config.json
```

which belongs to the directory from which **swot-reservoir-wse** is being used.

For example:

```text
project-a/
└── config.json

project-b/
└── config.json
```

These two working directories can therefore use different Earth Engine Project IDs.

Earthdata credentials, by contrast, are stored in the user's netrc file and are therefore user-level rather than working-directory-specific.

This means that creating a new **swot-reservoir-wse** working directory may require an Earth Engine Project ID to be configured for that directory, while valid Earthdata credentials can normally be reused from the existing user-level netrc file.

---

## Credential Storage Summary

| Information | Storage | Scope | Removed by `swot-reservoir-wse auth --remove` |
| --- | --- | --- | :---: |
| Earth Engine Project ID | config.json | Working directory | Yes |
| Earth Engine OAuth credentials | Google/Earth Engine authentication system | Google authentication environment | No |
| Earthdata username and password | _netrc on Windows or .netrc on Linux/macOS | User account | Yes |

The Earth Engine Project ID is configuration information rather than a password or authentication token.

The runtime config.json may contain environment-specific configuration and should not be committed to the repository.

---

## Common Authentication Commands

For normal first-time setup:

```bash
swot-reservoir-wse auth
```

Authenticate only Google Earth Engine:

```bash
swot-reservoir-wse auth --earth-engine-only
```

Authenticate only NASA Earthdata:

```bash
swot-reservoir-wse auth --earthdata-only
```

Force both services to authenticate again:

```bash
swot-reservoir-wse auth --force
```

Remove authentication information managed by the package:

```bash
swot-reservoir-wse auth --remove
```

For initial account and service setup, see [Installation](installation.md).

For all command-line options, see the [Command Reference](command_reference.md).
