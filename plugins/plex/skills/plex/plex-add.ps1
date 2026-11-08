<#
  plex-add.ps1  -  Ingest & normalize media, then trigger a Plex library scan.
  Backs the `/plex add` command. Dry-run by default; pass -Apply to rename.

  Usage:
    plex-add.ps1 -Target all                 # dry-run every library
    plex-add.ps1 -Target movies -Apply -Scan # rename movies, then scan section
    Targets: movies | homemovies | tv | music | all

  Config:
    All server/library specifics are read at runtime from a per-machine config
    file OUTSIDE this repo, so the plugin stays generic and public-safe:
        $HOME/.claude/plex/config.json
    Run the /plex:init skill once to create it. Schema:
        {
          "server": "http://localhost:32400",
          "token":  "<X-Plex-Token>",
          "quarantine": "D:\\Plex\\_Quarantine",
          "libraries": {
            "movies":     { "key": 1, "path": "D:\\Plex\\Movies" },
            "homemovies": { "key": 7, "path": "D:\\Plex\\Home Movies" },
            "tv":         { "key": 3, "path": "D:\\Plex\\TV Shows" },
            "music":      { "key": 8, "path": "D:\\Plex\\Music" }
          },
          "horror": {                         // OPTIONAL — omit to skip curation
            "genreKey": 123,
            "familyFriendlyCollectionKey": 456,
            "notHorrorLabel": "not-horror"
          }
        }

  Notes
   * Movies use the documented dot-format; the normalizer is conservative -
     it preserves multi-part " - ptN" suffixes, {edition|imdb|tmdb-} tags,
     all-caps acronyms (DC), roman numerals (II), and MixedCase (4Ever).
   * TV & Music already follow Plex's standard layouts, so they are VALIDATED
     and reported, never reformatted into dot-format. TV auto-fixes only the
     unambiguous cases; Music is report-only (Plex is tag-driven).
   * Home Movies use a date-first convention (see Get-CleanHomeMovieName).
     A file whose date can't be derived is flagged, never guessed.
#>
param(
    [ValidateSet('movies','homemovies','tv','music','all')]
    [string]$Target = 'all',
    [switch]$Apply,       # actually rename/move (default: dry-run)
    [switch]$Scan,        # trigger Plex scan of affected sections when done
    [switch]$NoJunkSweep  # skip the junk sweep (on by default as part of every run)
)

$ErrorActionPreference = 'Stop'

# ---------- config (per-machine, outside the repo) ------------------------
$ConfigDir  = Join-Path $HOME '.claude\plex'
$ConfigFile = Join-Path $ConfigDir 'config.json'
if (-not (Test-Path -LiteralPath $ConfigFile)) {
    throw "No Plex config at $ConfigFile. Run the /plex:init skill first to create it."
}
$cfg = Get-Content -LiteralPath $ConfigFile -Raw | ConvertFrom-Json

$PlexBase = ([string]$cfg.server).TrimEnd('/')
$Headers  = @{ 'X-Plex-Token' = $cfg.token; 'Accept' = 'application/json' }
$VideoExt = @('*.mp4','*.mkv','*.m4v','*.avi')

$QuarantineRoot = $cfg.quarantine   # a folder outside every library path, so Plex never scans it

$Sections = @{}
foreach ($name in 'movies','homemovies','tv','music') {
    $lib = $cfg.libraries.$name
    if ($lib) { $Sections[$name] = @{ Key = [int]$lib.key; Path = [string]$lib.path } }
}

$romanRx  = '^(I{1,3}|IV|V|VI{0,3}|IX|X|XI{0,3}|XIV|XV)$'
$encodeRx = '(?i)^(BluRay|WEBRip|WEB-DL|WEB|HDRip|BRRip|BDRip|DVDRip|DVD|x264|x265|h264|h265|HEVC|XviD|AAC.*|DTS.*|DD5|AC3|1080p|720p|2160p|480p|4K|HDR|REMUX|PROPER|REPACK|RARBG|YIFY|YTS.*)$'

# ---------- helpers -------------------------------------------------------
function Invoke-TwoStepRename {
    param([string]$FullPath, [string]$NewName)
    $dir = Split-Path $FullPath -Parent
    $tmp = (Split-Path $FullPath -Leaf) + '.RENAMETMP'
    Rename-Item -LiteralPath $FullPath -NewName $tmp            # NTFS case-insensitive: temp hop
    Rename-Item -LiteralPath (Join-Path $dir $tmp) -NewName $NewName
}

