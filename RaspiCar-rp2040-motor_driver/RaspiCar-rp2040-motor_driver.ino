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
#include "util.h"

#define BUF_SIZE 40

// Pins
#define SERIAL_TX         8      // serial interface to Raspberry Pi
#define SERIAL_RX         9
#define RASPI_IN          2      // reserve: additional GPIO to RaspiPi 
#define RASPI_OUT         3      // reserve: additional GPIO to RaspiPi 

// Decode input from serial interface
#define VALID_LIMIT 999999

// Global variables
LCD_Display display;
Motors motors;
Battery bat;
char buf[BUF_SIZE];
int buf_pnt=0;
int i = 0;
volatile uint8_t job_flags = 0b00000000;
int power_down_bt_status = 0;


//-------------------------------------------------------------------------
// Adds a char from the serial interface to the input buffer. 
// Returns false, unless a end-of-line character is detected.
bool add_to_buffer(char c) {
  switch ((uint8_t) c) {
    case 13:   // carriage return
    case 10:   // line feed
      buf[buf_pnt] = '\0';
      buf_pnt = 0;
      return true;
    case 8:    // backspace
      buf[buf_pnt] = '\0';
      if (buf_pnt > 0) buf_pnt -= 1;
      break;
    default:     // all other chars
      buf[buf_pnt] = c;
      if (buf_pnt < BUF_SIZE - 1) 
      ++buf_pnt;
  }
  return false;
}

//-------------------------------------------------------------------------
// get_int
// Extracts an integer from the input buffer. 
// Moves the pointer to the next position after the integer
int32_t get_int(uint8_t *pnt) {
  int32_t result = 0;
  bool negative_flag = false, done = false, valid = false;

  while (buf[*pnt] == ' ') *pnt += 1;     // skip leading blanks
  
  while (!done) {
    if (buf[*pnt] == '+') {
      negative_flag = false;
    } else if (buf[*pnt] == '-') {
      negative_flag = true;
    } else if ((buf[*pnt] >= '0') && (buf[*pnt] <= '9')) {
      result = result * 10;
      result += buf[*pnt] - '0';
      valid = true;
    } else {
      done = true;
    }
    if (buf[*pnt] != '\0')      // don't progress beyond end of string
      *pnt += 1;
  }
  if (!valid) {
    result = VALID_LIMIT;
  } else if (negative_flag) {
    result = -result;
  }
  return result;
}

//-------------------------------------------------------------------------
void decode_config_command(uint8_t pnt) {
  char local_buf[16];
  uint32_t a;
  bool okay = true;
  
  switch (buf[pnt]) {
    case 'r':               // set_ramp
    case 'R':
      pnt += 1;
      a = get_int(&pnt);    
      if ((a >= 1) && (a <= 50)) {
        motors.set_ramp(a); 
      } else {
        uart_puts(uart1, "Valid range: 1 ... 50");
        okay = false;
      }
      break;

    case 'g':
    case 'G':             // get config
      uart_puts(uart1, "Ramp: ");
      itoa(motors.get_ramp(), local_buf, 10);
      uart_puts(uart1, local_buf);
      okay = false;
      break;

    default:
      okay = false;
  }
  if (okay) {
      uart_puts(uart1, PROMPT_OK);
  } else {
      uart_puts(uart1, "Config command not recognized: ");
      uart_puts(uart1, buf);
  }
  uart_puts(uart1, "\r\n");
}

//-------------------------------------------------------------------------
void decode_bat_command(uint8_t pnt) {
  char local_buf[16];
  bool okay = true;
  
  switch (buf[pnt]) {
    case 'v':               // get battery voltage
    case 'V':
      itoaf(bat.get_voltage(), local_buf, 4, 2, false);
      uart_puts(uart1, local_buf); 
      break;

    case 's':               // get battery status
    case 'S':
      bat.get_full_status(local_buf);
      uart_puts(uart1, local_buf);
      break;

    case 'x':
    case 'X':
      display.print_msg("Shutting down");
      bat.start_shutdown();
      uart_puts(uart1, "OK");
      break;
 
    default:
      okay = false;
  }
    if (okay) {
      uart_puts(uart1, PROMPT_OK);
  } else {
      uart_puts(uart1, "Battery command not recognized: ");
      uart_puts(uart1, buf);
  }
  uart_puts(uart1, "\r\n");
}

//-------------------------------------------------------------------------
void decode_display_command(uint8_t pnt) {
  bool okay = true;
  
  switch (buf[pnt]) {
    case 'c':           // clear display
    case 'C':
      display.clear();
      break;
      
    case 't':           // print title
    case 'T':
      display.print_title(buf+2);
      break;
      
    case 'm':           // print message
    case 'M':
      display.print_msg(buf+2);
      break;
      
    default:
      okay = false;
  }
  if (okay) {
    uart_puts(uart1, PROMPT_OK);
  } else {
    uart_puts(uart1, "Display command not recognized: ");
    uart_puts(uart1, buf);
  }
  uart_puts(uart1, "\r\n");
}

