// CAN Send Example
//

#include <mcp_can.h>
#include <SPI.h>

MCP_CAN CAN0(53);     // Set CS to pin 10 for UNO

void setup()
{
  Serial.begin(115200);

  // Initialize MCP2515 running at 16MHz with a baudrate of 500kb/s and the masks and filters disabled.
  if(CAN0.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) == CAN_OK) {
    Serial.println("MCP2515 Initialized Successfully!");
  } else {
    Serial.println("Error Initializing MCP2515...");
  }
  CAN0.setMode(MCP_NORMAL);   // Change to normal mode to allow messages to be transmitted
}

byte data[8] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07};
int joy_value;
void loop()
{
  joy_value = analogRead(0);
  //data[0] = map(joy_value, 0, 1023, 0, 255);
  data[0] = random(0, 255);
  // send data:  ID = 0x100, Standard CAN Frame, Data length = 8 bytes, 'data' = array of data bytes to send
  byte sndStat = CAN0.sendMsgBuf(0x1009, 1, 8, data);
  if(sndStat == CAN_OK){
    Serial.println("Message Sent Successfully! ");
  } else {
    Serial.println("Error Sending Message...");
  }
  data[0] = random(0, 255);
  data[1] = 0;
  data[2] = 0;
  data[3] = 0;
  data[4] = 0;
  data[5] = 0;
  data[6] = 50;
  data[7] = 5;
  sndStat = CAN0.sendMsgBuf(0x1000, 1, 8, data);
  delay(50);
  
  data[0] = 0;
  data[1] = 0;
  data[2] = random(0, 105);
  data[3] = 0;
  data[4] = 0;
  data[5] = 0;
  data[6] = 50;
  data[7] = 5;
  sndStat = CAN0.sendMsgBuf(0x1001, 1, 8, data);
  delay(50);
  
  data[0] = random(0, 105); // IAT
  data[1] = random(0, 105); // CLT
  data[2] = 0; // Aux
  data[3] = 0; // Ign Adv
  data[4] = 0; // Ign Dur
  data[5] = random(0, 6); // Gear
  data[6] = random(0, 2); // ECU Map
  data[7] = random(10, 12); // Battery
  sndStat = CAN0.sendMsgBuf(0x1003, 1, 8, data);
  delay(50);
}

/*
 * On RPI This works in Python
 * bus = can.interface.Bus(channel='can0', bustype='socketcan_native', can_filters=[{"can_id": 0, "can_mask": 100, "extended": True}])
 * pre-up /sbin/ip link set can0 type can bitrate 500000 triple-sampling on
 * 
 */