function Start-Case-Token {
    param([string]$t)
    if     ($t -match '^(19|20)\d{2}$')            { $t }                       # year
    elseif ($t.ToUpper() -cmatch $script:romanRx -and $t.Length -le 5) { $t.ToUpper() } # roman
    elseif ($t -cmatch '^[a-z0-9]+$')              { $t.Substring(0,1).ToUpper() + $t.Substring(1) } # all-lower
    else                                           { $t }                       # acronym / MixedCase
}

# ---------- MOVIES --------------------------------------------------------
function Get-CleanMovieName {
    param([string]$baseName, [string]$ext)

    $enDash = [char]0x2013
    $partSuffix = ''
    $mPart = [regex]::Match($baseName, '\s+' + $enDash + '\s+pt(\d+)\s*$')
    if ($mPart.Success) {
        $partSuffix = ' ' + $enDash + ' pt' + $mPart.Groups[1].Value
        $baseName = $baseName.Substring(0, $mPart.Index)
    }

    $tags = [System.Collections.Generic.List[string]]::new()
    $work = [regex]::Replace($baseName, '\{(edition|imdb|tmdb)-[^}]+\}', { param($m) $tags.Add($m.Value); '' })

    $work = $work -replace '\[[^\]]*\]','' -replace '\([^\)]*\)',''
    $work = $work -replace '-',' ' -replace '\s+','.'
    $work = $work -replace "['`,:;!&]",''
    $work = $work -replace '\.\.+','.'
    $tokens = $work.Trim('.').Split('.') | Where-Object { $_ -ne '' }

    $yearIdx = -1
    for ($i=0; $i -lt $tokens.Count; $i++) { if ($tokens[$i] -match '^(19|20)\d{2}$') { $yearIdx = $i } }
    if ($yearIdx -ge 0) { $titleTokens = $tokens[0..$yearIdx] }
    else { $titleTokens = $tokens | Where-Object { $_ -notmatch $script:encodeRx } }

    $out = foreach ($t in $titleTokens) { Start-Case-Token $t }

    $name = ($out -join '.')
    foreach ($tag in $tags) { $name += '.' + $tag }
    $name += $partSuffix
    $name += $ext.ToLower()
    return $name
}

# ---------- HOME MOVIES ---------------------------------------------------
# Convention:  YYYY-MM-DD.Description.In.Start.Case.ext   (fewer date parts as known)
#   & -> And   |  apostrophes/specials removed  |  hyphens/spaces -> dots
function Get-CleanHomeMovieName {
    param([System.IO.FileInfo]$file)

    $base = $file.BaseName
    # Existing date prefix?  YYYY, YYYY-MM, or YYYY-MM-DD at the start.
    $mDate = [regex]::Match($base, '^(?<d>(19|20)\d{2}(-\d{2}(-\d{2})?)?)[.\s_-]+(?<rest>.+)$')
    if ($mDate.Success) {
        $date = $mDate.Groups['d'].Value; $desc = $mDate.Groups['rest'].Value
    } else {
        # No date in name and no reliable embedded date (ffprobe absent) -> flag.
        return [pscustomobject]@{ Target=$null; Flag="no derivable date - supply YYYY[-MM[-DD]] + description" }
    }

    $desc = $desc -replace '&',' And '
    $desc = $desc -replace '-',' ' -replace '\s+','.'
    $desc = $desc -replace "['`,:;!]",''
    $desc = $desc -replace '\.\.+','.'
    $descTokens = $desc.Trim('.').Split('.') | Where-Object { $_ -ne '' } | ForEach-Object { Start-Case-Token $_ }
    $name = $date + '.' + ($descTokens -join '.') + $file.Extension.ToLower()
    return [pscustomobject]@{ Target=$name; Flag=$null }
}

