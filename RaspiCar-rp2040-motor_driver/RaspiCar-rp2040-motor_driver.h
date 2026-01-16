#ifndef __RASPICAR_RP2040__
#define __RASPICAR_RP2040__

#include <arduino.h>
#include <EEPROM.h>
#include "util.h"

#define SOFTWARE_VERSION 96
#define PROMPT_OK "OK"
#define INFO "RaspiCar Motor Driver (by SLW) "

// EEPROM
#define EEPROM_BASE_ADDR       0
#define EEPROM_MOTOR_RAMP      0
#define EEPROM_BAT_SLOPE       4
#define EEPROM_BAT_INTERCEPT   8

#endif