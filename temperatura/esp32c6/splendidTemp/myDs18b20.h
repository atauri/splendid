#include "OneWireNg_CurrentPlatform.h"
#include "drivers/DSTherm.h"
#include "utils/Placeholder.h"

#ifndef OW_PIN
# define OW_PIN 4
#endif

#if !defined(SINGLE_SENSOR) && !CONFIG_SEARCH_ENABLED
# error "CONFIG_SEARCH_ENABLED is required for non single sensor setup"
#endif

#if defined(PWR_CTRL_PIN) && !CONFIG_PWR_CTRL_ENABLED
# error "CONFIG_PWR_CTRL_ENABLED is required if PWR_CTRL_PIN is configured"
#endif

#if (CONFIG_MAX_SEARCH_FILTERS > 0)
static_assert(CONFIG_MAX_SEARCH_FILTERS >= DSTherm::SUPPORTED_SLAVES_NUM,
    "CONFIG_MAX_SEARCH_FILTERS too small");
#endif

#ifdef PARASITE_POWER
# define PARASITE_POWER_ARG true
#else
# define PARASITE_POWER_ARG false
#endif

static Placeholder<OneWireNg_CurrentPlatform> ow;

static float getTemp(const DSTherm::Scratchpad& scrpd)
{
    const uint8_t *scrpd_raw = scrpd.getRaw();
    long temp = scrpd.getTemp2();
    return (float)temp / 16;

}

void beginDs18b20()
{

    Serial.println("begin");
    #ifdef PWR_CTRL_PIN
        new (&ow) OneWireNg_CurrentPlatform(OW_PIN, PWR_CTRL_PIN, false);
    #else
        new (&ow) OneWireNg_CurrentPlatform(OW_PIN, false);
    #endif
        DSTherm drv(ow);

    #if (CONFIG_MAX_SEARCH_FILTERS > 0)
        drv.filterSupportedSlaves();
    #endif

    #ifdef COMMON_RES
    /*
     * Set common resolution for all sensors.
     * Th, Tl (high/low alarm triggers) are set to 0.
     */
    drv.writeScratchpadAll(0, 0, COMMON_RES);

    /*
     * The configuration above is stored in volatile sensors scratchpad
     * memory and will be lost after power unplug. Therefore store the
     * configuration permanently in sensors EEPROM.
     */
    drv.copyScratchpadAll(PARASITE_POWER_ARG);
    #endif
}

float leerDs18b20(){
    
    DSTherm drv(ow);

    drv.convertTempAll(DSTherm::MAX_CONV_TIME, PARASITE_POWER_ARG);
    Placeholder<DSTherm::Scratchpad> scrpd;

    for (const auto& id: *ow) {
        //if (printId(id)) {
            if (drv.readScratchpad(id, scrpd) == OneWireNg::EC_SUCCESS)
                //printScratchpad(scrpd);
                return getTemp(scrpd);
            else
              return -9999;
    }

}
