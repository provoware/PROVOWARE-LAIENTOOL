# I34 – Plugin-Grenze

## Status

**Stabile Daten-/Capability-Grenze implementiert. Plugin-Runtime bleibt vollständig gesperrt.**

## Ziel

B09 wird so weit wie sinnvoll automatisiert, ohne ausführbare Drittanbieterlogik zu laden.

## Manifest-Vertrag

Ein zukünftiges Plugin darf in I34 nur Metadaten deklarieren:

- Plugin-ID;
- Anzeigename;
- Version;
- Plugin-API-Version;
- gewünschte bestehende PROVOWARE-Use-Cases.

Zusätzlich gilt:

- Status ausschließlich `DISABLED`;
- `auto_install=False`;
- `auto_enable=False`;
- `network_required=False`;
- `entrypoint=None`.

## Capability-Grenze

Genehmigungsfähig sind ausschließlich Use-Cases, die in der gemeinsamen Registry gleichzeitig `READY` und `read-only` sind.

OPEN-, Preview-/Write- oder unbekannte Use-Cases werden blockiert.

## Repository-Guard

`scripts/plugin_boundary_guard.py` blockiert bis zu einem expliziten späteren REOPEN:

- `importlib`-/Entry-Point-basierte dynamische Loader;
- `__import__`;
- typische Plugin-Loader-Dateien;
- `plugins/`-Runtime-Verzeichnisse;
- `requests`/`httpx` im Produktcode;
- Auto-Install-Marker.

## Sicherheitsgrenze

I34 implementiert keinen Plugin-Loader, Installer, Downloader, Plugin-Verzeichnis-Scanner, Entry-Point, Auto-Enable, Netzwerkzugriff, Plugin-Persistenz oder Sandbox.

## Folgegate

Erst ein separater späterer Decision-/Threat-Model-Block darf entscheiden, ob ausführbare Plugins benötigt werden. Bis dahin bleibt die Erweiterungsschnittstelle data-only und deaktiviert.
