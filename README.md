# cFos SolarAssistant Meterdateien

Meterdateien für cFos Power Brain / cFos Wallboxen, um Werte direkt per IP aus SolarAssistant auszulesen.

Offizielle Projekte:

- SolarAssistant: <https://solar-assistant.io/>
- cFos eMobility / cFos Power Brain: <https://www.cfos-emobility.de/>

Dieses Projekt ist nicht offiziell mit SolarAssistant oder cFos eMobility verbunden.

Die Dateien nutzen die SolarAssistant HTTP-API:

- `total/grid_power`
- `total/pv_power`
- `total/battery_power`
- `total/battery_state_of_charge`
- `total/load_power`
- Energiezähler unter `total/*_energy*`
- Netz- und AC-Ausgangsfrequenz
- Dreiphasige Spannungs- und Leistungswerte von `inverter_1`
- Batteriespannung und Batteriestrom
- PV-Spannung und PV-Strom je MPPT von `inverter_1`

## Enthaltene Meter

| Datei | cFos-Typ | SolarAssistant Topic | Zweck |
| --- | --- | --- | --- |
| `meters/meter_solarassistant_grid.json` | Netz | Leistung, Energie, Frequenz, Spannung und Leistung je Phase | Netzbezug / Einspeisung |
| `meters/meter_solarassistant_pv.json` | Erzeugung | Leistung, Energie, Spannung und Strom je MPPT | PV-Erzeugung |
| `meters/meter_solarassistant_battery.json` | Batterie | Leistung, Energie, SoC, Spannung und Strom | Batteriespeicher |
| `meters/meter_solarassistant_load.json` | Verbrauch | Leistung, Energie, Frequenz, Spannung und Leistung je Phase | Hausverbrauch, hauptsächlich Anzeige |

Beim Batterie-Meter wird zusätzlich zur Leistung auch der Batterieladestand (`SoC`) übertragen.

Die Energieangaben von SolarAssistant werden von kWh in die von cFos erwarteten Wh
umgerechnet. Beim Netz- und Load-Meter berechnet cFos die Phasenströme aus den
jeweiligen Phasenspannungen und Phasenleistungen. Dadurch werden keine lediglich
aus der Gesamtleistung geschätzten Ströme verwendet.

## Voraussetzungen für die erweiterten Werte

Die Leistungs- und Energiewerte unter `total/*` sind anlagenübergreifend. Die
Phasen- und MPPT-Werte verwenden Topics von `inverter_1` und benötigen einen
SolarAssistant-kompatiblen dreiphasigen Wechselrichter, der diese Topics liefert,
z. B. einen dreiphasigen Deye/SunSynk/Sol-Ark. Vor dem Einsatz kann die Verfügbarkeit
mit der SolarAssistant REST API geprüft werden:

```text
GET /api/v1/metrics
```

Fehlen die verwendeten `inverter_1/*`-Topics, sollten die betreffenden Felder aus
der lokalen Meterdatei entfernt oder ein gerätespezifisches Profil erstellt werden.

## Optionaler lokaler Cache für schnelle Regelzyklen

cFos führt bei HTTP-Metern für jedes Feld eine eigene Anfrage aus. Bei den
erweiterten Profilen kann das den Regelzyklus deutlich verlängern. Für einen
externen Linux-Charging-Manager enthält `proxy/` deshalb einen kleinen lokalen
Cache. Er lädt den vollständigen SolarAssistant-Snapshot höchstens einmal pro
Sekunde und beantwortet die einzelnen cFos-Anfragen anschließend lokal.

Installation in Kurzform:

1. `solarassistant_metrics_proxy.py` nach `/opt/cfos-solarassistant-proxy/` kopieren.
2. Die Beispielkonfiguration nach `/etc/cfos-solarassistant-proxy.conf` kopieren,
   Zugangsdaten eintragen und mit restriktiven Dateirechten schützen.
3. `cfos-solarassistant-proxy.service` als Systemd-Dienst installieren.
4. Optional `cfos-charging-manager-proxy.conf` als Systemd-Drop-in des Charging
   Managers installieren.
5. Als Adresse der SolarAssistant-Meter `http://127.0.0.1:9180` verwenden.

Der Proxy lauscht standardmäßig ausschließlich auf Loopback. Bei einem kurzen
SolarAssistant-Ausfall liefert er höchstens 5 Sekunden alte Werte; danach antwortet
er mit HTTP 503, damit cFos den Kommunikationsfehler und seinen Failsafe erkennt.

## Wichtiger Hinweis zum Load-Meter

Der Load-Meter ist normalerweise nur zur Anzeige gedacht. Die cFos Wallbox berechnet den relevanten Verbrauch für das Überschussladen selbst aus den Meterdaten.

Den Load-Meter sollte man nicht als Regelungsgrundlage verwenden, außer die Wallbox ist elektrisch vor dem Deye und vor den CTs angeschlossen. In diesem Sonderfall wird der Verbrauch der Wallbox sonst nicht automatisch aus den Meterdaten herausgerechnet.

Kurzfassung:

- Normale Installation: Load nur anzeigen.
- Wallbox vor Deye und vor CTs: Load kann relevant sein, weil die Wallbox-Leistung sonst nicht sauber herausgerechnet wird.

## Verwendung

