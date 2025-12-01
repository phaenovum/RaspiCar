#include <arduino.h>
#include "display.h"

PicoLCD_I2C lcd(0, 0x27, LCD_SDA, LCD_SCL, 20, 400000);

// -----------------------------------------------------------------------------------------
void LCD_Display::init(void) {
  mot_a_is_power = true;
  mot_a_is_enabled = true;
  mot_b_is_power = true;
  mot_b_is_enabled = true;
  char msg[21];

  strcpy(msg, "RaspiCar MotDr ");
  itoaf(SOFTWARE_VERSION, msg+15, 3, 2, false);
  msg[15] = 'V';
  
  lcd.begin();
  lcd.print(msg);
  delay(100);
  mot_a_power(false);
  mot_a_enabled(false);
  mot_a_rpm(0);
  mot_b_power(false);
  mot_b_enabled(false);
  mot_b_rpm(0);
  lcd.setCursor(19, 3);
  lcd.write('V');
}

// -----------------------------------------------------------------------------------------
void LCD_Display::mot_a_enabled(bool state) {
  if (state != mot_a_is_enabled) {
    lcd.setCursor(LCD_X_MOTA_E, 3);
    if (state) lcd.write('*');
    else lcd.write('-');
    mot_a_is_enabled = state;
  }
}

// -----------------------------------------------------------------------------------------
void LCD_Display::mot_b_enabled(bool state) {
  if (state != mot_b_is_enabled) {
    lcd.setCursor(LCD_X_MOTB_E, 3);
    if (state) lcd.write('*');
    else lcd.write('-');
    mot_b_is_enabled = state;
  }
}

// -----------------------------------------------------------------------------------------
void LCD_Display::mot_a_power(bool state) {
  if (state != mot_a_is_power) {
    lcd.setCursor(LCD_X_MOTA_P, 3);
    if (state) lcd.write('*');
    else lcd.write('-');
    mot_a_is_power = state;
  }
}

// -----------------------------------------------------------------------------------------
void LCD_Display::mot_b_power(bool state) {
  if (state != mot_b_is_power) {
    lcd.setCursor(LCD_X_MOTB_P, 3);
    if (state) lcd.write('*');
    else lcd.write('-');
    mot_b_is_power = state;
  }
}

// -----------------------------------------------------------------------------------------
void LCD_Display::mot_a_rpm(uint32_t rpm) {
  lcd.setCursor(LCD_X_MOTA_RPM, 3);
  print_dec(rpm);
}

// -----------------------------------------------------------------------------------------
void LCD_Display::mot_b_rpm(uint32_t rpm) {
  lcd.setCursor(LCD_X_MOTB_RPM, 3);
  print_dec(rpm);
}

// -----------------------------------------------------------------------------------------

void LCD_Display::print_dec(int n) {
  char local_buf[5];
  if (n < 1000) lcd.write(' ');
  if (n < 100) lcd.write(' ');
  if (n < 10) lcd.write(' ');
  itoa(n, local_buf, 10);
  lcd.print(local_buf);
}

//-------------------------------------------------------------------------
void LCD_Display::show_voltage(uint16_t bat_voltage) {
  char buf[8];
  lcd.setCursor(LCD_X_BAT_VOLTAGE, 3);
  if (bat_voltage < 900) lcd.print(" < 9");
  else {
    itoaf(bat_voltage / 10, buf, 3, 1, false);
    lcd.print(buf);
  }
}

//-------------------------------------------------------------------------
void LCD_Display::shutdown(void) {
  lcd.setCursor(0, 0);
  lcd.print("Shut down ...       ");
}

//-------------------------------------------------------------------------
void LCD_Display::shutdown_timer(int i) {
  lcd.setCursor(16, 0);
  print_dec(i);
}

//-------------------------------------------------------------------------
void LCD_Display::clear(void) {
  lcd.setCursor(0, 0);
  lcd.print("                    ");
  lcd.setCursor(0, 1);
  lcd.print("                    ");
  lcd.setCursor(0, 2);
  lcd.print("                    ");
}

//-------------------------------------------------------------------------
void LCD_Display::print_title(const char buf[]) {
  int l = strlen(buf);
  lcd.setCursor(0, 0);
  for (int i = 0; i < 20; ++i) {
    if (i < l) lcd.write(buf[i]);
    else lcd.write(' ');
  }
}

//-------------------------------------------------------------------------
void LCD_Display::print_msg(const char buf[]) {
  int l = strlen(buf);
  lcd.setCursor(0, 1);
  lcd.print("                    ");
  lcd.setCursor(0, 2);
  lcd.print("                    ");
  lcd.setCursor(0, 1);
  if (l > 20) {
    for (int i = 0; i < 20; ++i) lcd.write(buf[i]);
    lcd.setCursor(0, 2);
    for (int i = 0; i < l - 20; ++i) lcd.write(buf[i+20]);
  } else {
    lcd.print(buf);
  }
}
