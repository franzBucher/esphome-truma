#!/usr/bin/env python3
"""Applies the Timer Start/Stop text_sensor changes to esphome-truma.

Run from the repository root (the folder containing `components/`):

    python3 apply_timer_text_sensor.py

This does NOT use `git apply`/`git am` - it writes the small new/changed
source files outright and does a plain, context-free string replacement on
the four docs files. That makes it immune to line-ending / patch-context
mismatches. If a doc anchor can't be found (e.g. because the file already
differs), that one file is skipped with a warning instead of aborting -
everything else still gets applied.
"""
import pathlib
import sys

ROOT = pathlib.Path(".").resolve()
if not (ROOT / "components" / "truma_inetbox" / "version.h").exists():
    sys.exit(
        "Bitte aus dem Repo-Root ausfuehren "
        "(components/truma_inetbox/version.h wurde nicht gefunden)."
    )

TEXT_SENSOR_DIR = ROOT / "components" / "truma_inetbox" / "text_sensor"
TEXT_SENSOR_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Small files: written in full, no dependency on prior content.
# ---------------------------------------------------------------------------

FULL_FILES = {}

FULL_FILES[TEXT_SENSOR_DIR / "enum.h"] = '''#pragma once

#include "esphome/core/log.h"

namespace esphome {
namespace truma_inetbox {

enum class TRUMA_TEXT_SENSOR_TYPE {
  UNKNOWN,

  VERSION,

  TIMER_START_TIME,
  TIMER_STOP_TIME,
};

#ifdef ESPHOME_LOG_HAS_CONFIG
static const char *enum_to_c_str(const TRUMA_TEXT_SENSOR_TYPE val) {
  switch (val) {
    case TRUMA_TEXT_SENSOR_TYPE::VERSION:
      return "VERSION";
      break;
    case TRUMA_TEXT_SENSOR_TYPE::TIMER_START_TIME:
      return "TIMER_START_TIME";
      break;
    case TRUMA_TEXT_SENSOR_TYPE::TIMER_STOP_TIME:
      return "TIMER_STOP_TIME";
      break;
    default:
      return "";
      break;
  }
}
#endif  // ESPHOME_LOG_HAS_CONFIG

}  // namespace truma_inetbox
}  // namespace esphome
'''

FULL_FILES[TEXT_SENSOR_DIR / "TrumaTimerTextSensor.h"] = '''#pragma once

#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/truma_inetbox/TrumaiNetBoxApp.h"
#include "enum.h"

namespace esphome {
namespace truma_inetbox {

// Reads the current start/stop time of the CP Plus timer schedule.
//
// The values originate from the `StatusFrameTimer` message that the CP Plus
// periodically broadcasts on the LIN bus (the same message that already
// backs `TrumaTimerBinarySensor`'s `TIMER_ACTIVE` / `TIMER_ROOM` /
// `TIMER_WATER` types). No additional polling or request is necessary -
// this class only formats fields that are already being read.
class TrumaTimerTextSensor : public Component, public text_sensor::TextSensor, public Parented<TrumaiNetBoxApp> {
 public:
  void setup() override;
  void dump_config() override;

  void set_type(TRUMA_TEXT_SENSOR_TYPE val) { this->type_ = val; }

 protected:
  TRUMA_TEXT_SENSOR_TYPE type_;

 private:
};
}  // namespace truma_inetbox
}  // namespace esphome
'''

