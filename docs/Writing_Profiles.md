# Writing Profiles

The `profiles.txt` is central to setting up and conducting different/separate backups. Without it, the program would not function.

The profile file should be listed in the preferences file. 

## Comments

Comments are allowed in the profile file.

```
# Any line that begins with a '#' will be ignored
# Block comments are not currently supported
...
```

## Separating Profiles

If multiple backup setups are required, the profiles should be separated with a `=`.

```
# backup a
...
=
# backup b
...
```

See [Multiple Setups Example](#multiple-backup-setups)

## Fields

The complete list of fields available to place in a profile. These fields help the program determine where files are located and where to store backups, along with other important metadata.

### Required

Without these required fields, the program will not execute.

- `name=` - User provided name for the backup.
- `originalPath=` - The original path, where the source files are located.
- `backupPath=` - The destination path, where the backup is stored.
- `indexPath=` - The path to the directory containing the index file for a particular backup.

*Note: It is encouraged to provide full directory paths for these fields.*

### Optional

These are optional fields that are not required for the program to run.

- `description=` - User provided description. Helpful if more than one profile has the same name.
- `blacklist=` - Child directories of the source directory to avoid backing up.

## Example `profiles.txt` File

### Bare Minimum

If only one backup setup is required, the below example should be everything needed in the profile file.

```
# minimum required fields
name=Work Backup
originalPath=/home/Work Files
backupPath=/mnt/Work Drive/Work Files Backup
indexPath=/home/Work Files
```

### Multiple Backup Setups

If multiple backup setups are required, this example shows how to setup the profile file. If multiple setups are being used, it is recommended to use the `description=` field. This will help distinguish between backups.

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

### Blacklist

Sometimes child directories may not need to be included in the backup. Placing these directories in the blacklist will ensure they are skipped.

In the below example, the original path is `/home/Photos`. Looking at the blacklist, the child paths `/home/Photos/Private` and `/home/Photos/Cats` will be skipped, and not backed up. This is a list of directories, separated by a comma, with no additional spaces (unless the directory name contains spaces).

```
name=Personal Photos
originalPath=/home/Photos
backupPath=/mnt/USB Drive/Photos Backup
indexPath=/home/Photos
blacklist=Private,Cats
```

*Note: Files placed in the blacklist will not be handled properly and may cause errors.*