# Plex derives a home-movie's title from its filename, so it shows the ugly date-prefixed
# form ("2006 09 14 A Birthday Party"). This sets a readable title + the filmed date
# via the API. It ONLY touches titles that still look raw (date-prefixed) so a nicer,
# hand-edited/locked title (with real & and apostrophes) is never clobbered.
function Repair-HomeMoviePlexTitles {
    param([bool]$DoApply)
    $sec = $script:Sections.homemovies.Key
    $items = Invoke-RestMethod -Uri "$script:PlexBase/library/sections/$sec/all?type=1" -Headers $script:Headers
    $fixes = @()
    foreach ($it in $items.MediaContainer.Metadata) {
        $file = @($it.Media.Part.file)[0]
        if (-not $file) { continue }
        $bn = [System.IO.Path]::GetFileNameWithoutExtension($file)
        $m = [regex]::Match($bn, '^(?<d>(19|20)\d{2}(-\d{2}(-\d{2})?)?)\.(?<rest>.+)$')
        if (-not $m.Success) { continue }
        # Only repair a still-raw title (starts with the date, e.g. "2006 09 14 ...").
        if ($it.title -notmatch '^(19|20)\d{2}[ ._-]\d{2}') { continue }
        $date  = $m.Groups['d'].Value
        $title = ($m.Groups['rest'].Value -replace '\.',' ').Trim()
        $fixes += [pscustomobject]@{ id=$it.ratingKey; title=$title; date=$date; old=$it.title }
    }
    Write-Host "=== HOME MOVIE PLEX TITLES ===  raw-titles-to-fix=$($fixes.Count)"
    foreach ($f in $fixes) { Write-Host "  [$($f.id)] '$($f.old)' -> '$($f.title)'  ($($f.date))" }
    if ($DoApply -and $fixes.Count) {
        foreach ($f in $fixes) {
            $t = [uri]::EscapeDataString($f.title)
            $uri = "$script:PlexBase/library/sections/$sec/all?type=1&id=$($f.id)" +
                   "&title.value=$t&title.locked=1&originallyAvailableAt.value=$($f.date)&originallyAvailableAt.locked=1"
            Invoke-RestMethod -Uri $uri -Method PUT -Headers $script:Headers | Out-Null
        }
        Write-Host "  applied $($fixes.Count) title fix(es). (Refine punctuation/& by hand where needed.)"
    }
}

# ---------- HORROR AUTO-CURATION (optional) -------------------------------
# Keeps a "True Horror"-style smart collection (genre Horror minus a not-horror label) clean as
# new movies arrive. Kid/family horror is auto-excluded (zero-false-positive rule: Family genre OR
# in the Family Friendly collection). Genuinely ambiguous new horror (Venom/Spawn-type) can't be
# judged by rule, so it's REPORTED once for a human call — tracked in a state file so it isn't nagged.
# Runs ONLY when config.json defines a `horror` block; otherwise it is skipped.
$Horror          = $cfg.horror
$HorrorStateFile = Join-Path $ConfigDir 'plex-horror-seen.json'

function Invoke-HorrorCuration {
    param([bool]$DoApply)
    if (-not $script:Horror) { Write-Host "=== HORROR CURATION ===  skipped (no 'horror' block in config.json)"; return }
    $sec = $script:Sections.movies.Key
    $base = $script:PlexBase; $h = $script:Headers
    $genreKey  = $script:Horror.genreKey
    $ffKey     = $script:Horror.familyFriendlyCollectionKey
    $notLabel  = $script:Horror.notHorrorLabel

    $horror   = @((Invoke-RestMethod -Uri "$base/library/sections/$sec/all?genre=$genreKey" -Headers $h).MediaContainer.Metadata)
    $labeled  = @((Invoke-RestMethod -Uri "$base/library/sections/$sec/all?label=$notLabel" -Headers $h).MediaContainer.Metadata).ratingKey
    $famKey   = ((Invoke-RestMethod -Uri "$base/library/sections/$sec/genre" -Headers $h).MediaContainer.Directory | Where-Object { $_.title -eq 'Family' }).key
    $famGenre = @((Invoke-RestMethod -Uri "$base/library/sections/$sec/all?genre=$famKey" -Headers $h).MediaContainer.Metadata).ratingKey
    $ffMembers= @((Invoke-RestMethod -Uri "$base/library/collections/$ffKey/children?X-Plex-Container-Size=1000" -Headers $h).MediaContainer.Metadata).ratingKey

    $seen = @()
    if (Test-Path -LiteralPath $script:HorrorStateFile) {
        # NB: ConvertFrom-Json returns a JSON array as ONE object in PS 5.1, so assign first,
        # then @()-wrap the variable (which enumerates) — @(pipeline) would nest it and break -contains.
        $loaded = Get-Content -LiteralPath $script:HorrorStateFile -Raw | ConvertFrom-Json
        $seen = @($loaded)
    }

    $autoExclude = @(); $review = @()
    foreach ($m in $horror) {
        if ($seen -contains $m.ratingKey) { continue }          # already processed in a prior run
        if ($labeled -contains $m.ratingKey) { continue }        # already excluded by hand
        $isKid = ($famGenre -contains $m.ratingKey) -or ($ffMembers -contains $m.ratingKey)
        if ($isKid) { $autoExclude += $m } else { $review += $m }
    }

    Write-Host "=== HORROR CURATION ===  new-since-last-run=$(@($autoExclude).Count + @($review).Count)  auto-exclude=$(@($autoExclude).Count)  to-review=$(@($review).Count)"
    foreach ($m in $autoExclude) { Write-Host "  [auto not-horror] $($m.title) ($($m.year))" }
    foreach ($m in $review)      { Write-Host "  [REVIEW - added to True Horror] $($m.title) ($($m.year))  -> tell me if this isn't really horror" }

    if ($DoApply) {
        foreach ($m in $autoExclude) {
            Invoke-RestMethod -Method PUT -Headers $h -Uri "$base/library/sections/$sec/all?type=1&id=$($m.ratingKey)&label%5B0%5D.tag.tag=$notLabel" | Out-Null
        }
        # Everything we saw this run (auto-excluded + reviewed) is now "processed" so reviews aren't repeated.
        $newSeen = @($seen) + @($autoExclude.ratingKey) + @($review.ratingKey) | Select-Object -Unique
        $newSeen | ConvertTo-Json | Set-Content -LiteralPath $script:HorrorStateFile -Encoding UTF8
        if ($autoExclude.Count) { Write-Host "  auto-excluded $(@($autoExclude).Count) kid/family horror film(s)." }
    }
}

