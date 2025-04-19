#! /bin/bash

DIR="venv"

if [ -d "$DIR" ]; then
    echo "Verzeichnis $DIR existiert. Lösche..."
    rm -rf "$DIR"
    echo "Löschen abgeschlossen."
else
    echo "Verzeichnis $DIR existiert nicht."
fi

echo "Erstelle neues virtuelles Enviroment 'venv' ..."

python3 -m venv "$DIR"

if [ -d "$DIR" ]; then
    echo "Virtuelles Enviroment '$DIR' erfolgreich erstellt"
else
    echo "Virtuelles Enviroment '$DIR' konnte nicht erstellt werden"
    exit
fi

source "$DIR"/bin/activate

pip install --upgrade build wheel

python3 -m build

deactivate

rm -rf "$DIR"