#pragma once

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
