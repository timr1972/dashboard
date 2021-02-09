
#!/usr/bin/python3
#
# http://skpang.co.uk/catalog/pican2-canbus-board-for-raspberry-pi-2-p-1475.html
#
# Make sure Python-CAN is installed first http://skpang.co.uk/blog/archives/1220
#
# Updated to sniff packets from Emerald ECU (Use 5v on the CanBus, not 3.3!)

import can
import time
import os

# print('\n\rCAN Rx test')
# print('Bring up CAN0....')
#os.system("sudo /sbin/ip link set can0 down")
#time.sleep(0.1)
#os.system("sudo /sbin/ip link set can0 up type can bitrate 1000000 triple-sampling on restart-ms 100")
#os.system("sudo /sbin/ip link set can0 up type can bitrate 1000000 listen-only on restart-ms 100")
#os.system("sudo /sbin/ip link set can0 up type can bitrate 1000000 loopback on restart-ms 100")
time.sleep(0.1)	

try:	
	bus = can.interface.Bus(channel='can0', bustype='socketcan_native', can_filters=[{"can_id": 0, "can_mask": 100, "extended": True}])
except OSError:
	print('Cannot find CAN board.')
	exit()
	
#print('Ready')

# 1000 8 | 0 0 3 e8 3 e7 0 78
# 1001 8 | 0 0 0 0 0 df 0 df
# 1002 8 | 20 82 0 0 1a 2e 0 2e
# 1003 8 | 30 2c 0 a 0 0 2 84

def HexToDec(hexString):
  decValue = 0
  nextInt = 0
  #print(hexString)
  for x in range(len(str(hexString))):
    nextInt = str(hexString[x])
#    if nextInt >= 48 and nextInt <= 57:
#      nextInt = map(nextInt, 48, 57, 0, 9)
#    if nextInt >= 65 and nextInt <= 70:
#      nextInt = map(nextInt, 65, 70, 10, 15)
#    if nextInt >= 97 and nextInt <= 102:
#      nextInt = map(nextInt, 97, 102, 10, 15)
#    nextInt = constrain(nextInt, 0, 15)
#    decValue = (decValue * 16) + nextInt
    #print("-")
  return decValue

try:
    while True:
        message = bus.recv()
        # 0x1003
        #   * 0 Air Temp
        #   * 1 Coolant Temp
        #   * 2 Aux temp
        #   * 3 Ignition Advance
        #   * 4 Injector Duration
        #   * 5 Gear
        #   * 6 Selected Map
        #   * 7 Battery
        #
        if message.arbitration_id==0x1003:
            # Air is char 1
            cString = message.data[0]
            #AIR = HexToDec(str(cString))
            AIR = cString-40
            s = 'Air=' + str(AIR) + '*C '
            # CLT is char 2
            cString = message.data[1]
            CLT = cString-40
            s += ' CLT=' + str(CLT) + '*C '
            # AUX is not in use
            cString = message.data[2]
            AUX = cString-40
            s += ' AUX=' + str(AUX) + '*C '
            # Ignition Advance = 4
            cString = message.data[3]
            IGN_ADV = cString/2
            s += ' IGN_ADV=' + str(IGN_ADV) + 'BTDC '
            # Injector Duration = 5
            cString = message.data[4]
            INJ_DUR = cString
            s += ' INJ_DUR=' + str(IGN_ADV) + '% '
            # Gear = 6
            cString = message.data[5]
            GEAR = cString
            s += ' GEAR=' + str(GEAR)
            # ECU_MAP = 7
            cString = message.data[6]
            ECU_MAP = cString
            s += ' ECU_MAP=' + str(ECU_MAP)
            # Battery = 8
            cString = message.data[7]
            BATTERY = cString/11
            s += ' BATTERY=' + str(BATTERY)
            #print(s)
        if message.arbitration_id==0x1009:
            c = '{0:f} {1:x} {2:x} '.format(message.timestamp,message.arbitration_id, message.dlc)
            s=''
            for i in range(message.dlc ):
                s +=  '{0:x} '.format(message.data[i])
            print(' {}'.format(c+s))

except KeyboardInterrupt:
	#Catch keyboard interrupt
	#os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')	
