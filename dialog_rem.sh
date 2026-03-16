#!/bin/sh

set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

replace_file() {
    file_path=$1
    tmp_path="${file_path}.tmp"
    cat > "$tmp_path"
    mv "$tmp_path" "$file_path"
}

remove_dependency() {
    file_path="$ROOT_DIR/pyproject.toml"
    awk '!/"aiogram-dialog>=2\.5\.0",/' "$file_path" | replace_file "$file_path"
}

remove_logger() {
    file_path="$ROOT_DIR/app/logging_setup.py"
    awk '{
        gsub(/, "aiogram_dialog"/, "")
        print
    }' "$file_path" | replace_file "$file_path"
}

remove_startup_setup() {
    file_path="$ROOT_DIR/app/main.py"
    awk '
        /from aiogram_dialog import setup_dialogs/ { next }
        /setup_dialogs\(dp\)/ { next }
        { if (!skip) print }
    ' "$file_path" | replace_file "$file_path"
}

remove_dialog_files() {
    rm -rf "$ROOT_DIR/app/presentation/dialogs"
}

update_readme() {
    file_path="$ROOT_DIR/README.md"
    awk '
        /Если `aiogram-dialog` не нужен, просто запусти:/ {
            print "Если `aiogram-dialog` не нужен, просто запусти `./dialog_rem.sh`."
            skip=1
            next
        }
        skip && /^## / { skip=0; print; next }
        !skip { print }
    ' "$file_path" | replace_file "$file_path"
}

remove_dependency
remove_logger
remove_startup_setup
remove_dialog_files
update_readme

echo "aiogram-dialog dependency, startup integration and dialog files removed."
