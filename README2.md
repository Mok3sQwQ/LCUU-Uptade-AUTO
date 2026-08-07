# LCUU Tier Update

An automated Python tool for maintaining Smogon's Little Cup (LC) tier data. It downloads monthly usage statistics, calculates tier shifts, updates the local tier database, and produces a forum-ready BBCode report.

It also includes a small Viability Rankings (VR) BBCode formatter.

## Features

- Downloads `gen9lc-1630.txt` usage statistics from Smogon.
- Calculates usage cutoffs from configurable T-values.
- Identifies Pokémon that rise to LC OU or drop from LC OU.
- Generates a BBCode tier-shift report with a spoiler section for base data.
- Creates a dated backup before updating tier data.
- Formats VR lists into color-coded BBCode.

## Requirements

- Python 3.x
- No external packages; the project only uses Python's standard library.

## Project Files

| File | Purpose |
| --- | --- |
| `tier_updater.py` | Main script for downloading stats, calculating shifts, and updating tiers. |
| `tiers.json` | Current tier database. |
| `stats.txt` | Downloaded Smogon usage data. |
| `tier_shift_report.txt` | Generated BBCode report. |
| `tiers_backup_YYYYMM.json` | Automatic pre-update backup, created only when shifts are found. |
| `vr_post.py` | VR list to BBCode formatter. |

## Running the Tier Updater

1. Open a terminal in the project folder.
2. Run one of the following commands:

   ```bash
   python tier_updater.py
   ```

   On Windows, if `python` is not available, use:

   ```powershell
   py tier_updater.py
   ```

3. Enter the target stats month when prompted, for example:

   ```text
   2026-07
   ```

The script will:

1. Determine the Smogon cycle quarter and month.
2. Download and save the matching usage statistics as `stats.txt`.
3. Calculate the usage cutoff and determine rises or drops.
4. Save a BBCode report as `tier_shift_report.txt`.
5. If shifts are found, back up the current tier data before overwriting `tiers.json`.

For an input of `2026-07`, the backup file is named:

```text
tiers_backup_202607.json
```

## Report Output

The report includes a base-data spoiler, followed by rise and drop sections:

```bbcode
========== TIER SHIFT REPORT ==========

[SPOILER="Base Data"]

Cycle: Q3 - Month 2 (August)

Mode: Quick Drops Only (Rises Locked)

Teams Parameter (T): 16 (base_t * 2)

Applied Cutoff: 4.24%

[/SPOILER]

**Rises (To LC OU):**

None (Rises are locked for this cycle phase)

**Drops (From LC OU):**

:zorua-hisui: Zorua-Hisui (2.56%)
```

## Configuration

Edit the **Configuration Settings** section at the top of `tier_updater.py` to change:

- `base_t`: Base teams parameter used in cutoff calculations.
- `x_value`: Cutoff input value.
- `end_of_gen_mode`: Locks rises at the end of a generation.
- `recently_banned`: Pokémon to exclude from usage-based shifts.

## Monthly Automation

The repository includes `.github/workflows/monthly-tier-update.yml`. GitHub Actions runs it on the 2nd day of each month at 08:00 UTC.

The workflow processes the previous month's stats, commits the updated data files to the repository, and creates a GitHub Issue titled `Publish LCUU tier update for <Month Year>` as a reminder to publish the report manually. It does not post to the Smogon forums.

You can also run the workflow manually from the **Actions** tab and optionally provide a stats month in `YYYY-MM` format.

## Running the VR Formatter

1. Open `vr_post.py`.
2. Paste Pokémon names into `mons_input`.
3. Paste their corresponding rankings into `tiers_input`.
4. Run:

   ```bash
   python vr_post.py
   ```

5. Copy the generated BBCode into the Smogon forums.

## Credits

The VR formatter is based on a tool originally created by [Albi_75](https://github.com/Albi-75/lc-lowtiers-resources).
