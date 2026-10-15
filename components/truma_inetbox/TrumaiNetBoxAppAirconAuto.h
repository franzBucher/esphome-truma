#pragma once

#include "TrumaStausFrameStorage.h"
#include "TrumaStructs.h"

namespace esphome {
namespace truma_inetbox {

// Read-only since 1.0.41: the CP Plus rejects writes to the AUTO frame, only the status is kept.
class TrumaiNetBoxAppAirconAuto : public TrumaStausFrameStorage<StatusFrameAirconAuto> {
 public:
  void dump_data() const override;
};

}  // namespace truma_inetbox
}  // namespace esphome
