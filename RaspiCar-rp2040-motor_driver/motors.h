#ifndef __MOTORS__
#define __MOTORS__

#include <arduino.h>
#include <EEPROM.h>

// pin definitions
#define MOTA_PWR         21
#define MOTA_STEP        20
#define MOTA_DIR         19
#define MOTB_PWR         18
#define MOTB_STEP        17
#define MOTB_DIR         16

// Motor step time
#define MOT_STEP_TIME_MAX 150000
#define MOT_STEP_TIME_MIN     60
#define CONVERSION_FACTOR  75000  // lower values -> faster
#define MOT_RAMP              15  // limit: 0 ... 100
#define RPM_MAX             1250
#define RPM_MIN                1

// Function prototypes
bool mot_a_timer_callback(struct repeating_timer *t);
bool mot_b_timer_callback(struct repeating_timer *t);

// EEPROM
#define EEPROM_BASE_ADDR       0

class Motors {
  private:
    bool a_dir = true;
    bool b_dir = true;
	  int mot_ramp = MOT_RAMP;
	  uint32_t calc_step_time(uint32_t current_step_time, bool up);
    uint32_t a_step_time_target = MOT_STEP_TIME_MAX, b_step_time_target = MOT_STEP_TIME_MAX;

  public:
    bool a_enabled = false;
    bool b_enabled = false;
    bool a_power = false;
    bool b_power = false;
  	uint32_t a_step_time = MOT_STEP_TIME_MAX, b_step_time = MOT_STEP_TIME_MAX;
  
    void init(void);
  	void set_a_enable(bool status);
  	void set_b_enable(bool status);
    bool get_a_enabled(void);
    bool get_b_enabled(void);  	
  	void set_a_power(bool status);
  	void set_b_power(bool status);
    bool get_a_power(void);
    bool get_b_power(void);
    void set_a_dir(bool status);
    void set_b_dir(bool status);
  	void check_step_time_a(void);
  	void check_step_time_b(void);
    void set_a_steptime(uint32_t steptime);
    void set_b_steptime(uint32_t steptime);
    void set_a_rpm(uint32_t rpm);
    void set_b_rpm(uint32_t rpm);
    uint32_t get_a_rpm(void);
    uint32_t get_b_rpm(void);
    void set_ramp(uint32_t ramp);
    uint32_t get_ramp(void);
	
};

#endif
