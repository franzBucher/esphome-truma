#pragma once

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
