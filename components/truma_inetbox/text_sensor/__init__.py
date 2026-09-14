from esphome.components import text_sensor
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
