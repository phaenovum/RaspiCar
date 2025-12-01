#include "util.h"


/* itoaf ---------------------------------------------------------------------------------------------------
* Converts an integer to a string including basic formatting information
* positions -> total number of digits to be reserved 
* dec_point -> number of positions from the right for a decimal point. 0 -> no decimal point
*/
void itoaf(int32_t value, char *s, uint8_t digits, const uint8_t dec_point, bool lead_zero) {
  bool neg = false;
  uint8_t count, blank_flag = 0;
  const uint32_t start_denom[] = {0, 10, 100, 1000, 10000, 100000, 1000000};
  uint32_t denominator;

  if (value < 0) {
    neg = true;
    value = -value;
  };
  if (digits > 7) digits = 7;
  if (digits < 1) digits = 1;
  denominator = start_denom[digits - 1];
  while (digits > 0) {
    count = value / denominator;
    value -= count * denominator;
    if ((digits == dec_point + 1) && !blank_flag) {
      if (neg) *s++ = ('-');
      else *s++ = (' ');
      blank_flag = 1;
    }
    if (digits == dec_point) {
      *s++ = ('.');
    }
    if ((count == 0) && (blank_flag == 0)) {
      if (lead_zero) *s++ = ('0');
      else *s++ = (' ');
    } else {
      if (blank_flag == 0) {
        if (neg) *s++ = ('-');
        else *s++ = (' ');
      };
      *s++ = ('0' + count);
      blank_flag = 1;
    };
    --digits;
    denominator /= 10;
  };
  *s = '\0';
}