FULL_FILES[TEXT_SENSOR_DIR / "TrumaTimerTextSensor.cpp"] = '''#include "TrumaTimerTextSensor.h"
#include "esphome/core/helpers.h"
#include "esphome/core/log.h"

namespace esphome {
namespace truma_inetbox {

static const char *const TAG = "truma_inetbox.timer_text_sensor";

void TrumaTimerTextSensor::setup() {
  this->parent_->get_timer()->add_on_message_callback([this](const StatusFrameTimer *status_timer) {
    switch (this->type_) {
      case TRUMA_TEXT_SENSOR_TYPE::TIMER_START_TIME:
        this->publish_state(
            esphome::str_snprintf("%02u:%02u", 5, status_timer->timer_start_hours, status_timer->timer_start_minutes));
        break;
      case TRUMA_TEXT_SENSOR_TYPE::TIMER_STOP_TIME:
        this->publish_state(
            esphome::str_snprintf("%02u:%02u", 5, status_timer->timer_stop_hours, status_timer->timer_stop_minutes));
        break;
      default:
        break;
    }
  });
}

void TrumaTimerTextSensor::dump_config() {
  LOG_TEXT_SENSOR("", "Truma Timer Text Sensor", this);
  ESP_LOGCONFIG(TAG, "  Type '%s'", enum_to_c_str(this->type_));
}
}  // namespace truma_inetbox
}  // namespace esphome
'''

FULL_FILES[TEXT_SENSOR_DIR / "TrumaVersionTextSensor.h"] = '''#pragma once

#include "esphome/core/component.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/truma_inetbox/TrumaiNetBoxApp.h"
#include "esphome/components/truma_inetbox/version.h"

namespace esphome {
namespace truma_inetbox {

// `Parented<TrumaiNetBoxApp>` is not used by this sensor (the version string is static and
// does not depend on the LIN bus), but it is kept so that `text_sensor/__init__.py` can
// register every `truma_inetbox` text sensor type through the same generic `to_code()`
// (see `TrumaTimerTextSensor` for a type that does use the parent).
class TrumaVersionTextSensor : public Component, public text_sensor::TextSensor, public Parented<TrumaiNetBoxApp> {
 public:
  void setup() override { this->publish_state(TRUMA_INETBOX_VERSION); }
  void dump_config() override;
};

}  // namespace truma_inetbox
}  // namespace esphome
'''

FULL_FILES[TEXT_SENSOR_DIR / "__init__.py"] = '''from esphome.components import text_sensor
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import CONF_ID, CONF_TYPE, ENTITY_CATEGORY_DIAGNOSTIC
from .. import truma_inetbox_ns, CONF_TRUMA_INETBOX_ID, TrumaINetBoxApp

DEPENDENCIES = ["truma_inetbox"]
CODEOWNERS = ["@havanti"]

TrumaVersionTextSensor = truma_inetbox_ns.class_(
    "TrumaVersionTextSensor", text_sensor.TextSensor, cg.Component
)
TrumaTimerTextSensor = truma_inetbox_ns.class_(
    "TrumaTimerTextSensor", text_sensor.TextSensor, cg.Component
)

# `TRUMA_TEXT_SENSOR_TYPE` is a enum class and not a namespace but it works.
TRUMA_TEXT_SENSOR_TYPE_dummy_ns = truma_inetbox_ns.namespace(
    "TRUMA_TEXT_SENSOR_TYPE")

# 0 - C++ class
# 1 - C++ enum (`None` if the class does not need `set_type`, e.g. `VERSION`)
CONF_SUPPORTED_TYPE = {
    # TrumaVersionTextSensor
    "VERSION": (TrumaVersionTextSensor, None),
    # TrumaTimerTextSensor
    "TIMER_START_TIME": (TrumaTimerTextSensor, TRUMA_TEXT_SENSOR_TYPE_dummy_ns.TIMER_START_TIME),
    "TIMER_STOP_TIME": (TrumaTimerTextSensor, TRUMA_TEXT_SENSOR_TYPE_dummy_ns.TIMER_STOP_TIME),
}


def set_default_based_on_type():
    def set_defaults_(config):
        # Update type based on configuration
        config[CONF_ID].type = CONF_SUPPORTED_TYPE[config[CONF_TYPE]][0]
        return config

    return set_defaults_


CONFIG_SCHEMA = (
    text_sensor.text_sensor_schema(
        TrumaVersionTextSensor,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        icon="mdi:tag",
    )
    .extend(
        {
            cv.GenerateID(CONF_TRUMA_INETBOX_ID): cv.use_id(TrumaINetBoxApp),
            # `VERSION` stays the default so that existing configs written before the
            # `type` option existed (`text_sensor: - platform: truma_inetbox name: "..."`
            # with no `type:` at all) keep working unchanged.
            cv.Optional(CONF_TYPE, default="VERSION"): cv.enum(CONF_SUPPORTED_TYPE, upper=True),
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
)
FINAL_VALIDATE_SCHEMA = set_default_based_on_type()


async def to_code(config):
    var = await text_sensor.new_text_sensor(config)
    await cg.register_component(var, config)
    await cg.register_parented(var, config[CONF_TRUMA_INETBOX_ID])

    if CONF_SUPPORTED_TYPE[config[CONF_TYPE]][1]:
        cg.add(var.set_type(CONF_SUPPORTED_TYPE[config[CONF_TYPE]][1]))
'''

