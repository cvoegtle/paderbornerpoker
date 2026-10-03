# Effort Poker
[Effort Poker](https://effortpoker.ew.r.appspot.com/) ist eine online Version des Planning Pokers während eines Clarification Meetings.
Die Anzahl Teilnehmer ist nur durch die Kapazität des Servers begrenzt. Diese lässt sich
erhöhen indem die automatische Aktualisierung ausgeschaltet wird.

## Vorbereitung & Virtual Environment
```bash
python3.12 -m venv env
source env/bin/activate
pip install -r planningpoker/requirements.txt
```

## Tests ausführen
```bash
python -m unittest discover -s planningpoker -p "*_test.py"
```

## lokal testen
Diesen Befehl auf der Shell ausführen, um den Datastore der Google Cloud zu emulieren:
```bash
gcloud beta emulators datastore start
```

Im IntelliJ eine Run Configuration für `planningpoker/main.py` anlegen. Dort folgende Umgebungsvariable setzen:
```
DATASTORE_EMULATOR_HOST=localhost:8081
```

## auf die Appengine deployen
Dieses Skript ausführen:
```bash
planningpoker/deploy2appengine.sh
```



