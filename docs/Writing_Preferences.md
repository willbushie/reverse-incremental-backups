# Writing Preferences

The `preferences.txt` is central to setting up and conducting backups. Without it, the program would not function.

The preferences file should be stored in the base directory of the application.

## Comments

Comments are allowed in the preferences file.

```
# Any line that begins with a '#' will be ignored
# Block comments are not currently supported
...
```

## Separating Preferences

If multiple backup setups are required, the preferences should be separated with a `=`.

```
# backup a
...
=
# backup b
...
```

See [Multiple Setups Example](#multiple-backup-setups)

## Fields

The complete list of fields available to place in a preferences file. These fields help the program determine where files are located and where to store backups.

### Required

Without these required fields, the program would not run.

- `originalPath=` - The original path, where the source files are located.
- `backupPath=` - The destination path, where the backup is stored.
- `indexPath=` - The path to the directory containing the index file for a particular backup.

*Note: It is encouraged to provide full directory paths for these fields.*

### Optional

These are optional fields that are not required for the program to run.

- `name=` - User provided name for the backup.
- `description=` - User provided description.

## Example `preferences.txt` File

### Bare Minimum

If only one backup setup is required, the below example should be everything needed in the preferences file.

```
# minimum required fields
originalPath=/home/Work Files
backupPath=/mnt/Work Drive/Work Files Backup
indexPath=/home/Work Files
```

### Multiple Backup Setups

If multiple backup setups are required, this example shows how to setup the preferences file. If multiple setups are being used, it is recommended to use the `name=` field. This will help distinguish between backups.

```
# multiple backups fields

# work backup
name=Work Files Backup
description=Backup for all work related files.
originalPath=/home/Work Files
backupPath=/mnt/Work Drive/Work Files Backup
indexPath=/home/Work Files
=
# personal photos backup
name=Photography Backup
description=Backup for all personal photos.
originalPath=/home/Photography/Photos
backupPath=/mnt/Photography USB/Photos Backup
indexPath=/mnt/Photography USB/Photos Backup
```
