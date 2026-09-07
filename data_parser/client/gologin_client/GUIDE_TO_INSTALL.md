# GoLogin Environment Setup

This project uses **GoLogin Agent Browser CLI** to run GoLogin browser profiles locally.

## Requirements

* Windows
* Node.js 20+
* npm
* GoLogin account
* A GoLogin browser profile

Check Node.js and npm:

```powershell
node --version
npm --version
```

## Install GoLogin Agent Browser CLI

Install the CLI globally:

```powershell
npm install -g gologin-agent-browser-cli
```

Verify the installation:

```powershell
gologin-agent-browser doctor
```

## Configure Environment Variables

The project requires two environment variables:

```env
GOLOGIN_TOKEN=your_gologin_token
GOLOGIN_PROFILE_ID=your_profile_id
```

For local development, add them to the project's `.env` file.

Example:

```env
GOLOGIN_TOKEN=xxxxxxxxxxxxxxxx
GOLOGIN_PROFILE_ID=xxxxxxxxxxxxxxxx
```

Make sure `.env` is included in `.gitignore`:

```gitignore
../../../.env
```

### PowerShell

You can also set the variables temporarily in the current PowerShell session:

```powershell
$env:GOLOGIN_TOKEN="YOUR_TOKEN"
$env:GOLOGIN_PROFILE_ID="YOUR_PROFILE_ID"
```

These variables will be removed when the PowerShell session is closed.

## Verify GoLogin Token

Check that the configured token is valid:

```powershell
gologin-agent-browser api GET /user
```

If the command returns your GoLogin account information, the token is configured correctly.

If you receive:

```text
401 Unauthorized
```

check your `GOLOGIN_TOKEN`.

## Verify Local Agent

Run:

```powershell
gologin-agent-browser local doctor --json
```

A correctly configured environment should report:

```json
{
  "ok": true,
  "tokenConfigured": true,
  "reachable": true
}
```

* `tokenConfigured: true` — the GoLogin token is configured.
* `reachable: true` — the local GoLogin Agent is running and accessible.

## Test Browser Profile

Replace `YOUR_PROFILE_ID` with the ID of your GoLogin profile:

```powershell
gologin-agent-browser local open "https://example.com" --profile "YOUR_PROFILE_ID"
```

If the browser opens `example.com`, the GoLogin environment is ready.

You can also test the target website:

```powershell
gologin-agent-browser local open "https://en.bidfax.info/" --profile "YOUR_PROFILE_ID"
```

## Troubleshooting

### `401 Unauthorized`

First check the token:

```powershell
gologin-agent-browser api GET /user
```

If this command also returns `401`, the token is invalid or not configured.

### `tokenConfigured: true` but `reachable: false`

The token is configured, but the local Agent is not currently running.

Run:

```powershell
gologin-agent-browser local doctor --json
```

and check the result again.

### Browser does not open

First test with a simple website:

```powershell
gologin-agent-browser local open "https://example.com" --profile "YOUR_PROFILE_ID"
```

If `example.com` works, but the target website does not, the problem is likely related to the target website rather than the GoLogin environment.

## Clean Reinstall

If the CLI installation is broken, remove it:

```powershell
npm uninstall -g gologin-agent-browser-cli
```

Remove local GoLogin state:

```powershell
Remove-Item "$env:USERPROFILE\.gologin" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:USERPROFILE\.gologin-local-agent-browser" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:USERPROFILE\.gologin-agent-browser" -Recurse -Force -ErrorAction SilentlyContinue
```

Then reinstall:

```powershell
npm install -g gologin-agent-browser-cli
```

Configure the environment variables again and repeat the verification steps above.
