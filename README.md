# Effort Poker
[Effort Poker](https://effortpoker.ew.r.appspot.com/) ist eine online Version des Planning Pokers während eines Clarification Meetings.
Die Anzahl Teilnehmer ist nur durch die Kapazität des Servers begrenzt. Diese lässt sich
erhöhen indem die automatische Aktualisierung ausgeschaltet wird

## lokal testen
diesen Befehl auf der Shell ausführen, um den Datastore der Google Cloud zu emulieren 
gcloud beta emulators datastore start

im IntelliJ eine Run Configuration für main.py anlegen. Dort folgende Umgebungsvariable setzen:
DATASTORE_EMULATOR_HOST=localhost:8081

## auf die Appengine deployen
dieses Skript ausführe:
planningpoker/deploy2appengine.sh


