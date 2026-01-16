#ifndef __COMMAND_DECODER__
#define __COMMAND_DECODER__

#include "RaspiCar-rp2040-motor_driver.h"
#include "motors.h"
#include "display.h"
#include "battery.h"

#define BUF_SIZE 100
#define VALID_LIMIT 999999

class CommandDecoder {
	private:
		char buf[BUF_SIZE];
		uint8_t buf_pnt = 0;
		char local_buf[12];
		int32_t get_int(uint8_t *pnt);
		void show_info(void);
		void decode_motor_command(uint8_t pnt);
		void decode_get_command(uint8_t pnt);
		void decode_bat_command(uint8_t pnt);
		void decode_display_command(uint8_t pnt);
		void decode_config_command(uint8_t pnt); 
		
	public:
		void init(void);
		bool add_to_buffer(char c);
		void decode_command(void);
};

#endif 
