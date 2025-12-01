#ifndef __DISPLAY__
#define __DISPLAY__

#include <PicoLCD_I2C.h>
#include "RaspiCar-rp2040-motor_driver.h"
#include "util.h"

// Pin definitions
#define LCD_SDA           4
#define LCD_SCL           5

// Display X-Positions 
#define LCD_X_MOTA_P       0
#define LCD_X_MOTA_E       1
#define LCD_X_MOTA_RPM     2
#define LCD_X_MOTB_P       7
#define LCD_X_MOTB_E       8
#define LCD_X_MOTB_RPM     9
#define LCD_X_BAT_VOLTAGE 14

class LCD_Display {
  private:
    bool mot_a_is_power, mot_b_is_power;
    bool mot_a_is_enabled, mot_b_is_enabled;
    void print_dec(int n);
    
  public:
    void init(void);
    void mot_a_enabled(bool state);
    void mot_b_enabled(bool state);
    void mot_a_power(bool state);
    void mot_b_power(bool state);
    void mot_a_rpm(uint32_t rpm);
    void mot_b_rpm(uint32_t rpm);
    void show_voltage(uint16_t bat_voltage);
    void shutdown(void);
    void shutdown_timer(int i);
    void clear(void);
    void print_title(const char buf[]);
    void print_msg(const char buf[]);
};

#endif
