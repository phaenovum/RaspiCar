/*
 * rp2040 Motor Driver (RaspiCar)
 * This module is part of the phaenovum RaspiCar project. 
 * It provides driver function for two stepper motors. Beyond that, it serves 
 * as power and battery manager. Finally, it includes a LCD display to shows 
 * status information and simplify debugging. It uses a seruial interface
 * (fixed baud rate at 115200) for communication with the Raspberry Pi. 
 * 
 * SLW - October 2022
 * Last update - November 2025
 */

#include "RaspiCar-rp2040-motor_driver.h"
#include "display.h"
#include "motors.h"
#include "battery.h"
#include "command_decoder.h"

// Pins
#define SERIAL_TX         8      // serial interface to Raspberry Pi
#define SERIAL_RX         9
#define RASPI_IN          2      // reserve: additional GPIO to RaspiPi 
#define RASPI_OUT         3      // reserve: additional GPIO to RaspiPi 

// Global variables
LCD_Display display;
Motors motors;
Battery bat;
CommandDecoder cmd;
char buf[BUF_SIZE];
int buf_pnt=0;
int i = 0;
volatile uint8_t job_flags = 0b00000000;
int power_down_bt_status = 0;


//-------------------------------------------------------------------------
void setup() {
  // initialize power management
  pinMode(POWER_ON, OUTPUT);
  digitalWrite(POWER_ON, HIGH);
  pinMode(POWER_DOWN_BT, INPUT_PULLUP);
  pinMode(RASPI_IN, OUTPUT);
  pinMode(RASPI_OUT, INPUT);

  Serial.begin(115200);

  // initialize serial interface to RaspPi
  gpio_set_function(SERIAL_TX, GPIO_FUNC_UART);   // TX 
  gpio_set_function(SERIAL_RX, GPIO_FUNC_UART);   // RX
  uart_init(uart1, 115200);

  // initilaize eeprom
  EEPROM.begin(256);

  // start motors
  motors.init();

  // start battery management
  bat.init();

  // initialize reserve GPIOs to and from Raspi
  pinMode(RASPI_OUT, INPUT);
  pinMode(RASPI_IN, OUTPUT);
  digitalWrite(RASPI_IN, LOW);

  // start display
  display.init();

  // start command decoder
  cmd.init();

  delay(100);
}

long cnt=0;

//-------------------------------------------------------------------------
void loop() {
  char c;
  
  if (uart_is_readable(uart1)) {
    c = uart_getc(uart1);
    if (cmd.add_to_buffer(c) == true) {
      cmd.decode_command();
    }
  }

  if (job_flags & (1 << JF_REFRESH_BAT_VOLTAGE)) {
    job_flags &= ~(1 << JF_REFRESH_BAT_VOLTAGE);
    if (bat.run_adc()) { 
      display.show_voltage(bat.get_voltage());
    if (bat.get_status() == STATUS_BAT_SHUTDOWN) 
      bat.request_bat_shutdown();
    }
    motors.check_step_time_a();
    motors.check_step_time_b();
  }
}
