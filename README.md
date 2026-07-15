## Git History Reset Script

A minimalist Python script to wipe your entire Git commit history while keeping
your current code intact.

## ⚠️ Disclaimer

USE AT YOUR OWN RISK. This script performs destructive Git operations. It
permanently deletes history from your local and remote repositories. Back up
your repository before running it.

## Why

Specially in the AI era, my projects start messy until I decide they are
important enough to be more organized. Eventually I reset the history and start
taking versioning seriously.

![Messy](https://imgs.xkcd.com/comics/git_commit.png)

https://imgs.xkcd.com/comics/git_commit.png

## How - What it does

0. Checks some prerequisites: Git installed, correct OS (Windows), and if the
   remote exists etc.
1. Creates a temporary orphan branch.
2. Adds and commits your current files.
3. Deletes the old main branch.
4. Renames the temporary branch to main.
5. Force-pushes the clean state to origin.

## How to Use

```python
python main.py
```
