---
name: init
description: >
  Set up (or update) the local, per-machine configuration the `plex` skill needs to talk to
  a Plex Media Server. Run this once before first using `/plex`, or again to change the server,
  token, or library mapping. It interviews the user for connection details, discovers their
  libraries live via the Plex API, and writes everything to ~/.claude/plex/config.json —
  a file that lives OUTSIDE the plugin repo so no personal server details are ever committed.
  Also trigger on: "/plex:init", "plex init", "set up plex", "configure plex", "plex config",
  "connect plex", "plex token", "my plex isn't configured", "no plex config".
---

You are configuring the local Plex connection for the `plex` plugin. The goal is to produce
a valid `~/.claude/plex/config.json`. **Nothing you collect here is ever written into the
plugin repo** — it all goes to the user's home directory.

## Config file

Target path: **`~/.claude/plex/config.json`** (create the `~/.claude/plex/` directory if needed).

Schema (write exactly this shape):

```json
{
  "server": "http://localhost:32400",
  "token":  "<X-Plex-Token>",
  "machineId": "<machineIdentifier>",
  "quarantine": "D:\\Plex\\_Quarantine",
  "libraries": {
    "movies":     { "key": 1, "path": "D:\\Plex\\Movies" },
    "homemovies": { "key": 7, "path": "D:\\Plex\\Home Movies" },
    "tv":         { "key": 3, "path": "D:\\Plex\\TV Shows" },
    "music":      { "key": 8, "path": "D:\\Plex\\Music" }
  },
  "horror": {
    "genreKey": 123,
    "familyFriendlyCollectionKey": 456,
    "notHorrorLabel": "not-horror",
    "trueHorrorCollectionKey": 789
  }
}
```

Only `server`, `token`, and at least one `libraries` entry are required. `machineId`,
`quarantine`, and `horror` are optional (the `plex` skill fetches `machineId` live if absent,
and skips horror curation entirely when there's no `horror` block).

## Steps

### 1. If a config already exists
Read `~/.claude/plex/config.json`. If present, show a redacted summary (server, library names,
token masked to its last 4 chars) and ask whether to **update** it or start fresh. Preserve any
fields the user doesn't change.

### 2. Server URL
Ask for the base URL. Default `http://localhost:32400`. Accept `http(s)://host:port`; strip any
trailing slash.

### 3. Token
Ask for the `X-Plex-Token`. Tell the user how to get one if they don't have it handy:
- Open any item in the Plex **web app**, click **⋯ → Get Info → View XML**, and copy the
  `X-Plex-Token=...` value from the resulting URL, **or**
- Grab it from the URL of almost any authenticated Plex web request (`&X-Plex-Token=...`).

Never echo the full token back in plaintext after this — mask it.

### 4. Verify + discover libraries
With the server + token, confirm connectivity and discover everything (do not ask the user to
type section keys by hand):

```powershell
$base = "<server>".TrimEnd('/')
$h = @{ 'X-Plex-Token' = '<token>'; 'Accept' = 'application/json' }
# machineIdentifier
(Invoke-RestMethod -Uri "$base/" -Headers $h).MediaContainer.machineIdentifier
# libraries: key, title, type, and on-disk path(s)
(Invoke-RestMethod -Uri "$base/library/sections" -Headers $h).MediaContainer.Directory |
    Select-Object key, title, type, @{n='path';e={ $_.Location.path -join '; ' }}
```

If the call fails, report the error (bad token, unreachable host, https cert) and stop — don't
write a broken config.

### 5. Map the four logical targets
The `plex` skill and `plex-add.ps1` use four logical names: `movies`, `homemovies`, `tv`, `music`.
Map each to a discovered section. Auto-propose a mapping from the discovered list (match `type`:
`movie` → movies/homemovies, `show` → tv, `artist` → music; if two `movie` libraries exist, the
one whose title contains "home" is `homemovies`). Show the proposal and let the user correct it.
Use each section's reported `Location.path` as its `path`. It's fine to omit a target the user
doesn't have.

### 6. Quarantine folder (optional)
Where the junk sweep moves suspected-junk files. Must be **outside** every library path so Plex
won't scan it. Propose `<parent of the library root>\_Quarantine` and let the user override.

### 7. Horror auto-curation (optional — ask, default no)
Only set a `horror` block if the user wants the `/plex add movies` horror curation (auto-exclude
kid/family films from a "True Horror"-style smart collection). If yes, discover the ids against
the movies section:

```powershell
$mk = <moviesKey>
# Horror genre id
((Invoke-RestMethod -Uri "$base/library/sections/$mk/genre" -Headers $h).MediaContainer.Directory |
    Where-Object { $_.title -eq 'Horror' }).key
# A Family-Friendly-style collection's ratingKey (pick from the list)
(Invoke-RestMethod -Uri "$base/library/sections/$mk/collections" -Headers $h).MediaContainer.Metadata |
    Select-Object ratingKey, title
```

Set `notHorrorLabel` to the label the user wants applied to excluded films (default `not-horror`).
`trueHorrorCollectionKey` is informational (the smart collection the exclusion feeds); include it
if they have one. If the user doesn't want this feature, **omit the whole `horror` block**.

### 8. Write the file
Create `~/.claude/plex/` and write `config.json` as UTF-8. Example writer:

```powershell
$dir = Join-Path $HOME '.claude\plex'
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$config = [ordered]@{
  server     = $server
  token      = $token
  machineId  = $machineId
  quarantine = $quarantine
  libraries  = $libraries   # hashtable of name -> @{ key = N; path = '...' }
  # horror   = @{ ... }     # only if configured
}
$config | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $dir 'config.json') -Encoding UTF8
```

### 9. Confirm
Read the file back, validate it parses, and print a redacted summary (token masked). Tell the user
they can now run `/plex` (and `/plex add`). If they changed libraries, note that the horror state
file `~/.claude/plex/plex-horror-seen.json` (if any) may need re-seeding.

## Notes
- This config is intentionally per-machine and git-ignored by living in `~/.claude/` — the plugin
  in the repo ships only placeholders.
- A `/plugin update` never touches `~/.claude/plex/`, so config and state survive plugin upgrades.
