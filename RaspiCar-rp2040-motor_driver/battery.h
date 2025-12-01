#ifndef __BATTERY__
#define __BATTERY__

#include <arduino.h>
#include "display.h"
#include "util.h"

// pin definitions
#define ADC_BATTERY      A2
#define ADC_BATTERY_GPIO 28
#define LED_BAT_LOW      13
#define POWER_ON         10      // system power 
#define POWER_DOWN_BT    11      // user button requesting system shutdown

// ADC
#define BAT_TL431_OFFSET      8.35
#define BAT_DIVIDER           1.85   // may need to be adjusted according to R2/R3
#define ADC_RANGE             1024
#define ADC_REF               3.24
#define BAT_LOW               1050
#define BAT_SHUTDOWN           950
#define BAT_EXTERNAL           890

// Shutdown
#define WAIT_SHUTDOWN                         6
#define WAIT_SHUTDOWN_REQUEST_CONFIRMATION    5
#define FORCE_SHUTDOWN_WAIT                 100

// status
#define STATUS_OK                 0   // 'OK'
#define STATUS_BAT_LOW            1   // 'BL'
#define STATUS_BAT_SHUTDOWN       2   // 'BS'
#define STATUS_BAT_EXTERNAL       3   // 'BE'
#define STATUS_SHUTDOWN_REQUESTED 4   // 'SR'
#define STATUS_SHUTDOWN_ACTIVE    5   // 'SX'

// Job flags
#define JF_REFRESH_BAT_VOLTAGE 0

class Battery {
  private:
    uint16_t voltage = 0;   // battery voltage, 10mV
    uint8_t status = 0;     // 0 -> all fine (OK), 1 -> battery low (BL), 
                            // 2 -> battery shutdown (SB), 3 -> shutdown requested (SR)
                            // 4 -> shutdown active
    int cnt_adc = 0;
    int cnt_show = 0;
    int cnt_shutdown = 0;
    long cnt_shutdown_button = 0;
    int cnt_shutdown_request_wait = 0;
    int cnt_force_shutdown = 0;
    uint32_t adc_sum = 0;
    void request_shutdown(void);
    void force_shutdown(void);
    
  public:
    void init(void);
    bool run_adc(void);
    int16_t get_voltage(void);
    uint8_t get_status(void);
    void get_full_status(char msg[]);
    void start_shutdown(void);  
    void request_bat_shutdown(void); 
};

// Function prototypes
bool bat_voltage_timer_callback(struct repeating_timer *t);

#endif
