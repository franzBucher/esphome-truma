#pragma once

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