# ---------- processors ----------------------------------------------------
function Process-MovieLike {
    param([string]$Path, [scriptblock]$Namer, [string]$Label)
    $files = Get-ChildItem $Path -Recurse -File -Include $script:VideoExt
    $changed = @(); $flagged = @()
    foreach ($f in $files) {
        $res = & $Namer $f
        if ($res -is [string]) { $target = $res; $flag = $null } else { $target = $res.Target; $flag = $res.Flag }
        if ($flag) { $flagged += [pscustomobject]@{ File=$f.Name; Note=$flag }; continue }
        if ($target -and $target -cne $f.Name) {
            $changed += [pscustomobject]@{ From=$f.Name; To=$target; Full=$f.FullName; Dir=$f.DirectoryName }
        }
    }
    Write-Host "=== $Label ===  files=$($files.Count)  to-rename=$($changed.Count)  flagged=$($flagged.Count)"
    foreach ($c in $changed) { Write-Host "  $($c.From)"; Write-Host "    -> $($c.To)" }
    foreach ($fl in $flagged) { Write-Host "  [FLAG] $($fl.File)  ($($fl.Note))" }
    if ($Apply) {
        foreach ($c in $changed) {
            $dest = Join-Path $c.Dir $c.To
            # A case-only rename maps to the SAME NTFS file (dest path == source, case-insensitive) — not a real collision.
            $sameFile = ($dest -ieq $c.Full)
            if ((Test-Path -LiteralPath $dest) -and -not $sameFile) { Write-Host "  [SKIP collision] $($c.To) exists"; continue }
            Invoke-TwoStepRename -FullPath $c.Full -NewName $c.To
        }
        if ($changed.Count) { Write-Host "  applied $($changed.Count) renames." }
    }
    return $changed.Count
}

function Process-TV {
    param([string]$Path)
    $issues = @()
    # Episodes dumped directly in the library root (not inside any show folder) — these never
    # reach the per-show loop below, so flag them explicitly or they slip through silently.
    foreach ($l in Get-ChildItem -Path "$Path\*" -File -Include $script:VideoExt) {
        $issues += "[<library root>] loose at TV root (needs a show folder): $($l.Name)"
    }
    foreach ($show in Get-ChildItem $Path -Directory) {
        # loose video files sitting directly in the show root (should be under Season N)
        $loose = Get-ChildItem -Path "$($show.FullName)\*" -File -Include $script:VideoExt
        foreach ($l in $loose) { $issues += "[$($show.Name)] loose in show root: $($l.Name)" }
        foreach ($vid in Get-ChildItem $show.FullName -Recurse -File -Include $script:VideoExt) {
            # Specials legitimately lack sNNeNN markers, so don't flag files inside a Specials / Season 00 folder.
            $parent = Split-Path $vid.DirectoryName -Leaf
            if ($parent -match '(?i)^(specials?|season\s*0+)$') { continue }
            # Accept sNNeNN (optional space) and the legacy NxNN marker; flag only truly markerless files.
            if ($vid.Name -notmatch '(?i)(s\d{1,2}\s*e\d{1,3}|\d{1,2}x\d{2,3})') { $issues += "[$($show.Name)] no episode marker: $($vid.Name)" }
        }
    }
    Write-Host "=== TV SHOWS ===  issues=$($issues.Count)  (validate-only; standard layout preserved)"
    $issues | Select-Object -First 60 | ForEach-Object { Write-Host "  $_" }
    return 0
}

