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

## Enthaltene Meter

| Datei | cFos-Typ | SolarAssistant Topic | Zweck |
| --- | --- | --- | --- |
| `meters/meter_solarassistant_grid.json` | Netz | `total/grid_power` | Netzbezug / Einspeisung |
| `meters/meter_solarassistant_pv.json` | Erzeugung | `total/pv_power` | PV-Leistung |
| `meters/meter_solarassistant_battery.json` | Batterie | `total/battery_power`, `total/battery_state_of_charge` | Batterie-Leistung und SoC |
| `meters/meter_solarassistant_load.json` | Verbrauch | `total/load_power` | Hausverbrauch, hauptsächlich Anzeige |

Beim Batterie-Meter wird zusätzlich zur Leistung auch der Batterieladestand (`SoC`) übertragen.

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

## Included Meters

| File | cFos type | SolarAssistant topic | Purpose |
| --- | --- | --- | --- |
| `meters/meter_solarassistant_grid.json` | Grid | `total/grid_power` | Grid import / export |
| `meters/meter_solarassistant_pv.json` | Generation | `total/pv_power` | PV power |
| `meters/meter_solarassistant_battery.json` | Battery | `total/battery_power`, `total/battery_state_of_charge` | Battery power and SoC |
| `meters/meter_solarassistant_load.json` | Consumption | `total/load_power` | House load, mainly for display |

The battery meter also transmits the battery state of charge (`SoC`) in addition to battery power.

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
