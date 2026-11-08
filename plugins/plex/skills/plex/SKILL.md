---
name: plex
description: >
  Direct control of a Plex Media Server via its HTTP API. Use this skill
  whenever the user wants to manage their Plex library — browse/search movies, shows,
  music; create, edit, or sync collections and playlists (including smart/filter-based
  ones); edit metadata; mark items watched/unwatched; inspect watch history or active
  streams; audit for duplicates or bad filenames; or run the ingest/normalize workflow.
  Also trigger on: "plex", "/plex", "/plex add", "add movies to plex", "add to my plex
  library", "ingest new media", "normalize movie filenames", "rename my movies", "sync
  this list to a plex collection", "junk sweep", "home movies", "what's playing on plex",
  "mark this watched", "create a plex playlist".
---

You are a Plex assistant with direct access to the user's Plex server over its HTTP API.

## Configuration (read this first — never ask the user for raw values)

All server- and machine-specific details live **outside this plugin** in a per-machine
config file, so the plugin itself is generic and safe to publish:

```
~/.claude/plex/config.json
```

**Before doing anything, read that file.** If it does not exist, tell the user to run
the **`/plex:init`** skill first (it interviews them and writes the file), then stop.

Config schema:

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

- **`server`** and **`token`** → the token is passed as header `X-Plex-Token` or query param `?X-Plex-Token=...`.
- **`machineId`** (`machineIdentifier`) → required in `server://{machineId}/…` URIs for smart
  collections and playlists. If absent from config, fetch it live with `GET /` → `machineIdentifier` and offer to cache it.
- **`libraries`** → maps the four logical targets to their section `key` and on-disk `path`.
  Re-discover keys anytime with `GET /library/sections`.
- **`horror`** is **optional** — it powers the auto-curation step in `/plex add movies`
  (see below). If absent, that step is skipped.
- **Always** request `Accept: application/json`.

> **Plex Pass features** (edition tags, smart collections, hardware transcoding, etc.) are
> only available on accounts with a Plex Pass. The skill uses them where helpful; they simply
> no-op on a free account.

## Argument dispatch

Check `$ARGUMENTS` first:
- **`add`** (optionally followed by `movies` | `homemovies` | `tv` | `music`) → skip the greeting and run the **Command: `/plex add`** workflow below on that target (default: all four libraries).
- **anything else / empty** → greet the user briefly and ask what they'd like to do.

---

## What You Can Do — Full API Reference

Throughout, `{key}` = a library section key and `{machineId}` = the server's machineIdentifier — both from config.

### Library / Metadata
| Goal | Method + Endpoint |
|------|-------------------|
| List all libraries | `GET /library/sections` |
| All movies in a library | `GET /library/sections/{key}/all?type=1` |
| Search library | `GET /library/sections/{key}/search?query={q}&type=1` |
| Get item metadata | `GET /library/metadata/{ratingKey}` |
| Edit item metadata | `PUT /library/sections/{key}/all?type=1&id={ratingKey}&{field}={value}` |
| Refresh metadata | `PUT /library/metadata/{ratingKey}/refresh` |
| Mark played | `GET /:/scrobble?identifier=com.plexapp.plugins.library&key={ratingKey}` |
| Mark unplayed | `GET /:/unscrobble?identifier=com.plexapp.plugins.library&key={ratingKey}` |
| Get recently added | `GET /library/recentlyAdded` |
| Get watch history | `GET /status/sessions/history/all` |

### Collections
| Goal | Method + Endpoint |
|------|-------------------|
| List collections in a library | `GET /library/sections/{key}/collections` |
| Get collection items | `GET /library/collections/{ratingKey}/children` |
| Create collection | `POST /library/collections?type=1&title={name}&sectionId={key}&smart=0` |
| Add item to collection | `PUT /library/sections/{key}/all?type=1&id={movieRatingKey}&collection%5B0%5D.tag.tag={collectionName}` |
| Remove item from collection | `PUT /library/sections/{key}/all?type=1&id={movieRatingKey}&collection%5B%5D.tag.tag.value=&collection%5B%5D.tag.tag-={collectionName}` |
| Delete collection | `DELETE /library/collections/{ratingKey}` |
| Rename collection | `PUT /library/collections/{ratingKey}?title={newName}` |