FULL_FILES[ROOT / "components" / "truma_inetbox" / "version.h"] = '''#pragma once

namespace esphome {
namespace truma_inetbox {

static constexpr const char *TRUMA_INETBOX_VERSION = "1.0.26";

}  // namespace truma_inetbox
}  // namespace esphome
'''

for path, content in FULL_FILES.items():
    path.write_text(content, encoding="utf-8")
    print(f"geschrieben: {path.relative_to(ROOT)}")

# ---------------------------------------------------------------------------
# 2. Doc files: context-free string replacement (anchor -> new text).
#    If an anchor isn't found, warn and skip that file instead of aborting.
# ---------------------------------------------------------------------------

DOC_REPLACEMENTS = [
    (
        ROOT / "README.md",
        '''### Text Sensor

Zeigt die installierte Komponentenversion im ESPHome-Webinterface und Home Assistant an.

```yaml
text_sensor:
  - platform: truma_inetbox
    name: "ESPHome Truma Version"
```

Standardwerte: `entity_category: diagnostic`, `icon: mdi:tag`. Keine weiteren Parameter erforderlich.''',
        '''### Text Sensor

```yaml
text_sensor:
  - platform: truma_inetbox
    name: "ESPHome Truma Version"
    type: VERSION
  - platform: truma_inetbox
    name: "Timer Start"
    type: TIMER_START_TIME
  - platform: truma_inetbox
    name: "Timer Stopp"
    type: TIMER_STOP_TIME
```

Standardwerte: `entity_category: diagnostic`, `icon: mdi:tag`. Keine weiteren Parameter erforderlich.
`type:` ist optional und ist `VERSION`, wenn weggelassen — bestehende Configs ohne `type:` funktionieren
also unverändert weiter.

Verfügbare `type`-Werte:

- `VERSION` — zeigt die installierte Komponentenversion im ESPHome-Webinterface und Home Assistant an.
- `TIMER_START_TIME` — Startzeit des aktuell auf dem CP Plus hinterlegten Timers, Format `HH:MM`
  (z. B. `07:00`).
- `TIMER_STOP_TIME` — Stoppzeit des aktuell auf dem CP Plus hinterlegten Timers, Format `HH:MM`.

`TIMER_START_TIME` und `TIMER_STOP_TIME` lesen dieselbe `StatusFrameTimer`-Nachricht, die der CP Plus
im normalen Update-Zyklus über den LIN-Bus sendet (dieselbe Nachricht, aus der auch die Binary Sensors
`TIMER_ACTIVE` / `TIMER_ROOM` / `TIMER_WATER` gespeist werden) — es wird also nichts zusätzlich
abgefragt, nur ein bereits eintreffendes Feld zusätzlich als Entität veröffentlicht. Die beiden Sensoren
aktualisieren sich damit im selben Turnus wie z. B. `CURRENT_ROOM_TEMPERATURE`.''',
    ),
    (
        ROOT / "README.en.md",
        '''### Text Sensor

Exposes the installed component version in the ESPHome web interface and Home Assistant.

```yaml
text_sensor:
  - platform: truma_inetbox
    name: "ESPHome Truma Version"
```

Defaults: `entity_category: diagnostic`, `icon: mdi:tag`. No further parameters required.''',
        '''### Text Sensor

```yaml
text_sensor:
  - platform: truma_inetbox
    name: "ESPHome Truma Version"
    type: VERSION
  - platform: truma_inetbox
    name: "Timer Start"
    type: TIMER_START_TIME
  - platform: truma_inetbox
    name: "Timer Stop"
    type: TIMER_STOP_TIME
```

Defaults: `entity_category: diagnostic`, `icon: mdi:tag`. No further parameters required.
`type:` is optional and defaults to `VERSION` when omitted, so existing configs without a `type:`
keep working unchanged.

Available `type` values:

- `VERSION` — exposes the installed component version in the ESPHome web interface and Home Assistant.
- `TIMER_START_TIME` — start time of the timer schedule currently stored on the CP Plus, formatted as
  `HH:MM` (e.g. `07:00`).
- `TIMER_STOP_TIME` — stop time of the timer schedule currently stored on the CP Plus, formatted as
  `HH:MM`.

`TIMER_START_TIME` and `TIMER_STOP_TIME` read the same `StatusFrameTimer` message the CP Plus already
sends over the LIN bus as part of its normal update cycle (the same message that also feeds the
`TIMER_ACTIVE` / `TIMER_ROOM` / `TIMER_WATER` binary sensors) — nothing extra is requested from the
device, an already-arriving field is simply exposed as its own entity as well. Both sensors therefore
refresh on the same cadence as, for example, `CURRENT_ROOM_TEMPERATURE`.''',
    ),
    (
        ROOT / "CHANGELOG.md",
        '''## Kompatibilitätsstatus

### Zusammenfassung

Dieses Release ändert nur die Beispielkonfigurationen: Der Sensor „Operating Status" hat
jetzt eine `id` und lässt sich damit in Lambdas auswerten, etwa um zu erkennen, ob der
Brenner gerade läuft. Am Code der Komponenten hat sich nichts geändert.

Getestet mit:
- ESPHome **2026.8.2** — ESP-IDF ✅
- ESPHome **2026.6.5** — ESP-IDF ✅
- ESPHome **2026.6.4** — ESP-IDF ✅

---


## [1.0.25] — 2026-09-07 — Beispiel-YAMLs: `id` für Operating Status''',
        '''## Kompatibilitätsstatus

### Zusammenfassung

Dieses Release fügt zwei neue `text_sensor`-Typen hinzu (`TIMER_START_TIME` / `TIMER_STOP_TIME`),
die die vom CP Plus bereits über den LIN-Bus gelieferten Timer-Start-/Stoppzeiten als eigene
Home-Assistant-Entität verfügbar machen. Bestehende `text_sensor`-Configs ohne `type:` sind davon
nicht betroffen (Default bleibt `VERSION`).

⚠️ Diese Änderung wurde noch nicht auf echter Hardware getestet (weder kompiliert noch gegen ein
CP Plus verifiziert) — vor dem produktiven Einsatz bitte selbst mit `esphome compile`/`esphome run`
gegenprüfen.

Zuletzt auf Hardware getestet (Stand 1.0.25):
- ESPHome **2026.8.2** — ESP-IDF ✅
- ESPHome **2026.6.5** — ESP-IDF ✅
- ESPHome **2026.6.4** — ESP-IDF ✅

---


## [1.0.26] — 2026-09-14 — Timer-Start-/Stoppzeit als Text Sensor

### Hinzugefügt
- Neue `text_sensor`-Typen `TIMER_START_TIME` und `TIMER_STOP_TIME`: geben die aktuell auf dem
  CP Plus hinterlegte Timer-Start- bzw. Stoppzeit im Format `HH:MM` aus
- Beide lesen dieselbe `StatusFrameTimer`-LIN-Bus-Nachricht, die auch die Binary Sensors
  `TIMER_ACTIVE` / `TIMER_ROOM` / `TIMER_WATER` speist — kein zusätzlicher Bus-Traffic
- `text_sensor`-Plattform unterstützt jetzt mehrere Typen über `type:` (vorher war nur die
  Versionsanzeige möglich). `type:` ist optional, Default `VERSION` — bestehende Configs ohne
  `type:` sind nicht betroffen
- README (DE/EN): neuer Abschnitt zu den verfügbaren `text_sensor`-Typen mit Beispiel-YAML

### Intern
- `TrumaVersionTextSensor` erbt jetzt zusätzlich von `Parented<TrumaiNetBoxApp>`, damit alle
  `truma_inetbox`-Text-Sensoren über denselben generischen `to_code()`-Pfad registriert werden
  können (ungenutzter Parent-Pointer, kein Verhaltensunterschied)

## [1.0.25] — 2026-09-07 — Beispiel-YAMLs: `id` für Operating Status''',
    ),
    (
        ROOT / "CHANGELOG.en.md",
        '''## Compatibility Status

### Summary

This release only touches the example configurations: the "Operating Status" sensor now
has an `id` and can be evaluated from lambdas, for example to tell whether the burner is
currently running. No changes to the component code.

Tested against:
- ESPHome **2026.8.2** — ESP-IDF ✅
- ESPHome **2026.6.5** — ESP-IDF ✅
- ESPHome **2026.6.4** — ESP-IDF ✅

---


## [1.0.25] — 2026-09-07 — Example YAMLs: `id` for Operating Status''',
        '''## Compatibility Status

### Summary

This release adds two new `text_sensor` types (`TIMER_START_TIME` / `TIMER_STOP_TIME`) that expose
the timer start/stop times the CP Plus already reports over the LIN bus as their own Home Assistant
entities. Existing `text_sensor` configs without `type:` are unaffected (default stays `VERSION`).

⚠️ This change has not been tested on real hardware yet (neither compiled nor verified against a
CP Plus) — please double-check with `esphome compile`/`esphome run` yourself before relying on it.

Last tested on hardware (as of 1.0.25):
- ESPHome **2026.8.2** — ESP-IDF ✅
- ESPHome **2026.6.5** — ESP-IDF ✅
- ESPHome **2026.6.4** — ESP-IDF ✅

---


## [1.0.26] — 2026-09-14 — Timer start/stop time as a text sensor

### Added
- New `text_sensor` types `TIMER_START_TIME` and `TIMER_STOP_TIME`: report the timer start/stop
  time currently stored on the CP Plus, formatted as `HH:MM`
- Both read the same `StatusFrameTimer` LIN bus message that already feeds the `TIMER_ACTIVE` /
  `TIMER_ROOM` / `TIMER_WATER` binary sensors — no extra bus traffic
- The `text_sensor` platform now supports multiple types via `type:` (previously only the version
  display was possible). `type:` is optional, defaulting to `VERSION` — existing configs without
  `type:` are unaffected
- README (DE/EN): new section documenting the available `text_sensor` types with an example YAML

### Internal
- `TrumaVersionTextSensor` now also inherits from `Parented<TrumaiNetBoxApp>` so that every
  `truma_inetbox` text sensor can be registered through the same generic `to_code()` path (unused
  parent pointer, no behavior change)

## [1.0.25] — 2026-09-07 — Example YAMLs: `id` for Operating Status''',
    ),
]

exit_code = 0
for path, anchor, replacement in DOC_REPLACEMENTS:
    if not path.exists():
        print(f"WARNUNG: {path.relative_to(ROOT)} nicht gefunden, uebersprungen.")
        exit_code = 1
        continue
    text = path.read_text(encoding="utf-8")
    if anchor not in text:
        print(
            f"WARNUNG: Anker-Text in {path.relative_to(ROOT)} nicht gefunden - "
            "Datei wurde NICHT veraendert. Vermutlich weicht der Inhalt ab; "
            "bitte diese Datei manuell nachziehen."
        )
        exit_code = 1
        continue
    text = text.replace(anchor, replacement, 1)
    path.write_text(text, encoding="utf-8")
    print(f"aktualisiert: {path.relative_to(ROOT)}")

if exit_code:
    print("\\nFertig, aber mit Warnungen (siehe oben) - bitte pruefen.")
else:
    print("\\nAlle Dateien erfolgreich geschrieben/aktualisiert.")
sys.exit(exit_code)
