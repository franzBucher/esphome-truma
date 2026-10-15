#include "TrumaCpPlusBinarySensor.h"
#include "esphome/core/log.h"
#include "esphome/components/truma_inetbox/helpers.h"

namespace esphome {
namespace truma_inetbox {

static const char *const TAG = "truma_inetbox.cpplus_binary_sensor";

static constexpr uint32_t CP_PLUS_TIMEOUT_US = 90 * 1000 * 1000;  // 90 seconds without CP Plus request = disconnected

void TrumaCpPlusBinarySensor::update() {
  const uint32_t last_request = this->parent_->get_last_cp_plus_request();
  // A request that already timed out keeps the sensor off until a newer one arrives; otherwise the
  // subtraction below would report "connected" for 90 s every time micros() wraps around (~71 min).
  if (this->parent_->get_lin_bus_fault() || last_request == 0 || last_request == this->timed_out_request_) {
    this->publish_state(false);
    return;
  }
  // Subtraction idiom is wraparound-safe for the 32-bit micros() counter.
  const uint32_t since_last_request = micros() - last_request;
  if (since_last_request >= CP_PLUS_TIMEOUT_US) {
    this->timed_out_request_ = last_request;
  }
  this->publish_state(since_last_request < CP_PLUS_TIMEOUT_US);
}

void TrumaCpPlusBinarySensor::dump_config() { LOG_BINARY_SENSOR("", "Truma CP Plus Binary Sensor", this); }
}  // namespace truma_inetbox
}  // namespace esphome