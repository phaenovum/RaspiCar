# include "command_decoder.h"


//-------------------------------------------------------------------------
// init
void CommandDecoder::init(void) {
	buf[0] = '\0';
	buf_pnt = 0;
}


//-------------------------------------------------------------------------
// Adds a char from the serial interface to the input buffer. 
// Returns false, unless a end-of-line character is detected.
bool CommandDecoder::add_to_buffer(char c) {
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
int32_t CommandDecoder::get_int(uint8_t *pnt) {
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
// show_info
void CommandDecoder::show_info(void) {
  uart_puts(uart1, INFO);
  uart_puts(uart1, "\r\nSoftware Version:");
  itoaf(SOFTWARE_VERSION, local_buf, 3, 2, false);
  uart_puts(uart1, local_buf);
  uart_puts(uart1, "\r\n");
}


//-------------------------------------------------------------------------
void CommandDecoder::decode_get_command(uint8_t pnt) {
  uint8_t status = 0;   // 0 -> okay, 1 -> okay, no prompt, 2 -> error
  extern Battery bat;
  
  switch (buf[pnt]) {
    case 'i':               // get info
    case 'I':
      show_info();
      status = 1;
      break;

    case 'm':               // get max speed
    case 'M':
      itoaf(RPM_MAX, local_buf, 5, 0, false);
      uart_puts(uart1, local_buf); 
      status = 1;
      break;

    case 'r':               // get battery raw voltage
    case 'R':
      itoaf(bat.get_raw_voltage(), local_buf, 5, 0, false);
      uart_puts(uart1, local_buf); 
      status = 1;
      break;

    case 's':               // get battery status
    case 'S':
      bat.get_decode_status(local_buf);
      uart_puts(uart1, local_buf);
      status = 1;
      break;

    case 'u':               // get battery voltage
    case 'U':
      itoaf(bat.get_voltage(), local_buf, 4, 2, false);
      uart_puts(uart1, local_buf); 
      status = 1;
      break;

    case 'v':               // return software version number
    case 'V':
      itoaf(SOFTWARE_VERSION, local_buf, 3, 2, false);
      uart_puts(uart1, local_buf);
      status = 1;
      break;

    default:
      status = 2;
  }

  switch (status) {
    case 0: 
     uart_puts(uart1, PROMPT_OK);
     break;
    case 1:
      break;
    case 2:
      uart_puts(uart1, "Get command not recognized: ");
      uart_puts(uart1, buf);
    default:
      break;
  }
  uart_puts(uart1, "\r\n");
}


//-------------------------------------------------------------------------
void CommandDecoder::decode_config_command(uint8_t pnt) {
  uint32_t a;
  uint8_t status = 0;   // 0 -> okay, 1 -> okay, no prompt, 2 -> error
  extern Battery bat;
  extern Motors motors;
  
  switch (buf[pnt]) {
    case 'r':               // set_ramp
    case 'R':
      pnt += 1;
      a = get_int(&pnt);    
      if ((a >= 1) && (a <= 50)) {
        motors.set_ramp(a); 
      } else {
        uart_puts(uart1, "Ramp out of range (valid range: 1 ... 50)");
        status = 1;
      }
      break;

    case 'g':
    case 'G':             // get config
      uart_puts(uart1, "Motor ramp:        ");
      itoa(motors.get_ramp(), local_buf, 10);
      uart_puts(uart1, local_buf);
      uart_puts(uart1, "\r\n");
      uart_puts(uart1, "Bat ADC intercept: ");
      itoa(bat.get_bat_intercept(), local_buf, 10);
      uart_puts(uart1, local_buf);
      uart_puts(uart1, "\r\n");
      uart_puts(uart1, "Bat ADC slope    : ");
      itoa(bat.get_bat_slope(), local_buf, 10);
      uart_puts(uart1, local_buf);
      status = 1;
      break;

    case 'i':             // set bat intercept
    case 'I':
      pnt += 1;
      a = get_int(&pnt);    
      if ((a >= BAT_INTERCEPT_MIN) && (a <= BAT_INTERCEPT_MAX)) {
        bat.set_bat_intercept(a); 
      } else {
        uart_puts(uart1, "Bat intercept out of range! (valid range ");
        itoa(BAT_INTERCEPT_MIN, local_buf, 10);
        uart_puts(uart1, local_buf);
        uart_puts(uart1, " ... ");
        itoa(BAT_INTERCEPT_MAX, local_buf, 10);
        uart_puts(uart1, local_buf);
        uart_puts(uart1, ")");
        status = 1;
      }
      break;

    case 's':             // set bat slope
    case 'S':
      pnt += 1;
      a = get_int(&pnt);    
      if ((a >= BAT_SLOPE_MIN) && (a <= BAT_SLOPE_MAX)) {
        bat.set_bat_slope(a); 
      } else {
        uart_puts(uart1, "Bat slope out of range! (valid range ");
        itoa(BAT_SLOPE_MIN, local_buf, 10);
        uart_puts(uart1, local_buf);
        uart_puts(uart1, " ... ");
        itoa(BAT_SLOPE_MAX, local_buf, 10);
        uart_puts(uart1, local_buf);
        uart_puts(uart1, ")");
        status = 1;
      }
      break;

    default:
      status = 2;
  }

  switch (status) {
    case 0: 
     uart_puts(uart1, PROMPT_OK);
     break;
    case 1:
      break;
    case 2:
      uart_puts(uart1, "Config command not recognized: ");
      uart_puts(uart1, buf);
    default:
      break;
  }
  uart_puts(uart1, "\r\n");
}


//-------------------------------------------------------------------------
void CommandDecoder::decode_bat_command(uint8_t pnt) {
  uint8_t status = 0;   // 0 -> okay, 1 -> okay, no prompt, 2 -> error
  extern Battery bat;
  extern LCD_Display display;
  
  switch (buf[pnt]) {
    case 'v':               // get battery voltage
    case 'V':
      itoaf(bat.get_voltage(), local_buf, 4, 2, false);
      uart_puts(uart1, local_buf); 
      status = 1;
      break;

    case 's':               // get battery status
    case 'S':
      bat.get_full_status(local_buf);
      uart_puts(uart1, local_buf);
      status = 1;
      break;

    case 'r':               // get battery raw voltage
    case 'R':
      itoaf(bat.get_raw_voltage(), local_buf, 5, 0, false);
      uart_puts(uart1, local_buf); 
      status = 1;
      break;

    case 'x':
    case 'X':
      display.print_msg("Shutting down");
      bat.start_shutdown();
      break;
 
    default:
      status = 2;
  }

  switch (status) {
    case 0: 
     uart_puts(uart1, PROMPT_OK);
     break;
    case 1:
      break;
    case 2:
      uart_puts(uart1, "Battery command not recognized: ");
      uart_puts(uart1, buf);
    default:
      break;
  }
  uart_puts(uart1, "\r\n");
}


//-------------------------------------------------------------------------
void CommandDecoder::decode_display_command(uint8_t pnt) {
  uint8_t status = 0;   // 0 -> okay, 1 -> okay, no prompt, 2 -> error
  extern LCD_Display display;
  
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
      status = 2;
  }
  
  switch (status) {
    case 0: 
     uart_puts(uart1, PROMPT_OK);
     break;
    case 1:
      break;
    case 2:
      uart_puts(uart1, "Config command not recognized: ");
      uart_puts(uart1, buf);
    default:
      break;
  }
    uart_puts(uart1, "\r\n");
}

//-------------------------------------------------------------------------
void CommandDecoder::decode_motor_command(uint8_t pnt) {
  int32_t a, b;
  uint8_t status = 0;   // 0 -> okay, 1 -> okay, no prompt, 2 -> error
  extern Motors motors;
  extern LCD_Display display;

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

    case 'r':
    case 'R':                         // runs the motor at a given speed
      pnt += 1;
      a = get_int(&pnt);    
      b = get_int(&pnt);
      if (a < VALID_LIMIT) {
        if (a <= RPM_MAX) {
          motors.set_a_rpm(a);
          display.mot_a_rpm(motors.get_a_rpm());
          display.mot_a_enabled(motors.get_a_enabled()); 
          display.mot_a_power(motors.get_a_power());
        } else {
          uart_puts(uart1, "Motor RPM A out of range! (max ");
          itoa(RPM_MAX, local_buf, 10);
          uart_puts(uart1, local_buf);
          uart_puts(uart1, ")\r\n");
          status = 1;
          status = 1;
        }
      };
      if (b < VALID_LIMIT) {
        if (b <= RPM_MAX) {
          motors.set_b_rpm(b);
          display.mot_b_rpm(motors.get_b_rpm());
          display.mot_b_enabled(motors.get_b_enabled()); 
          display.mot_b_power(motors.get_b_power());
        } else {
          uart_puts(uart1, "Motor RPM B out of range! (max ");
          itoa(RPM_MAX, local_buf, 10);
          uart_puts(uart1, local_buf);
          uart_puts(uart1, ")\r\n");
          status = 1;
        }
      };
      break;
      
    default:
      status = 2;
  }
  
  switch (status) {
    case 0: 
     uart_puts(uart1, PROMPT_OK);
     uart_puts(uart1, "\r\n");
     break;
    case 1:
      break;
    case 2:
      uart_puts(uart1, "Config command not recognized: ");
      uart_puts(uart1, buf);
      uart_puts(uart1, "\r\n");
    default:
      break;
  }
}


//-------------------------------------------------------------------------
void CommandDecoder::decode_command(void) {
  uint8_t pnt = 0;

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

    case 'g':
    case 'G':
      decode_get_command(pnt+1);
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
      show_info();
      break;

    default:
	  uart_puts(uart1, "Not recognized: ");
      uart_puts(uart1, buf);
      uart_puts(uart1, "\r\n");
  }  

  buf[0] = '\0';
}    
