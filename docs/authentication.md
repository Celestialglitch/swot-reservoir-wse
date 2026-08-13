# Authentication

**swot-wse** accesses two external services during processing:

- **Google Earth Engine (GEE)** — used to derive reservoir footprints from the JRC Global Surface Water dataset.
- **NASA Earthdata** — used to discover and retrieve SWOT observation products.

Authentication for both services is configured through:

```bash
swot-wse auth
```

Authentication is normally required only during initial setup or when credentials or accounts need to be changed.

---

## Before You Begin

You will need:

1. a Google account with access to Google Earth Engine;
2. a Google Cloud project configured for Earth Engine; and
3. a NASA Earthdata Login account.

Account creation and Earth Engine project setup are covered in [Installation](installation.md).

Once those accounts are available, **swot-wse** can configure access from the command line.

---

## Authenticate

To configure both Google Earth Engine and NASA Earthdata, run:

```bash
swot-wse auth
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

Google Earth Engine requires two separate pieces of information:

- Google-managed Earth Engine authentication credentials;
- a Google Cloud **Project ID** authorized for Earth Engine use.

These should not be confused with each other.

The authentication credentials establish which Google account is being used. The Project ID identifies the Google Cloud project through which Earth Engine requests are made.

**swot-wse** stores the selected Project ID in its working-directory configuration. Google manages the authentication credentials themselves.

---

## Configure Earth Engine

Run:

```bash
swot-wse auth --earth-engine-only
```

If no Earth Engine Project ID is configured, you will be prompted for one:

```text
Google Earth Engine project ID:
```

Enter the **Project ID**, not the project name or project number.

You can provide it directly instead:

```bash
swot-wse auth --earth-engine-only --project-id my-project-id
```

The package first attempts to initialize Earth Engine using the available Google credentials. If authentication is required, the standard Earth Engine authentication flow is started.

After successful initialization, the Project ID is saved in the active `config.json` and reused for subsequent runs from that working directory.

---

## Change Account or Project

To explicitly run the Earth Engine authentication flow again:

```bash
swot-wse auth --earth-engine-only --force
```

This is useful when changing the Google account used for Earth Engine.

A different project can be selected at the same time:

```bash
swot-wse auth --earth-engine-only --force --project-id another-project-id
```

The successfully initialized Project ID becomes the Earth Engine project stored in the active configuration.

---

## Remove the Configured Project

To remove the Earth Engine Project ID stored by **swot-wse**:

```bash
swot-wse auth --earth-engine-only --remove
```

This clears the Project ID from the active `config.json`.

It does **not** delete Google-managed OAuth credentials.

As a result, authenticating again may still reuse the previously authenticated Google account. The `--remove` operation only removes authentication information that **swot-wse** manages itself.

---

# NASA Earthdata

Access to SWOT products requires a NASA Earthdata Login account.

**swot-wse** uses the standard netrc mechanism supported by Earthdata tooling and stores credentials under the machine entry:

```text
urs.earthdata.nasa.gov
```

---

## Configure Earthdata

Run:

```bash
swot-wse auth --earthdata-only
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

On POSIX systems, **swot-wse** sets the credential file permissions to:

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
swot-wse auth --earthdata-only --force
```

The existing `urs.earthdata.nasa.gov` entry is removed before new credentials are requested.

The replacement credentials are validated before being written to the netrc file.

Use this when changing Earthdata accounts or replacing invalid credentials.

---

## Remove Earthdata Credentials

To remove the Earthdata credentials stored by **swot-wse**:

```bash
swot-wse auth --earthdata-only --remove
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
swot-wse auth --force
```

For Earth Engine, this starts a new Earth Engine authentication flow.

For Earthdata, the existing Earthdata netrc entry is removed and replacement credentials are requested.

If an Earth Engine Project ID is already configured, it continues to be used unless another one is supplied:

```bash
swot-wse auth --force --project-id another-project-id
```

---

# Removing Authentication Information

To remove authentication information managed directly by **swot-wse**:

```bash
swot-wse auth --remove
```

This:

- removes the Earth Engine Project ID from the active `config.json`;
- removes the `urs.earthdata.nasa.gov` entry from the user's netrc file.

It does **not** remove Google-managed Earth Engine OAuth credentials.

This distinction is important because the three pieces of authentication state are stored and managed differently:

| Information | Stored in | Removed by `swot-wse auth --remove` |
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
