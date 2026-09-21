# B01-A – Zielplattform und read-only Preflight

**Status:** implementiert, physische Zweitgeräte-Prüfung noch OPEN  
**Bezug:** REQ-001, REQ-003, REQ-004; AQ-010, AQ-013, AQ-020

## Scope

B01-A legt den ersten reproduzierbaren Start-/Preflight-Pfad fest. Er prüft ausschließlich lokale Plattform- und Runtime-Fakten.

## Initiale Plattform-Baseline

Für den ersten Implementierungsstand wird konservativ nur folgende Familie freigegeben:

- Ubuntu 24.04 LTS
- Kubuntu 24.04 LTS
- Linux
- Python >= 3.10

Patchstände innerhalb 24.04 werden als dieselbe LTS-Familie behandelt.

Andere Distributionen oder Versionen werden **nicht abgelehnt oder verändert**, sondern mit Status `OPEN` gemeldet. Insbesondere Ubuntu/Kubuntu 26.04 wird erst nach realer Prüfung freigegeben.

## Noch offen

Die ursprüngliche Anforderung nennt zwei reale Zielgeräte, deren konkrete Betriebssystemstände im Repository nicht vollständig belegt sind. Deshalb bleibt die **physische Zweitgeräte-Abnahme OPEN**, bis deren Preflight-Ausgabe als Evidence vorliegt.

## Sicherheitsvertrag

Der B01-A-Preflight darf:

- `/etc/os-release` lesen;
- Python-/Kernel-/Architekturinformationen lesen;
- Desktop-Umgebungsvariablen lesen;
- Ergebnis auf stdout/stderr ausgeben.

Er darf nicht:

- Dateien des Nutzers verändern;
- Pakete installieren;
- Netzwerkzugriffe ausführen;
- `sudo` oder andere Rechteausweitung verwenden;
- Konfiguration migrieren;
- fehlende Abhängigkeiten automatisch nachladen.

## Start

```bash
python3 start.py
```

Maschinenlesbar:

```bash
python3 start.py --json
```

Statuscodes:

- `0`: freigegebene Plattformfamilie erkannt;
- `3`: Voraussetzungen oder Plattform noch OPEN;
- `2`: ungültige Option.

## B01-Grenze

Dieser Block implementiert noch **kein Pfad-/Symlink-Sicherheitsmodell**. Das folgt separat als B01-B, bevor Dateiinventar oder Dateioperationen entstehen.