function Process-Music {
    param([string]$Path)
    $issues = @()
    foreach ($artist in Get-ChildItem $Path -Directory) {
        # A top-level folder named "Artist - Album" is itself a valid album folder holding tracks
        # directly (a common layout Plex reads fine via tags) — don't flag those as loose.
        $isCombinedAlbumFolder = ($artist.Name -match ' - ')
        $looseInArtist = if ($isCombinedAlbumFolder) { @() } else { Get-ChildItem -Path "$($artist.FullName)\*" -File -Include *.mp3,*.m4a,*.flac }
        foreach ($l in $looseInArtist) { $issues += "[$($artist.Name)] track not in an album folder: $($l.Name)" }
        foreach ($trk in Get-ChildItem $artist.FullName -Recurse -File -Include *.mp3,*.m4a,*.flac) {
            # Plex is tag-driven; only flag files with no leading track number at all (e.g. scrambled export names).
            if ($trk.Name -notmatch '^\d{1,2}[\s\-_.]') { $issues += "[$($artist.Name)] no leading track number: $($trk.Name)" }
        }
    }
    Write-Host "=== MUSIC ===  issues=$($issues.Count)  (report-only; Plex reads embedded tags)"
    $issues | Select-Object -First 60 | ForEach-Object { Write-Host "  $_" }
    return 0
}

# ---------- JUNK SWEEP ----------------------------------------------------
# Conservative: never quarantine a file that has a real episode marker, and only
# treat keyword/tiny-clip hits as junk when the file also LACKS an episode marker.
# So real content (e.g. "Doctor Who - Time Crash.AVI", Ink Master specials) is safe.
function Test-IsJunk {
    param([System.IO.FileInfo]$f, [bool]$AggressiveVideo = $true)
    # Broad list so we never mistake a real video (e.g. .mov special) for a stray file.
    $videoExts = @('.mp4','.mkv','.m4v','.avi','.mov','.wmv','.mpg','.mpeg','.flv','.ts','.m2ts','.webm','.divx','.vob')
    $junkExts  = @('.txt','.nfo','.url','.exe','.lnk','.ini','.db','.bat','.cmd','.sfv','.sample')
    $ext = $f.Extension.ToLower()
    # OS metadata cruft (name-based, junk in every library incl. Music): macOS AppleDouble
    # "._name" forks, .DS_Store, Spotlight/Trashes, and Windows Thumbs.db/desktop.ini.
    if ($f.Name -like '._*' -or $f.Name -eq '.DS_Store' -or $f.Name -like '.Spotlight*' -or
        $f.Name -like '.Trashes*' -or $f.Name -eq 'Thumbs.db' -or $f.Name -eq 'desktop.ini') { return $true }
    if ($ext -in $junkExts) { return $true }                          # unambiguous non-content files
    # Keyword/size heuristics only in AggressiveVideo mode (TV/Movies). In Music, small video
    # files are usually wanted music videos, not junk, so we skip them here.
    if ($AggressiveVideo -and $ext -in $videoExts) {
        $hasMarker = $f.Name -match '(?i)(s\d{1,2}\s*e\d{1,3}|\d{1,2}x\d{2,3})'
        if (-not $hasMarker) {
            if ($f.BaseName -match '(?i)(trailer|sample|slogan|readme|proof|RARBG)') { return $true }
            if ($f.Length -lt 20MB) { return $true }                  # tiny markerless clip
        }
    }
    # images, subtitles, and anything else: leave for manual review, never auto-quarantine
    return $false
}