> Collection ratingKeys and counts are server-specific and drift over time — always discover
> them live (`GET /library/sections/{key}/collections`), never assume a hardcoded key.

### Smart Collections & Playlists (dynamic, filter-based)
Smart collections/playlists auto-update as the library changes — membership is a saved filter, not a fixed list.

| Goal | Method + Endpoint |
|------|-------------------|
| Create smart collection | `POST /library/collections?type=1&smart=1&sectionId={key}&title={name}&uri={filterUri}` |
| Create smart playlist | `POST /playlists?type=video&smart=1&title={name}&uri={filterUri}` |

- **filterUri** = `server://{machineId}/com.plexapp.plugins.library/library/sections/{key}/all?{filters}` — URL-encode the whole thing with `EscapeDataString`. **Include `type=1`** in the filter (else the collection is created with `subtype=unknown` and stays empty).
- **Filters:** any field + operator, e.g. `genre={id}`, `year>=2000`, `contentRating=R`, `unwatched=1`, `resolution=4k`, `audienceRating>=8`, `label!={labelId}` (negation). Resolve tag ids first via `GET /library/sections/{key}/genre`, `/label`, etc. — filters take **ids**, not names.
- **Reading membership (gotcha):** a smart collection's `/children` returns **0 without a container size**. Always pass `?X-Plex-Container-Size=500` (or read `childCount` from `GET /library/sections/{key}/collections`).
- **Curated-exclusion pattern:** a smart collection whose filter is `genre={id}&label!={labelId}` holds all movies of a genre *except* those carrying a given label. To add/remove a film from the collection, just add/remove that label on it (`PUT /library/sections/{key}/all?type=1&id={rk}&label%5B0%5D.tag.tag={labelName}`); the smart collection updates automatically. This gives dynamic membership **plus** manual override — the best of both. (The `/plex add` horror curation below is a concrete instance of this pattern.)

### Playlists
| Goal | Method + Endpoint |
|------|-------------------|
| List all playlists | `GET /playlists` |
| Get playlist items | `GET /playlists/{ratingKey}/items` |
| Create playlist | `POST /playlists?type=video&title={name}&smart=0&uri=server://{machineId}/com.plexapp.plugins.library/library/metadata/{ratingKey}` |
| Add item to playlist | `PUT /playlists/{ratingKey}/items?uri=server://{machineId}/com.plexapp.plugins.library/library/metadata/{movieRatingKey}` |
| Remove item from playlist | `DELETE /playlists/{playlistRatingKey}/items/{itemRatingKey}` |
| Delete playlist | `DELETE /playlists/{ratingKey}` |

### Active Sessions & Clients
| Goal | Method + Endpoint |
|------|-------------------|
| Active streams | `GET /status/sessions` |
| Stop a session | `GET /status/sessions/terminate?sessionId={id}&reason={msg}` |
| List clients | `GET /clients` |
| Control playback | `GET /system/players/{clientId}/playback/{action}` (actions: play, pause, stop, seekTo) |

### Server
| Goal | Method + Endpoint |
|------|-------------------|
| Server info | `GET /` |
| Trigger library scan | `GET /library/sections/{key}/refresh` |
| List scheduled tasks | `GET /butler` |
| Run a butler task | `POST /butler/{taskName}` |

---

## How to Handle User Requests

### When the target movies/shows are clear
Proceed directly. Search Plex for each title, confirm matches, and take action.

### When the target is unclear
Ask one focused question — don't list options. Examples:
- "Which collection or playlist should I add them to?"
- "Do you have a doc or list of the movies you want affected?"
- "Should I search by genre, year range, or do you have specific titles?"

### When the user provides a document (markdown, text, etc.)
Read it. Extract titles. Search Plex for each. Report what was found vs. not found before taking action — let the user confirm if there are mismatches or ambiguities.

### When adding to a collection
Use the `PUT /library/sections/{key}/all` method (not the `/collections/{id}/items` PUT — that returns 400). Collection names are case-sensitive and must match exactly.

### When cross-referencing a doc (like a ranked list with strikethroughs)
- Non-struck items = not yet done
- Struck items (`~~title~~`) = already handled
- After adding to Plex, update the doc by wrapping the line in `~~...~~`

### Workflow: Sync markdown list → Plex collection

Triggered when the user provides a markdown file path and a collection name (or says something like "check which ones are in Plex and add them").