//-------------------------------------------------------------------------
void decode_motor_command(uint8_t pnt) {
  int32_t a, b;
  bool okay = true;

  switch (buf[pnt]) {
    case 'd':
    case 'D':                                 // dir
      pnt += 1;
      a = get_int(&pnt);    
      b = get_int(&pnt);
      if (a < VALID_LIMIT) {
        motors.set_a_dir(a > 0);
      }
      if (b < VALID_LIMIT) {
        motors.set_b_dir(b > 0);
      }     
      break;
    
    case 'e':
    case 'E':                                 // enable
      pnt += 1;
      a = get_int(&pnt);    
      b = get_int(&pnt);
      if (a < VALID_LIMIT) {
        motors.set_a_enable(a > 0);
        display.mot_a_enabled(motors.get_a_enabled());
      }
      if (b < VALID_LIMIT) {
        motors.set_b_enable(b > 0);
        display.mot_b_enabled(motors.get_b_enabled());
      }     
      break;
      
    case 'p':
    case 'P':                                 // power
      pnt += 1;
      a = get_int(&pnt);    
      b = get_int(&pnt);
      if (a < VALID_LIMIT) {
        motors.set_a_power(a > 0);
        display.mot_a_power(motors.get_a_power());
      }
      if (b < VALID_LIMIT) {
        motors.set_b_power(b > 0);
        display.mot_b_power(motors.get_b_power());
      }     
      break;

    /*
    case 't':                             // set cycle time
    case 'T':
      pnt += 1;
      a = get_int(&pnt);    
      b = get_int(&pnt);
      if (a < VALID_LIMIT) {
        if (a < MOT_STEP_TIME_MIN) {
          a = MOT_STEP_TIME_MIN;
          uart_puts(uart1, "Mot A: Lower limit\n\r");
        }
        else if (a > MOT_STEP_TIME_MAX) {
          a = MOT_STEP_TIME_MAX;
          uart_puts(uart1, "Mot A: Upper limit\n\r");
        }
        mot_a_step_time_target = a;  
        display.mot_a_rpm(CONVERSION_FACTOR / a);  
      }
      if (b < VALID_LIMIT) {
        if (b < MOT_STEP_TIME_MIN) {
          b = MOT_STEP_TIME_MIN;
          uart_puts(uart1, "Mot B: Lower limit\n\r");
        }
        else if (b > MOT_STEP_TIME_MAX) {
          uart_puts(uart1, "Mot B: Upper limit\n\r");
          b = MOT_STEP_TIME_MAX;
        }
        mot_b_step_time_target = b; 
        display.mot_b_rpm(CONVERSION_FACTOR / b);  
      }
      */
      break;   

    case 'r':
    case 'R':                         // set rounds per minute
      pnt += 1;
      a = get_int(&pnt);    
      b = get_int(&pnt);
      if (a < VALID_LIMIT) {
        motors.set_a_rpm(a);
        display.mot_a_rpm(motors.get_a_rpm());
        display.mot_a_enabled(motors.get_a_enabled()); 
        display.mot_a_power(motors.get_a_power());
      };
      if (b < VALID_LIMIT) {
        motors.set_b_rpm(b);
        display.mot_b_rpm(motors.get_b_rpm());
        display.mot_b_enabled(motors.get_b_enabled()); 
        display.mot_b_power(motors.get_b_power());
      };
      break;
      
    default:
      okay = false;
  }

  if (okay) {
    uart_puts(uart1, PROMPT_OK);
  } else {
    uart_puts(uart1, "Motor command not recognized: ");
    uart_puts(uart1, buf);
  }
  uart_puts(uart1, "\r\n");
}

//-------------------------------------------------------------------------
void decode_command(void) {
  uint8_t pnt = 0;
  char local_buf[6];

  while (buf[pnt] == ' ') pnt += 1;     // skip leading blanks
  if (strlen(buf+pnt) == 0) {
    uart_puts(uart1, "\r\n");
    return;
  }
  
  switch (buf[pnt]) {
    case 'b':
    case 'B':
      decode_bat_command(pnt+1);
      break;
    case 'c':
    case 'C':
      decode_config_command(pnt+1);
      break;
    case 'd':
    case 'D':
      decode_display_command(pnt+1);
      break;
    case 'm':
    case 'M':
      decode_motor_command(pnt+1);
      break;
    case 'p':   // ping
    case 'P':
    case 'x':
    case 'X':
      // send a ping
      uart_puts(uart1, PROMPT_OK);
      uart_puts(uart1, "\r\n");
      break;

    case 'i':
    case 'I':
      uart_puts(uart1, INFO);
      uart_puts(uart1, "Software Version:");
      itoaf(SOFTWARE_VERSION, local_buf, 3, 2, false);
      uart_puts(uart1, local_buf);
      uart_puts(uart1, "\r\n");
      break;

    default:
      uart_puts(uart1, "Not recognized: ");
      uart_puts(uart1, buf);
      uart_puts(uart1, "\r\n");
  }  

  buf[0] = '\0';
}    

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

  delay(100);
}

long cnt=0;

//-------------------------------------------------------------------------
void loop() {
  char local_buf[16];
  
  if (uart_is_readable(uart1)) {
    if (add_to_buffer(uart_getc(uart1)) == true) {
      decode_command();
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
