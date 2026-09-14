#include "TrumaTimerTextSensor.h"
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