function Invoke-JunkSweep {
    param([string[]]$Paths)
    $musicPath = $script:Sections.music.Path
    $cands = foreach ($p in $Paths) {
        $aggressive = ($p -ne $musicPath)   # Music: only non-content extensions count as junk
        # -Force so hidden OS cruft (macOS ._ forks / .DS_Store are Hidden on Windows) is caught.
        # Tag each candidate with the library root it came from so the quarantine name can be
        # derived without hardcoding any media root path.
        Get-ChildItem $p -Recurse -File -Force -ErrorAction SilentlyContinue |
            Where-Object { Test-IsJunk $_ -AggressiveVideo $aggressive } |
            ForEach-Object { $_ | Add-Member -NotePropertyName SweepRoot -NotePropertyValue $p -PassThru }
    }
    Write-Host "=== JUNK SWEEP ===  candidates=$(@($cands).Count)  quarantine=$QuarantineRoot"
    foreach ($c in $cands) { Write-Host ("  {0,7:N1} MB  {1}" -f ($c.Length/1MB), $c.FullName) }
    if ($Apply -and @($cands).Count) {
        if (-not (Test-Path -LiteralPath $QuarantineRoot)) { New-Item -ItemType Directory -Path $QuarantineRoot | Out-Null }
        $manifest = Join-Path $QuarantineRoot '_manifest.txt'
        foreach ($c in $cands) {
            # Flatten into one folder; prefix with the path relative to the library's parent so names
            # stay unique and origin stays obvious (e.g. "Movies - Subdir - stray.nfo").
            $relRoot = Split-Path $c.SweepRoot -Parent
            $rel = $c.FullName.Substring($relRoot.Length).TrimStart('\','/') -replace '[\\/]',' - '
            $destName = $rel
            $dest = Join-Path $QuarantineRoot $destName
            $n = 1
            while (Test-Path -LiteralPath $dest) { $dest = Join-Path $QuarantineRoot ("$destName ($n)"); $n++ }
            Move-Item -LiteralPath $c.FullName -Destination $dest
            Add-Content -LiteralPath $manifest -Value ("{0}`t<=`t{1}" -f (Split-Path $dest -Leaf), $c.FullName)
        }
        Write-Host "  moved $(@($cands).Count) file(s) to quarantine. Origins logged in _manifest.txt (delete the folder when you're happy)."
    }
}

# ---------- run -----------------------------------------------------------
$affected = @()
function Run-Target([string]$t) {
    switch ($t) {
        'movies'     {
            if (Process-MovieLike $script:Sections.movies.Path { param($f) Get-CleanMovieName $f.BaseName $f.Extension } 'MOVIES') { $script:affected += $script:Sections.movies.Key }
            # Keep True Horror clean: auto-exclude kid/family horror, report ambiguous new horror.
            try { Invoke-HorrorCuration -DoApply $Apply } catch { Write-Host "=== HORROR CURATION ===  skipped ($($_.Exception.Message))" }
        }
        'homemovies' {
            Process-MovieLike $script:Sections.homemovies.Path { param($f) Get-CleanHomeMovieName $f } 'HOME MOVIES' | Out-Null
            if ($Apply) { $script:affected += $script:Sections.homemovies.Key }
            # Fix ugly filename-derived titles for items Plex has already imported.
            # (Brand-new files: re-run after the scan finishes so they exist in Plex first.)
            Repair-HomeMoviePlexTitles -DoApply $Apply
        }
        'tv'         { Process-TV    $script:Sections.tv.Path    | Out-Null }
        'music'      { Process-Music $script:Sections.music.Path | Out-Null }
    }
}

if ($Target -eq 'all') { 'movies','homemovies','tv','music' | ForEach-Object { Run-Target $_ } }
else { Run-Target $Target }

if (-not $NoJunkSweep) {
    if ($Target -eq 'all') { $sweepPaths = $Sections.Values.Path }
    else { $sweepPaths = @($Sections[$Target].Path) }
    Invoke-JunkSweep -Paths $sweepPaths
}

if ($Scan -and $Apply) {
    foreach ($key in ($affected | Select-Object -Unique)) {
        Invoke-RestMethod -Uri "$PlexBase/library/sections/$key/refresh" -Headers $Headers | Out-Null
        Write-Host "Triggered Plex scan: section $key"
    }
} elseif ($Scan) {
    Write-Host "(-Scan ignored in dry-run; re-run with -Apply -Scan to scan)"
}