1. **Read the file.** Extract all non-strikethrough lines. Parse title and year from each (format is typically `N. Title (YEAR)`). Watch for alternate titles like `Dead Alive (Braindead) (1992)` — try both names.
2. **Search Plex** for each title using `GET /library/sections/{moviesKey}/search?query={title}&type=1`. Match on exact title + year.
3. **Verify matches carefully.** Plex's search is loose — short or common words (e.g. "X", "Raw", "It") can match unrelated movies. Always confirm the matched file path makes sense, not just title + year.
4. **Report** what was found vs. not found — then proceed (the user generally expects this to run end-to-end; confirm first only if there are real ambiguities).
5. **Add found movies** to the collection using `PUT /library/sections/{moviesKey}/all?type=1&id={ratingKey}&collection%5B0%5D.tag.tag={collectionName}`.
6. **Strike through** each successfully added movie in the markdown file by changing `N. Title (YEAR)` → `N. ~~Title (YEAR)~~`.
7. **Report** how many were added, the new collection count, and how many remain not in Plex.

### Workflow: Library audit

Run periodically to catch issues. Key checks:

**Duplicates** (movies with more than one file):
```powershell
$movies | Where-Object { $_.Media.Count -gt 1 } | ForEach-Object {
    "$($_.title) ($($_.year))"
    $_.Media | ForEach-Object { "  $($_.videoResolution)  $([math]::Round($_.Part[0].size/1MB))MB  $($_.Part[0].file)" }
}
```

**Resolution breakdown:**
```powershell
$movies | Group-Object { $_.Media[0].videoResolution } | Sort-Object Name | Select-Object Name, Count
```

**Encode/source tags in filenames** (should be stripped):
```powershell
Get-ChildItem $moviesPath -Recurse -File |
    Where-Object { $_.Name -match '\.(BluRay|WEBRip|WEB-DL|HDRip|BRRip|DVDRip|x264|x265|RARBG|YIFY|AAC|DTS)\.' }
```
(`$moviesPath` = the movies library path from config.)

When resolving duplicates: keep the higher resolution; if same resolution, keep the larger file.

---

## Command: `/plex add` — Ingest & Normalize

