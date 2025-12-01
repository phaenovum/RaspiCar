#include "battery.h"

struct repeating_timer bat_voltage_timer;

//-------------------------------------------------------------------------
void Battery::init(void) {
  pinMode(ADC_BATTERY_GPIO, INPUT);
  pinMode(LED_BAT_LOW, OUTPUT);
  digitalWrite(LED_BAT_LOW, LOW);

  add_repeating_timer_ms(10, bat_voltage_timer_callback, NULL, &bat_voltage_timer); 
}

//-------------------------------------------------------------------------
// Retrieves and sums up the adc value.
// After every 16th call, returns true (to initiate display refresh), otherwise false
bool Battery::run_adc(void) {
  extern LCD_Display display;
  
  adc_sum += analogRead(ADC_BATTERY);
  cnt_adc += 1;
  if (cnt_adc > 16) {
    cnt_adc = 0;
    voltage = (uint16_t) (100*(adc_sum * ADC_REF * BAT_DIVIDER / (ADC_RANGE * 16) + BAT_TL431_OFFSET));
    if (voltage < BAT_EXTERNAL) voltage = 0;
    adc_sum = 0;
    cnt_show += 1;    
    if (status < 3) {    // if status unequal 'SR' and 'SX' and 'BE'
      if (voltage > BAT_LOW) status = 0; // 'OK'
      else if (voltage > BAT_SHUTDOWN) status = 1; // 'BL' battery low
      else if (voltage > BAT_EXTERNAL) status = 2; // 'BS' battery shutdown
      else status = 3; // 'BE' battery external
    }
  }

  // manage power down button
  if (digitalRead(POWER_DOWN_BT) == LOW) {
    cnt_shutdown_button += 1;
    switch (cnt_shutdown_button) {
      case 5:      // request or confirm shutdown
        request_shutdown();
        break;
      case 1000:   // force shutdown
        digitalWrite(POWER_ON, LOW);
        break;
    }
  } else {
    cnt_shutdown_button = 0;
  }

  // show battery status 
  if (cnt_show >= 16) {
    cnt_show = 0;
    // manage pending shutdown via cnt_shutdown_wait
    if ((status != STATUS_SHUTDOWN_ACTIVE) && 
        (digitalRead(POWER_DOWN_BT) == HIGH) && 
        (cnt_shutdown_request_wait > 0)) {
      cnt_shutdown_request_wait -= 1;
      if (cnt_shutdown_request_wait == 0) {
        display.print_msg("Shutdown cancelled");
        status = 0;
      }
    }
    // Run shutdown
    if ((cnt_shutdown > 0)) {
      cnt_shutdown -= 1;
      display.shutdown_timer(cnt_shutdown);
      if (cnt_shutdown == 0) {
        digitalWrite(POWER_ON, LOW);
      }
    }
    return true;
    
  } else {
    return false;
  }
}

//-------------------------------------------------------------------------
void Battery::get_full_status(char buf[]) {

  itoaf(voltage, buf, 4, 2, false);
  switch (status) {
    case STATUS_OK: 
      strcat(buf, ",OK");
      break;
    case STATUS_BAT_LOW: 
      strcat(buf, ",BL");
      break;
    case STATUS_BAT_SHUTDOWN: 
      strcat(buf, ",SB");
      break;
    case STATUS_BAT_EXTERNAL:
      strcat(buf, ",BE");
      break;
    case STATUS_SHUTDOWN_REQUESTED: 
      strcat(buf, ",SR");
      break;
    case STATUS_SHUTDOWN_ACTIVE:
      strcat(buf, ",SX");
  } 
}

//-------------------------------------------------------------------------
uint8_t Battery::get_status(void) {

  return status;
}

//-------------------------------------------------------------------------
int16_t Battery::get_voltage(void) {
  return voltage;
}

//-------------------------------------------------------------------------
void Battery::request_shutdown(void) {
  extern LCD_Display display;

  if (cnt_shutdown_request_wait == 0) {
    display.print_msg("Shutdown - are you sure?");
  } else {
    status = 4;
    display.print_msg("Shutdown requested");    
  }
  cnt_shutdown_request_wait = WAIT_SHUTDOWN_REQUEST_CONFIRMATION;
}

//-------------------------------------------------------------------------
void Battery::start_shutdown(void) {
  extern LCD_Display display;
  
  status = 2;
  cnt_shutdown = WAIT_SHUTDOWN;
  display.print_msg("Shutdown ...");
}


//-------------------------------------------------------------------------
void Battery::request_bat_shutdown(void) {
  extern LCD_Display display;

  status = 2;  // 'SR'
  display.print_msg("Battery shutdown");    
  cnt_shutdown_request_wait = WAIT_SHUTDOWN_REQUEST_CONFIRMATION;   
}

//-------------------------------------------------------------------
bool bat_voltage_timer_callback(struct repeating_timer *t) {
  extern volatile uint8_t job_flags;
  job_flags |= (1 << JF_REFRESH_BAT_VOLTAGE);
  return true;
}
