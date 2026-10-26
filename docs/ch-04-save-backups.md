# Backing up save files so nothing is ever lost

Somewhere, a grown-up is staring at a reboot prompt about disk space,
playing a game they have loved for 60 hours, and wondering why that save
never went anywhere. This chapter is insurance against being that person.

## What a save file is

A **save file** is a small file — often surprisingly small — holding the
record of where you got in a game: your progress, your choices, your
house with the roses. It is the game's memory of you, and it lives on
*your* computer unless the game puts it on a server (as MMOs like FFXIV
do for character data — but even FFXIV has client-side settings you want
backed up; see the FFXIV section below).

Where does it live? Some honest neighborhoods:

- `Documents` / `My Documents` — common and easy to find.
- `AppData` (Windows) — hidden by default; type `%APPDATA%` or
  `%LOCALAPPDATA%` into a File Explorer window and press Enter. Games
  love it here, in folders named after themselves.
- `Steam userdata` — Steam's own folder when a game uses Steam cloud
  storage; the game folder in your Steam library holds
  `steamapps/common/<game>`, and saves can live near that too.
- `~/Library/Application Support` (macOS), `~/.config` or `~/.local/share`
  (Linux).

You do not need to memorize those. You need to look *once*, for each
game you love, and write it down. That is the first half of the method.

## Cloud saves are a convenience, not a backup

Launchers like Steam can upload saves to their servers
([cloud save](glossary.md#cloud-save)). This is a very nice feature and
it is worth turning on per game (Steam: right-click the game, Properties,
General, Steam Cloud). It is *not* a backup system:

- It runs quietly; you rarely see it working, so you cannot trust it
  in silence. When a cloud save syncs an *empty* corner, or a patch
  breaks save compatibility, you will feel it — and a local copy will
  be the one still standing.
- It only covers games that offer it. Half your library probably does
  not.
- A backup you can *hold* (on a drive you can see) is the grown-up one.
  Also see [chapter 1](ch-01-launchers.md#what-makes-a-launcher-trustworthy)
  for 2FA and the honest truth about accounts.

## The grown-up backup method

Three steps, about an hour a year:

1. **Locate once.** For each game you care about, find its save folder
   (search "<game name> save file location" with the game name and "PC";
  the community keeps this honest). Note the path in a text file called
   `save-locations.txt` in your Documents folder.
2. **Copy elsewhere.** Make a folder called `Game Saves` in Documents
   (or on an external drive or USB stick). When you hit a milestone —
   finished a story act, built a new house, Sunday evening ritual —
   copy the save folder *whole* into a folder named `Game Saves/<game
   name>/<year-month-day>/`. Date suffixes turn one backup into history,
   which is the difference between insurance and a time machine.
3. **Repeat, gently automated.** Set a recurring reminder — Sunday
   evening is a friendly hour (see [chapter 7](ch-07-screens-and-eyes.md)
   for why gentle endings matter) — or automate it as described below.

> A save file is the only piece of a game that cannot be re-downloaded.
> Everything else in a game is public; your saves are yours alone.

## What the stores back up for you

For honesty's sake, the built-in help, which you get for free:

- **Steam cloud saves** — for games that support it (see above). Works
  across machines, which is magic when it works.
- **FFXIV server data** — your character's *inventory and progress* all
  live on Square Enix's servers; a house move on your end costs nothing
  but login time. Your *settings* (keybinds, hotbars, macros) are saved
  client-side; FFXIV has official tools for those, in
  [chapter 9](ch-09-ffxiv.md#keybind-comfort) and in the
  [launcher](ch-04-save-backups.md#the-launcher-backup-tool) description
  below.

That FFXIV setting backup is the reason this chapter has a whole extra
section.

## The launcher backup tool

FFXIV's proper official backup — on PC, the game launcher has a
"Backup Tool" (reach it via the config button in the launcher). It packs
your characters' keybinds, hotbars, macros, HUD layouts, and gear sets
into a single file (it is called `FFXIVconfig.fea`). Save that file to
your `Game Saves` folder. To restore it after a reinstall or new
computer, use the same button's *Restore* — see
[chapters 9](ch-09-ffxiv.md#keybind-comfort) for context around it.

This is the board game equivalent of "the box with all the pieces lives
in the closet with the label." It works, it is official, it is free.

## Automating backup so grown-ups forget less

The manual method above works. If you are the type who prefers the
computer to do chores, every modern system has a native assistant:

- **Windows File History** — Settings → Update & Security → Backup.
  Point it at an external drive; it keeps versions of Documents (and
  anywhere else you choose), so `Game Saves` gets covered forever.
- **OneDrive / iCloud / Google Drive with a folder rule** — put `Game
  Saves` inside the cloud-synced folder; the copying is then physically
  impossible to forget. (Verify the sync is not skipping
  [AppData](glossary.md#save-file): for hidden folders, copies are
  easier made manually, per the three steps above.)
- **A tiny scheduled script** — if you script your life, a scheduled
  `robocopy` / `rsync` command that mirrors your `Documents/Game Saves`
  folder to an external drive is a five-minute setup that runs forever.

The rule is one in any of these: **two physical copies, one of them
somewhere different.** Extra polish (versioning, encryption) is for
people who save games across multiple years and continents — worth
reading about, not blocking.

## One more caution: uninstalling

Uninstalling a game usually leaves the save files behind, but not always.
default, but not always. Before you uninstall a loved game:

1. Back up first (see the three steps above).
2. When the uninstaller (or Steam) offers "keep user settings," say yes.
3. If you modded the game, keep [chapter 6](ch-06-mod-safety.md)'s rule
   in mind: uninstall mods *first*, run the game once to confirm your
   save still loads, then uninstall the game itself.

Next: free [Steam features](ch-05-steam-freebies.md) worth knowing —
including how the family layer interacts with cloud saves and refunds.
