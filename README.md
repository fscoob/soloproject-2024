# Tasks — a Pythonista app

A to-do list app for [Pythonista 3](http://omz-software.com/pythonista/) on iPhone and iPad.
It uses Pythonista's built-in `ui` module, so there's nothing extra to install.

## Features
- Quick-add bar, plus a **New** form for a task with notes
- Tap a task to check it off or uncheck it
- Tap the ⓘ button to edit the title, the notes or the completed state
- Swipe left to delete
- Live search over titles and notes
- **Options**: hide or show completed tasks, clear completed tasks
- Tasks are saved to `tasks.json` next to the scripts

## Install
1. Copy `main.py` and `task_store.py` into the **same folder** in Pythonista
   (for example with Working Copy, the Files app, or by pasting into new files).
2. Open `main.py` and tap ▶︎ to run it.
3. Optional: in Pythonista go to *Settings → Home Screen* (or use the wrench menu
   *Shortcuts → Home Screen*) to add a home-screen icon that launches `main.py`.

## Files
| File | Purpose |
| --- | --- |
| `main.py` | The user interface (Pythonista `ui`, `dialogs` and `console` modules) |
| `task_store.py` | Plain-Python storage layer with no iOS dependencies, so you can test it anywhere |
| `test_task_store.py` | Unit tests for the storage layer (`python -m unittest`) |
