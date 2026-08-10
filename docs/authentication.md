# Authentication

**swot-reservoir-wse** uses two external services that require authentication:

- Google Earth Engine for reservoir footprint generation.
- NASA Earthdata for discovering and downloading SWOT observation products.

Both services can be managed through the `swot-wse auth` command.

---

## Authenticate Both Services

Run:

```bash
swot-wse auth
```

The package checks both Google Earth Engine and NASA Earthdata authentication.

Existing credentials are reused whenever possible. If valid credentials are not available, the corresponding authentication flow is started.

---

## Google Earth Engine

### Standard Authentication

To manage only Google Earth Engine authentication, run:

```bash
swot-wse auth --earth-engine-only
```

If a Google Earth Engine Project ID has not already been configured, the package prompts for one:

```text
Google Earth Engine project ID:
```

If valid Google Earth Engine credentials are already available, they are reused. Otherwise, the Google Earth Engine authentication flow is started.

A Project ID can also be supplied directly:

```bash
swot-wse auth --earth-engine-only --project-id my-earth-engine-project
```

The selected Project ID is stored in the package configuration and reused during future executions.

---

### Reauthenticate Google Earth Engine

To force a new Google Earth Engine authentication flow, run:

```bash
swot-wse auth --earth-engine-only --force
```

A different Project ID can also be supplied during reauthentication:

```bash
swot-wse auth --earth-engine-only --force --project-id another-earth-engine-project
```

This is useful when changing the Google account, replacing invalid credentials, or switching to another Earth Engine project.

---

### Remove the Stored Earth Engine Project

Run:

```bash
swot-wse auth --earth-engine-only --remove
```

This removes the Google Earth Engine Project ID stored by **swot-reservoir-wse**.

Google-managed OAuth credentials are not deleted by this command.

---

## NASA Earthdata

### Standard Authentication

To manage only NASA Earthdata authentication, run:

```bash
swot-wse auth --earthdata-only
```

If valid Earthdata credentials are already stored, they are reused automatically.

Otherwise, the package prompts for the Earthdata Login username and password:

```text
Earthdata Login username:
Earthdata password:
```

After successful authentication, the credentials are stored in the standard user-level netrc credential file.

On Windows:

```text
%USERPROFILE%\_netrc
```

On Linux and macOS:

```text
~/.netrc
```

---

### Reauthenticate NASA Earthdata

To remove the currently stored Earthdata credentials and authenticate again, run:

```bash
swot-wse auth --earthdata-only --force
```

The package will request a new Earthdata Login username and password.

This command can be used when changing the Earthdata account or replacing invalid credentials.

---

### Remove NASA Earthdata Credentials

Run:

```bash
swot-wse auth --earthdata-only --remove
```

This removes only the NASA Earthdata Login credentials managed by the package.

Other credential entries stored in the same netrc file are preserved.

> **Security Note**
>
> Netrc files store credentials locally. Avoid storing Earthdata credentials on shared or untrusted systems.

---

## Reauthenticate Both Services

To force reauthentication for both Google Earth Engine and NASA Earthdata, run:

```bash
swot-wse auth --force
```

The package starts a new Google Earth Engine authentication flow and requests fresh NASA Earthdata credentials.

---

## Remove Stored Authentication Information

To remove the authentication information managed by the package for both services, run:

```bash
swot-wse auth --remove
```

This removes:

- the Google Earth Engine Project ID stored in the package configuration;
- the NASA Earthdata Login credentials stored in the user's netrc file.

Google Earth Engine OAuth credentials managed by Google's authentication system are not removed.

---

## Authentication Options

| Option                      | Description                                                       |
| --------------------------- | ----------------------------------------------------------------- |
| `--project-id <project-id>` | Supplies the Google Earth Engine Project ID directly.             |
| `--force`                   | Forces reauthentication instead of reusing existing credentials.  |
| `--remove`                  | Removes stored authentication information managed by the package. |
| `--earth-engine-only`       | Applies the authentication command only to Google Earth Engine.   |
| `--earthdata-only`          | Applies the authentication command only to NASA Earthdata.        |

For the complete command-line reference, see the [Command Reference](command_reference.md).
