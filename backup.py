import os
import shutil
import datetime
import sys
import tempfile


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUPS_DIR = os.path.join(SCRIPT_DIR, "backups")


def get_size_mb(size_bytes):
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def normalize_path(path):
    return os.path.abspath(os.path.expanduser(path))


def is_inside_directory(path, directory):
    path = normalize_path(path)
    directory = normalize_path(directory)

    try:
        common_path = os.path.commonpath([path, directory])
        return common_path == directory
    except ValueError:
        return False


def should_skip_path(path):
    path = normalize_path(path)

    if is_inside_directory(path, BACKUPS_DIR):
        return True

    return False


def backup_directory(source, backup_content_dir):
    copied_files = []
    created_folders = []
    skipped_files = []
    errors = []
    total_size = 0

    source = normalize_path(source)
    backup_content_dir = normalize_path(backup_content_dir)

    for root, dirs, files in os.walk(source, topdown=True):
        original_dirs = list(dirs)
        dirs.clear()

        for dir_name in original_dirs:
            src_dir = os.path.join(root, dir_name)
            rel_dir = os.path.relpath(src_dir, source)

            if should_skip_path(src_dir):
                skipped_files.append(f"Skipped backup directory: {rel_dir}")
                continue

            if os.path.islink(src_dir):
                skipped_files.append(f"Skipped symlink directory: {rel_dir}")
                continue

            dirs.append(dir_name)

            dst_dir = os.path.join(backup_content_dir, rel_dir)

            try:
                os.makedirs(dst_dir, exist_ok=True)
                created_folders.append(rel_dir)
            except Exception as error:
                errors.append(f"Failed to create directory {rel_dir}: {error}")

        for file_name in files:
            src_file = os.path.join(root, file_name)
            rel_file = os.path.relpath(src_file, source)

            if should_skip_path(src_file):
                skipped_files.append(f"Skipped backup file: {rel_file}")
                continue

            if os.path.islink(src_file):
                skipped_files.append(f"Skipped symlink file: {rel_file}")
                continue

            dst_file = os.path.join(backup_content_dir, rel_file)

            try:
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)
                copied_files.append(rel_file)
                total_size += os.path.getsize(src_file)
            except Exception as error:
                errors.append(f"Failed to copy {rel_file}: {error}")

    return copied_files, created_folders, skipped_files, errors, total_size


def write_backup_log(
    log_path,
    source,
    final_backup_dir,
    backup_content_dir,
    start_time,
    end_time,
    copied_files,
    created_folders,
    skipped_files,
    errors,
    total_size
):
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write("Backup Log\n")
        log_file.write("==========\n\n")

        log_file.write(f"Started At: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Finished At: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        log_file.write("Source Directory:\n")
        log_file.write(f"{source}\n\n")

        log_file.write("Backup Folder:\n")
        log_file.write(f"{final_backup_dir}\n\n")

        log_file.write("Copied Files Folder:\n")
        log_file.write(f"{backup_content_dir}\n\n")

        log_file.write("Summary\n")
        log_file.write("-------\n")
        log_file.write(f"Files Copied: {len(copied_files)}\n")
        log_file.write(f"Folders Created: {len(created_folders)}\n")
        log_file.write(f"Files Skipped: {len(skipped_files)}\n")
        log_file.write(f"Errors: {len(errors)}\n")
        log_file.write(f"Total Size Copied: {get_size_mb(total_size)}\n\n")

        if copied_files:
            log_file.write("Copied Files\n")
            log_file.write("------------\n")
            for file_path in copied_files:
                log_file.write(f"{file_path}\n")
            log_file.write("\n")

        if created_folders:
            log_file.write("Created Folders\n")
            log_file.write("---------------\n")
            for folder_path in created_folders:
                log_file.write(f"{folder_path}\n")
            log_file.write("\n")

        if skipped_files:
            log_file.write("Skipped Files\n")
            log_file.write("-------------\n")
            for skipped_file in skipped_files:
                log_file.write(f"{skipped_file}\n")
            log_file.write("\n")

        if errors:
            log_file.write("Errors\n")
            log_file.write("------\n")
            for error in errors:
                log_file.write(f"{error}\n")


def print_summary(
    source,
    final_backup_dir,
    final_backup_content_dir,
    final_log_path,
    copied_files,
    created_folders,
    skipped_files,
    errors,
    total_size
):
    if errors:
        print("\nBackup completed with errors.\n")
    else:
        print("\nBackup completed.\n")

    print(f"Source: {source}")
    print(f"Backup Folder: {final_backup_dir}")
    print(f"Copied Files: {final_backup_content_dir}\n")

    print(f"Files Copied: {len(copied_files)}")
    print(f"Folders Created: {len(created_folders)}")
    print(f"Files Skipped: {len(skipped_files)}")
    print(f"Errors: {len(errors)}")
    print(f"Total Size Copied: {get_size_mb(total_size)}\n")

    print(f"Log saved to: {final_log_path}")


def main():
    source = input("Enter source directory to back up: ").strip()
    source = normalize_path(source)

    if not os.path.exists(source):
        print(f"Error: Source directory '{source}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(source):
        print(f"Error: '{source}' is not a directory.")
        sys.exit(1)

    if is_inside_directory(source, BACKUPS_DIR):
        print("Error: Do not back up a folder inside the backups directory.")
        sys.exit(1)

    os.makedirs(BACKUPS_DIR, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_folder_name = f"backup_{timestamp}"

    final_backup_dir = normalize_path(os.path.join(BACKUPS_DIR, backup_folder_name))
    final_backup_content_dir = os.path.join(final_backup_dir, "backup")
    final_log_path = os.path.join(final_backup_dir, "backup_log.txt")

    temporary_parent = tempfile.mkdtemp(prefix="backup_work_")
    temporary_backup_dir = os.path.join(temporary_parent, backup_folder_name)
    temporary_backup_content_dir = os.path.join(temporary_backup_dir, "backup")
    temporary_log_path = os.path.join(temporary_backup_dir, "backup_log.txt")

    start_time = datetime.datetime.now()

    try:
        os.makedirs(temporary_backup_content_dir, exist_ok=True)

        copied_files, created_folders, skipped_files, errors, total_size = backup_directory(
            source,
            temporary_backup_content_dir
        )

        end_time = datetime.datetime.now()

        write_backup_log(
            temporary_log_path,
            source,
            final_backup_dir,
            final_backup_content_dir,
            start_time,
            end_time,
            copied_files,
            created_folders,
            skipped_files,
            errors,
            total_size
        )

        shutil.move(temporary_backup_dir, final_backup_dir)

        print_summary(
            source,
            final_backup_dir,
            final_backup_content_dir,
            final_log_path,
            copied_files,
            created_folders,
            skipped_files,
            errors,
            total_size
        )

    finally:
        if os.path.exists(temporary_parent):
            shutil.rmtree(temporary_parent, ignore_errors=True)


if __name__ == "__main__":
    main()