#! /bin/bash

DIR="venv"

print_string() {
    local input="$1"
    echo ""
    echo "-------------------------------------------------------------------"
    echo "$input"
    echo ""
    
}

print_string "Prüfe ob altes virtuelles Enviroment 'venv' noch vorhanden ist ..."

if [ -d "$DIR" ]; then
    echo "  Verzeichnis $DIR existiert. Lösche..."
    rm -rf "$DIR"
    echo "  Löschen abgeschlossen."
else
    echo "  Verzeichnis $DIR existiert nicht. Keine weitere Aktion nötig"
fi

print_string "Erstelle neues virtuelles Enviroment 'venv' ..."

python3 -m venv "$DIR"

if [ -d "$DIR" ]; then
    echo "  Virtuelles Enviroment '$DIR' erfolgreich erstellt"
else
    echo "  Virtuelles Enviroment '$DIR' konnte nicht erstellt werden"
    exit
fi

print_string "Aktiviere virtuelles Enviroment '$DIR' ..."
source "$DIR"/bin/activate
echo "  Virtuelles Enviroment erfolgreich aktiviert"

print_string "Installiere benötigete Pakete aus tests_requirements.txt"
pip install -r tests_requirements.txt
echo "  Alle Pakete installiert"

print_string "Starte Tests ..."
python3 -m pytest
echo "  Tests beendet"

print_string "Deaktiviere virtuelles Enviroment"
deactivate
echo "  Virutelles Enviroment erfolgreich deaktiviert"

print_string "Enferne virtuelles Enviroment ..."
if [ -d "$DIR" ]; then
    echo "  Verzeichnis $DIR existiert. Lösche..."
    rm -rf "$DIR"
    echo "  Löschen abgeschlossen."
else
    echo "  Verzeichnis $DIR existiert nicht."
fi

print_string "run_tests.sh abgeschlossen"