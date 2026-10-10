#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_BIN="$APP_ROOT/dist/EduRate"
APP_ICON="$APP_ROOT/assets/logo.png"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
# Reuse the previous desktop-file ID so pinned Ubuntu favorites also launch
# this build instead of the obsolete ProfessorEvaluation executable.
DESKTOP_FILE="$DESKTOP_DIR/professorevaluation.desktop"
OLD_DESKTOP_FILE="$DESKTOP_DIR/professor-evaluation.desktop"

if [[ ! -x "$APP_BIN" ]]; then
    echo "Exécutable introuvable : $APP_BIN" >&2
    exit 1
fi
mkdir -p "$DESKTOP_DIR"
# Replace the old launcher even if another installer created it with
# read-only permissions; directory ownership allows replacing the entry.
rm -f "$DESKTOP_FILE"
cat > "$DESKTOP_FILE" <<DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=EduRate
Comment=Évaluation académique des professeurs
Exec="$APP_BIN"
Icon=$APP_ICON
Terminal=false
Categories=Education;
StartupNotify=true
StartupWMClass=EduRate
DESKTOP
chmod 644 "$DESKTOP_FILE"
rm -f "$OLD_DESKTOP_FILE"
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi
printf 'Lanceur installé : %s\n' "$DESKTOP_FILE"