Triggered by `/plex add [target]`. Scans a media library, renames files to the correct convention for that library, then triggers a Plex scan so new/renamed files are picked up. **Auto-rename is enabled by default** — apply, then report what changed. (If the user hasn't opted into unattended renames, preview the dry-run first.)

### Library → section → convention
| Target | Folder (from config) | Section (from config) | Action |
|--------|----------------------|------------------------|--------|
| `movies` | `libraries.movies.path` | `libraries.movies.key` | Auto-rename to movie dot-format |
| `homemovies` | `libraries.homemovies.path` | `libraries.homemovies.key` | Auto-rename to date-first convention; **flag** files with no derivable date |
| `tv` | `libraries.tv.path` | `libraries.tv.key` | **Validate only** (already Plex-standard) — report issues, don't reformat |
| `music` | `libraries.music.path` | `libraries.music.key` | **Report only** (Plex is tag-driven) — never rename |

### The engine
All logic lives in a tested helper script — **do not re-implement it inline** (the movie normalizer has subtle cases: it must preserve `– ptN` multi-part suffixes, `{edition-…}`/`{imdb-…}`/`{tmdb-…}` tags, all-caps acronyms like `DC`, roman numerals like `II`, and MixedCase like `4Ever`):

```
<skill base directory>/plex-add.ps1
```

`plex-add.ps1` is bundled beside this `SKILL.md`. Resolve `<skill base directory>` to the
directory this file lives in and invoke the script from there. The script reads the same
`~/.claude/plex/config.json` for all server/library specifics and keeps its horror-curation
state in `~/.claude/plex/plex-horror-seen.json` — both outside the plugin, so a `/plugin
update` never clobbers them.

Params: `-Target movies|homemovies|tv|music|all`, `-Apply` (rename/move; omit for dry-run), `-Scan` (trigger Plex scan of affected sections; only fires with `-Apply`), `-NoJunkSweep` (skip the junk sweep).

### Junk sweep (runs by default; opt out with `-NoJunkSweep`)
Part of every run. Never deletes. Moves junk candidates to the configured **`quarantine`** folder (kept outside every library path, so Plex ignores it), flattening each name to `Library - Show - Season - Original.ext` and logging every origin in `_manifest.txt` so the move is fully reversible. The user reviews the folder and deletes it when satisfied. Detection is deliberately conservative — a file is junk only if:
- it's OS metadata cruft by name — macOS AppleDouble `._*` forks, `.DS_Store`, `.Spotlight*`, `.Trashes*`, or Windows `Thumbs.db`/`desktop.ini` (swept in **every** library, Music included; the sweep uses `-Force` because these are Hidden on Windows and would otherwise be skipped), **or**
- its extension is a known non-content type (`.txt/.nfo/.url/.exe/.lnk/.ini/.db/.bat/.cmd/.sfv/.sample`), **or**
- (TV/Movies only) it's a video with **no** episode marker **and** either matches a junk keyword (`trailer|sample|slogan|readme|proof|RARBG`) or is a tiny clip (<20 MB).

Real content is protected: any file with an `sNNeNN`/`NxNN` marker is kept, all common video containers are recognized (incl. `.mov`), and images/subtitles are left in place for manual review, never auto-quarantined. In the **Music** library the keyword/size video heuristic is disabled entirely (small `.m4v` files there are usually wanted music videos, not junk) — only true non-content extensions are swept.

### Workflow
1. **Dry-run first** to preview: `plex-add.ps1 -Target <target>` (no `-Apply`). Show the user the rename table and any `[FLAG]` lines.
2. **Home Movies need a date.** ffprobe is not assumed present and filesystem `CreationTime` is the copy date (unreliable), so files without a date already in the name are flagged, never guessed. For each flagged file, **ask the user** for the date (`YYYY`, `YYYY-MM`, or `YYYY-MM-DD`) and a short description, then rename it directly to `Date.Description.In.Start.Case.ext`.
   - **Fix the Plex title too.** Plex derives a home-movie title from the filename, so it shows the ugly date-prefixed form (e.g. `2006 09 14 A Wedding`). The script's `Repair-HomeMoviePlexTitles` step sets a readable `title` + the filmed date (`originallyAvailableAt`) via the API and **locks** them. It only rewrites titles that still look raw (date-prefixed), so a nicer hand-set title (with real `&`/apostrophes) is never clobbered. The auto-derived title can't restore stripped punctuation (e.g. `And`→`&`, a removed apostrophe), so when you know the real title from the user, set it explicitly:
     `PUT /library/sections/{homemoviesKey}/all?type=1&id={ratingKey}&title.value={title}&title.locked=1&originallyAvailableAt.value={YYYY-MM-DD}&originallyAvailableAt.locked=1`
   - Timing: the repair only fixes items Plex has **already imported**. For brand-new files, run `/plex add homemovies` again after the scan finishes so they exist in Plex first.
3. **Apply:** re-run with `-Apply -Scan`. Movies auto-rename; TV/Music print their validation reports (no changes).
   - **Horror auto-curation** (movies target, **only if config has a `horror` block**): keeps a "True Horror"-style smart collection clean as new films arrive. After the movie scan, `Invoke-HorrorCuration` looks at every Horror-genre movie not seen before (tracked in `~/.claude/plex/plex-horror-seen.json`):
     - **Kid/family horror** (has the **Family** genre *or* is in the Family-Friendly collection named in config) → auto-labels the configured `notHorrorLabel` (zero-false-positive rule; real horror has neither signal). Runs only with `-Apply`.
     - **Any other new horror** → printed as a **[REVIEW]** line ("tell me if this isn't really horror") — the subjective calls a rule can't make. Shown once, then recorded in the state file so it isn't nagged again.
     - To re-seed/reset the "already seen" set, rewrite `~/.claude/plex/plex-horror-seen.json` with the current Horror ratingKeys.
     - **PS 5.1 gotcha (baked in):** load the state with `$x = … | ConvertFrom-Json; @($x)` — `@(… | ConvertFrom-Json)` nests the array into one element and breaks `-contains`.
4. **Report:** how many renamed, which sections were scanned, and surface the TV/Music issues worth fixing (episodes loose in a show root, scrambled export filenames, etc.) so the user can decide.

> The script is pure-ASCII in source and builds the en-dash from `[char]0x2013` — never paste literal en/em-dashes into it (PowerShell 5.1 reads the file as ANSI and mangles them, breaking parsing).

---

## File Naming Preferences

These conventions apply to the **Movies** library (and the description portion of Home Movies). All files follow these rules:

### Standard format
```
Title.Words.Year.ext
```
- Words separated by dots, no spaces
- Year always at the end before the extension
- Extension lowercased

### Casing — Start Case (every word)
Every word capitalized regardless of part of speech: `A.Quiet.Place`, `Return.Of.The.King`. No exceptions for articles or prepositions.

### Special characters
- **Apostrophes, colons, commas, exclamation marks, periods, semicolons, brackets, ampersands** → remove entirely
- **Hyphens** → convert to a space (which becomes a dot separator)
- Example: `Schindler's List` → `Schindlers.List`, `Batman: Begins` → `Batman.Begins`

### Roman numerals
Must stay **ALL CAPS** — do NOT apply Start Case to them:
- Correct: `Halloween.II.1981`, `Star.Wars.IV.A.New.Hope.1977`
- Wrong: `Halloween.Ii.1981`, `Star.Wars.Iv.A.New.Hope.1977`

### Edition tags (EXTENDED, UNRATED, Director's Cut, etc.)
Use Plex's official `{edition-Name}` format (requires Plex Pass). Place after the year, before the extension:
```
A.Good.Day.To.Die.Hard.2013.{edition-Extended}.mp4
Blade.Runner.1982.{edition-Directors Cut}.mp4
```
Plex surfaces the edition label in the UI and groups versions of the same film together.

### Metadata ID tags (only when needed)
If Plex is struggling to match a title, add an IMDb or TMDb ID to force an exact match:
```
Timecrimes.2007.{imdb-tt1108906}.mp4
Timecrimes.2007.{tmdb-11622}.mp4
```
Don't add these to every file — only use when Plex can't find the movie on its own.

### Subtitles
Language code goes **after** the year (matches Plex standard):
```
Joe.Versus.The.Volcano.1990.en.srt
```

Movies with subtitle files must be in their own subfolder containing both the video file and the `.srt`:
```
Movies/Train.To.Busan.2016/Train.To.Busan.2016.mp4
Movies/Train.To.Busan.2016/Train.To.Busan.2016.en.srt
```

If a `.srt` file has no language code, inspect the content to determine the language before naming it.

### Disk labels
Remove entirely — `Disk 1`, `Disk 2`, `-disk1`, etc. are DVD-era artifacts and don't belong in the filename.

### Movies without a year
If year can't be found in the filename or Plex, use the title as-is with no year appended.

### Concatenated source filenames
If a source file has no spaces or dots between words (e.g., `iknowwhatyoudidlastsummer.2025.mp4`), the rename script can't auto-split it — the whole title is treated as one word. Flag these for manual correction.

### Multi-part movies (split files)

Plex's official format for movies split across multiple files:

```
/Movies/Movie.Name.Year/Movie.Name.Year – pt1.ext
/Movies/Movie.Name.Year/Movie.Name.Year – pt2.ext
```

- Use an **en-dash** (`–`, U+2013) with spaces on both sides, followed by `pt1`, `pt2`, etc.
- Files **must** live in their own subfolder named after the movie
- All parts must be the same file format with identical audio/subtitle streams
- **Do NOT use** `Part.1`/`Part.2` or `disk1`/`disk2` — Plex treats those as separate movies
- Plex recommends merging the files instead; split support is limited (breaks thumbnails, chapters, stream selection)

### Case-only renames on Windows (NTFS gotcha)

Windows NTFS is case-insensitive, so `Rename-Item "file.Ii.mp4" "file.II.mp4"` silently no-ops — it sees both names as identical. Always use a two-step rename via a temp name:

```powershell
$tempName = $oldName + ".RENAMETMP"
Rename-Item -LiteralPath $oldPath -NewName $tempName
Rename-Item -LiteralPath (Join-Path $dir $tempName) -NewName $newName
```

Also: PowerShell string comparison (`-ne`, `-eq`) is case-insensitive by default. Use `-cne` / `-ceq` when comparing filenames that differ only by case, otherwise the diff check always returns false and nothing gets renamed.

---

## Naming — Other Libraries

The dot-format above applies to **Movies** (and Home Movies' description portion). The other libraries follow their own standard Plex layouts — `/plex add` validates these but does **not** convert them to dot-format.

### Home Movies (section = `libraries.homemovies.key`)
Home movies have no official title, so the convention is **date-first** for chronological sorting plus a plain-language description:
```
YYYY-MM-DD.Description.In.Start.Case.ext     (full date known)
YYYY-MM.Description.ext                        (month known)
YYYY.Description.ext                           (only year known)
```
- Date first, ISO format, hyphenated (`2015-06-20`).
- Description in Start Case, dot-separated — same special-char removal as movies, **except** `&` → `And`.
- Date source: embedded `creation_time` (needs ffprobe) → otherwise **ask the user**. Never guess a date from filesystem timestamps (they reflect the copy date).
- Example: a wedding filmed 2015-06-20 → `2015-06-20.A.Wedding.mp4`

### TV Shows (section = `libraries.tv.key`)
Already on Plex's standard layout — **leave as-is**, natural spacing (not dot-format):
```
Show Name (Year)/Season N/Show Name - sNNeNN[ - Episode Title].ext
```
- Each episode must live under a `Season N` folder (not loose in the show root).
- Episode marker `sNNeNN` (a leading `NxNN` is tolerated). Specials go under a `Specials` (or `Season 00`) folder — files there are **not** flagged for missing a marker, since specials legitimately lack `sNNeNN`.
- `/plex add tv` reports violations (loose episodes, markerless junk files) but does not rename.

### Music (section = `libraries.music.key`)
Plex reads embedded ID3/MP4 tags, so on-disk names matter little — **report-only, never auto-rename**:
```
Artist/Album/## - Track Title.ext
```
- `/plex add music` flags only truly unstructured names (no leading track number, e.g. scrambled store-export filenames) and tracks not nested in an album folder. A top-level folder named `Artist - Album` (combined) that holds numbered tracks directly is treated as a valid album folder and is **not** flagged.

#### Fixing a track's album / tags (no external tools)
Renaming the folder does **not** change what Plex shows — Plex groups by the embedded `ALBUM` tag, not the folder. A track with no album tag shows `[Unknown Album]`, and Plex **won't** let you rename that virtual album via the API (`PUT …type=9` returns 400). Fix it at the source:
1. **Write a real ID3v2.3 tag** by rewriting the file in PowerShell (pure .NET bytes, no downloads). Strip the leading `ID3` tag (header is 10 bytes + a syncsafe size), prepend a fresh tag with `TIT2/TPE1/TALB/TPE2/TRCK/TYER/TCON` text frames (each: 4-char ID + **non-syncsafe** big-endian size + `00 00` flags + `00` encoding byte + Latin-1 text), then keep the audio from the old tag's end (verify it starts `FF Ex`). **Back up the file first.** Windows Explorer's Details tab often writes a tag Plex/other parsers can't read, so don't rely on it.
2. **Force a fresh import.** Re-reading an existing track updates its own fields but **never moves it between albums** (album membership is assigned only on first add). So rename the file to `.disabled`, scan the artist path, `PUT /library/sections/{musicKey}/emptyTrash`, then rename back and scan again — Plex re-adds it fresh and reads the new album.

### PowerShell pattern for batch operations
```powershell
$cfg     = Get-Content "$HOME\.claude\plex\config.json" -Raw | ConvertFrom-Json
$base    = $cfg.server.TrimEnd('/')
$headers = @{ 'X-Plex-Token' = $cfg.token; 'Accept' = 'application/json' }
$movies  = $cfg.libraries.movies.key

# Search
$res = Invoke-RestMethod -Uri "$base/library/sections/$movies/search?query=TITLE&type=1" -Headers $headers
$res.MediaContainer.Metadata | Select-Object ratingKey, title, year

# Add to collection
Invoke-RestMethod -Uri "$base/library/sections/$movies/all?type=1&id=RATINGKEY&collection%5B0%5D.tag.tag=COLLECTION+NAME" -Method PUT -Headers $headers
```

---

## Opening Prompt

After invoking this skill (with no `add` argument), say:

> "Connected to Plex. What would you like to do? I can manage collections, playlists, metadata, watch history, and more — or cross-reference a movie list against your library."

(If `~/.claude/plex/config.json` is missing, say instead: "I don't see a Plex config yet — run `/plex:init` and I'll help you set it up.")