1. SolarAssistant muss im Netzwerk per IP erreichbar sein.
2. Die passende Meterdatei in cFos als benutzerdefinierten HTTP-Meter verwenden.
3. In der cFos-Konfiguration als Adresse/Host die IP oder den Hostnamen von SolarAssistant eintragen.
   Beispiel:

   ```text
   http://admin:*PASSWORD*@*IP/HOSTNAME*
   ```

4. Die Werte prüfen, bevor damit Ladelogik gesteuert wird.

Die `address`-Felder in den JSON-Dateien enthalten nur den API-Pfad, z. B.:

```text
/api/v1/metrics?topic=total/grid_power&value=1
```

Host/IP und Zugangsdaten kommen aus der cFos-Meterkonfiguration.

## Dateien

```text
meters/
  meter_solarassistant_battery.json
  meter_solarassistant_grid.json
  meter_solarassistant_load.json
  meter_solarassistant_pv.json
proxy/
  solarassistant_metrics_proxy.py
  solarassistant-proxy.conf.example
  cfos-solarassistant-proxy.service
  cfos-charging-manager-proxy.conf
```

## Lizenz

MIT License, siehe `LICENSE`.

## English

Meter definition files for cFos Power Brain / cFos Wallbox devices to read values directly from SolarAssistant via IP.

Official projects:

- SolarAssistant: <https://solar-assistant.io/>
- cFos eMobility / cFos Power Brain: <https://www.cfos-emobility.de/>

This project is not affiliated with SolarAssistant or cFos eMobility.

The files use the SolarAssistant HTTP API:

- `total/grid_power`
- `total/pv_power`
- `total/battery_power`
- `total/battery_state_of_charge`
- `total/load_power`
- Energy totals below `total/*_energy*`
- Grid and AC output frequency
- Three-phase voltage and power values from `inverter_1`
- Battery voltage and current
- PV voltage and current per MPPT from `inverter_1`

## Included Meters

| File | cFos type | SolarAssistant topic | Purpose |
| --- | --- | --- | --- |
| `meters/meter_solarassistant_grid.json` | Grid | Power, energy, frequency, voltage and power per phase | Grid import / export |
| `meters/meter_solarassistant_pv.json` | Generation | Power, energy, voltage and current per MPPT | PV generation |
| `meters/meter_solarassistant_battery.json` | Battery | Power, energy, SoC, voltage and current | Battery storage |
| `meters/meter_solarassistant_load.json` | Consumption | Power, energy, frequency, voltage and power per phase | House load, mainly for display |

The battery meter also transmits the battery state of charge (`SoC`) in addition to battery power.

SolarAssistant energy values are converted from kWh to Wh as required by cFos.
For the grid and load meters, cFos derives phase currents from the corresponding
phase voltages and phase powers. This avoids currents estimated only from total
power.

## Requirements for extended values

Power and energy values below `total/*` are installation independent. Phase and
MPPT values use `inverter_1` topics and require a SolarAssistant-compatible
three-phase inverter that publishes these topics, for example a three-phase
Deye/SunSynk/Sol-Ark. Check topic availability through the SolarAssistant REST API:

```text
GET /api/v1/metrics
```

If the referenced `inverter_1/*` topics are missing, remove those fields from the
local meter file or create a device-specific profile.

## Optional local cache for fast control cycles

cFos performs a separate HTTP request for every meter field. With the extended
profiles, this can significantly increase the control cycle time. For an external
Linux Charging Manager, `proxy/` therefore includes a small local cache. It loads
the complete SolarAssistant snapshot at most once per second and serves the
individual cFos requests locally.

Installation outline:

1. Copy `solarassistant_metrics_proxy.py` to `/opt/cfos-solarassistant-proxy/`.
2. Copy the example configuration to `/etc/cfos-solarassistant-proxy.conf`, enter
   the credentials and protect it with restrictive file permissions.
3. Install `cfos-solarassistant-proxy.service` as a systemd service.
4. Optionally install `cfos-charging-manager-proxy.conf` as a systemd drop-in for
   the Charging Manager.
5. Use `http://127.0.0.1:9180` as the address of each SolarAssistant meter.

The proxy listens on loopback only by default. During a short SolarAssistant
outage it serves values that are no more than 5 seconds old; after that it returns
HTTP 503 so cFos can detect the communication error and engage its failsafe.

## Important Note About the Load Meter

The load meter is normally meant for display only. The cFos Wallbox calculates the relevant consumption for surplus charging from the meter data itself.

Do not use the load meter as a control basis unless the wallbox is electrically installed before the Deye inverter and before the CTs. In that special case, the wallbox consumption is otherwise not automatically deducted from the meter data.

Short version:

- Normal installation: use Load for display only.
- Wallbox before Deye and before CTs: Load can be relevant because the wallbox power is otherwise not cleanly subtracted.

## Usage

1. SolarAssistant must be reachable in the network via IP.
2. Use the matching meter file in cFos as a custom HTTP meter.
3. In the cFos configuration, enter the IP or hostname of SolarAssistant as address/host.
   Example:

   ```text
   http://admin:*PASSWORD*@*IP/HOSTNAME*
   ```

4. Check the values before using them for charging logic.

The `address` fields in the JSON files only contain the API path, for example:

```text
/api/v1/metrics?topic=total/grid_power&value=1
```

Host/IP and credentials come from the cFos meter configuration.

## License

MIT License, see `LICENSE`.
