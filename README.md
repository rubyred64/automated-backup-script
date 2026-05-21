Automated Backup Script
=======================

A Python command-line backup utility that copies a user-selected source directory into a timestamped backup folder.

The program asks for a source directory, creates a backup inside a local backups folder, preserves the source folder structure, skips symlinks, records copy errors, and writes a backup log inside each backup folder.

Features
--------

- Prompts the user for a source directory
- Creates a local backups folder automatically
- Creates a timestamped backup folder for each run
- Copies files and folders recursively
- Preserves the original folder structure
- Copies hidden files
- Skips symlinked files and directories
- Prevents backing up the program's own backups folder
- Records copied files, created folders, skipped files, errors, and total copied size
- Stores backup_log.txt inside each timestamped backup folder
- Uses a temporary working folder before moving the completed backup into place

Requirements
------------

- Python 3

No external Python packages are required.

Project Structure
-----------------

    automated-backup-script/
    ├── backup.py
    ├── README.md
    ├── .gitignore
    ├── example-output.txt
    ├── backup_log_example.txt
    └── backups/
        └── backup_YYYY-MM-DD_HHMMSS/
            ├── backup_log.txt
            └── backup/
                └── copied source contents

Usage
-----

Run the program from the project folder:

    python3 backup.py

The program will ask:

    Enter source directory to back up:

Enter the full path of the folder you want to back up.

Example WSL path:

    /home/rubyred/back-it-toolkit/code-backup

Example Windows folder from WSL:

    /mnt/c/Users/YourName/Documents/MyFolder

Each run creates a new timestamped backup folder:

    backups/backup_YYYY-MM-DD_HHMMSS/

Inside that folder:

    backup_log.txt

contains the backup report, and:

    backup/

contains the copied source files.

Backup Layout
-------------

Each backup is stored like this:

    backups/
    └── backup_2026-05-08_153000/
        ├── backup_log.txt
        └── backup/
            ├── file1.txt
            ├── file2.py
            └── subfolder/
                └── nested_file.txt

Error Handling
--------------

If the source path does not exist, the program prints an error and exits.

If the source path is not a directory, the program prints an error and exits.

If the source path is inside the program's backups folder, the program prints an error and exits to prevent recursive backups.

If a backups folder is found while copying another source directory, that folder is skipped and recorded in backup_log.txt.

If a file cannot be copied because of permission issues or another copy error, the program records the error in backup_log.txt and continues copying the remaining files.

Symlinks are skipped and recorded in the backup log.

Generated Backups
-----------------

Generated backup folders are stored inside:

    backups/

The repository includes an example terminal output file:

    example-output.txt

The repository also includes an example backup log:

    backup_log_example.txt

Generated backup folders should not be committed to GitHub.

Notes
-----

The program creates backups beside backup.py inside the local backups folder.

The program does not ask for a backup destination. This keeps backup output predictable and prevents backups from being scattered across the system.

The program uses a temporary working folder while copying. The completed backup is moved into the backups folder only after the copy process and backup log are finished.

Future Improvements
-------------------

- Add command-line arguments
- Add dry-run mode
- Add optional compression into .zip files
- Add backup size warnings
- Add restore functionality
- Add file hashing to verify copied files
- Add automatic cleanup for old backups
