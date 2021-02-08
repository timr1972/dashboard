# Import the pygame library and initialise the game engine
import pygame
import time
import sys
import os
import can
from random import seed
from random import randint

seed(1)

# if set to 1 do not use CanBus
standalone = 0
max_counter = 2000

try:
    bus = can.interface.Bus(channel='can0', bustype='socketcan_native', can_filters=[{"can_id": 0, "can_mask": 100, "extended": True}])
except OSError:
    print('Cannot find CAN board.')
    exit()

try:
    pygame.display.init()
    (width, height) = (640, 480)
    screen = pygame.display.set_mode((width, height))
    pygame.mouse.set_visible(False)
    pygame.font.init()
    FPSCLOCK = pygame.time.Clock()
    #myfont = pygame.font.SysFont('MS Comic Sans', 62)
    datafont = pygame.font.Font('/home/pi/python/Righteous-Regular.ttf', 16)
    speedofont = pygame.font.Font('/home/pi/python/DSEG7ClassicMini-Bold.ttf', 96)
    myfont2 = pygame.font.Font('/home/pi/python/Righteous-Regular.ttf', 36)
except OSError:
    print('Pygame initialisation issue.')
    raise
    exit()
    
# Line 1 config
AIR = 10
CLT = 10
AUX = 0
IGN_ADV = 5
INJ_DUR = 5
GEAR = 0
ECU_MAP = 2
BATTERY = 12
RPM = 0
MAP = 0
BARO = 0
TPS = 0
EGT = 0
SPEED = 0
AFR1 = 0
AFR2 = 0

map_names = ['Loud','Road','Test']
x = 50
y = 50
width = 40
height = 60
vel = 5
pointer_width = 5
counter = 0

# Define some colors
BLACK = ( 0, 0, 0)
WHITE = ( 255, 255, 255)
GREEN = ( 0, 255, 0)
RED = ( 255, 0, 0)
BLUE = ( 0, 0, 255)
YELLOW = ( 255, 255, 0)
SILVER = ( 192, 192, 192)
TURQUOISE = ( 64, 224, 208)

def HexToDec(hexString):
  decValue = 0
  nextInt = 0
  #print(hexString)
#  for x in range(len(str(hexString))):
#    nextInt = str(hexString[x])
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

def speed_function(speed):
    # SPEED gauge
    img = speedofont.render(str(speed), True, WHITE, BLACK)
    rect = img.get_rect()
    rect.topright = (320, 200)
    screen.blit(img,rect)
    #pygame.draw.circle(screen, RED, [120, 240], 120, 3)
    #pygame.draw.line(screen, BLUE, startpoint, current_endpoint, pointer_width)
    #textsurface_SPEED = myfont.render(str(run_count), True, RED, BLACK)
    #textRect_SPEED = textsurface_SPEED.get_rect()
    #textRect_SPEED.center = (120, 320)
    #screen.blit(textsurface_SPEED,textRect_SPEED)

def gear_function(gear):
    # SPEED gauge
    pygame.draw.rect(screen,WHITE,(440,180,100,140),3)
    img = speedofont.render(str(gear), True, YELLOW, BLACK)
    rect = img.get_rect()
    rect.topleft = (450, 200)
    screen.blit(img,rect)
    #pygame.draw.circle(screen, RED, [120, 240], 120, 3)
    #pygame.draw.line(screen, BLUE, startpoint, current_endpoint, pointer_width)
    #textsurface_SPEED = myfont.render(str(run_count), True, RED, BLACK)
    #textRect_SPEED = textsurface_SPEED.get_rect()
    #textRect_SPEED.center = (120, 320)
    #screen.blit(textsurface_SPEED,textRect_SPEED)
    
def rpm_function():
    # RPM gauge
    pygame.draw.circle(screen, BLUE, [500, 240], 120, 3)
    pygame.draw.line(screen, RED, startpoint_2, current_endpoint_2, pointer_width)
    textsurface_RPM = myfont2.render(str(run_count*100), True, RED, BLACK)
    textRect_RPM = textsurface_RPM.get_rect()
    textRect_RPM.center = (500, 320)
    screen.blit(textsurface_RPM,textRect_RPM)

def rpm_line_function(rpm):
    # RPM Range is 0-7500
    # screen width = 640
    # 640/7500 = 0.85pixels per rpm
    shift_point = 5650
    
    # Less than shiftpoint minus 500 = Green
    if rpm <= shift_point - 500:
        colour = (0,255,0) # Green
    if rpm > (shift_point - 500) and rpm < shift_point:
        colour = (255,255,0) # Yellow
    if rpm >= shift_point:
        colour = (255,0,0) # Red
    # Drawing Rectangle
    pygame.draw.rect(screen, colour, pygame.Rect(10, 10, (rpm/12), 50))
    textsurface_RPM_bar = myfont2.render(str(rpm), True, BLACK)
    textRect_RPM_bar = textsurface_RPM_bar.get_rect()
    textRect_RPM_bar.center = (80, 35)
    screen.blit(textsurface_RPM_bar,textRect_RPM_bar)

def ecuMap_function(map_number):
    img = datafont.render('ECU Map: ' + map_names[map_number], True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (10, 430)
    screen.blit(img,rect)

def iat_function(iat):
    img = datafont.render('Air Temp: ' + str(iat) + ' C', True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (10, 455)
    screen.blit(img,rect)

def clt_function(clt):
    img = datafont.render('CLT Temp: ' + str(clt) + ' C', True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (150, 430)
    screen.blit(img,rect)

def battery_function(battery):
    img = datafont.render('Battery: ' + str(round(battery,2)) + ' v', True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (150, 455)
    screen.blit(img,rect)

def tps_function(tps):
    img = datafont.render('TPS: ' + str(tps) + ' %', True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (290, 430)
    screen.blit(img,rect)

def baro_function(baro):
    img = datafont.render('BARO: ' + str(baro) + ' mB', True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (290, 455)
    screen.blit(img,rect)

def coil_function(coil_on):
    img = datafont.render('Coil On: ' + str(coil_on) + ' ms', True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (430, 430)
    screen.blit(img,rect)

def afr1_function(afr1):
    img = datafont.render('AFR: ' + str(afr1), True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (430, 455)
    screen.blit(img,rect)

def air_function(air):
    img = datafont.render('IAT: ' + str(air) + ' ms', True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (550, 430)
    screen.blit(img,rect)

def ign_adv_function(ign_adv):
    img = datafont.render('Ign: ' + str(ign_adv) + ' BTDC', True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (550, 455)
    screen.blit(img,rect)

def extra_lines():
    pygame.draw.line(screen, SILVER, (0,425), (640,425), 1)
    pygame.draw.line(screen, SILVER, (0,450), (640,450), 1)
    pygame.draw.line(screen, SILVER, (0,475), (640,475), 1)
    pygame.draw.line(screen, SILVER, (145,425), (145,475), 1)
    pygame.draw.line(screen, SILVER, (285,425), (285,475), 1)
    pygame.draw.line(screen, SILVER, (425,425), (425,475), 1)
    pygame.draw.line(screen, SILVER, (605,425), (605,475), 1)
        
startpoint = pygame.math.Vector2(120, 240) # Center Point of arc
startpoint_2 = pygame.math.Vector2(500, 240) # Center Point of arc
endpoint = pygame.math.Vector2(80, 0) # Length of the arm
# 0 = Point to the right
# 90 = point down, the rest you can work out
angle = 135 # Start Angle 90+45
done = False
run_count = 0
   
try:
  print('Main routine starting ')
  while counter < max_counter:
    # The current endpoint is the startpoint vector + the
    # rotated original endpoint vector.
    # current_endpoint = startpoint + endpoint.rotate(angle)
    # current_endpoint_2 = startpoint_2 + endpoint.rotate(angle)
    # pygame.draw.line(screen, BLACK, startpoint, current_endpoint, 3)
    # pygame.draw.line(screen, BLACK, startpoint_2, current_endpoint_2, 3)
    screen.fill((0, 0, 0))
    
    if standalone==0:
        message = bus.recv()
        #print(message)
        # 0x1000
        #  0:1 RPM
        #  2:3 MAP (Manifold Air Pressure)  
        #  4:5 BARO
        #  6 TPS %
        #  7 Coil on time
        #
        if message.arbitration_id==0x1000:
            # 
            # RPM is 0:1
            #
            aString = '{:08b}'.format(message.data[0])       # MSB
            bString = '{:08b}'.format(message.data[1])[::-1] # LSB
            cString = aString + bString
            RPM = round(int(cString,2),0)
            s = 'RPM=' + str(RPM) + ' '
            #
            # MAP 2:3 (Not connected so always 100Kpa)
            #
            aString = '{:08b}'.format(message.data[2])       # MSB
            bString = '{:08b}'.format(message.data[3])[::-1] # LSB
            cString = aString + bString
            MAP = round(int(cString,2)/10,0)
            s = 'MAP=' + str(MAP) + ' KPa '
            #
            # BARO 4:5 is built into the Emerald
            #
            aString = '{:08b}'.format(message.data[2])       # MSB
            bString = '{:08b}'.format(message.data[3])[::-1] # LSB
            cString = aString + bString
            BARO = round(int(cString,2)+1000,0)
            s = 'BARO=' + str(BARO) + ' mB '
            #
            # TPS is char 6
            #
            cString = message.data[6]
            TPS = cString
            s = 'TPS=' + str(TPS) + ' % '
            #
            # Coil On Time is char 7
            #
            cString = message.data[7]
            COIL_ON = cString*0.0488
            s = 'Coil On=' + str(COIL_ON) + ' ms '
        
        # 0x1001
        #   0:1 EGT
        #   2:3 Road Speed
        #   4:5 AFR/Lambda 1
        #   6:7 AFR/Lambda 2
        #
        if message.arbitration_id==0x1001:
        	#
        	# EGT
        	#
            aString = '{:08b}'.format(message.data[0])       # MSB
            bString = '{:08b}'.format(message.data[1])[::-1] # LSB
            cString = aString + bString
            EGT = round(int(cString,2),0)
            s = 'EGT=' + str(EGT) + ' C '
            #
            # SPEED 
            #
            aString = '{:08b}'.format(message.data[2])       # MSB
            bString = '{:08b}'.format(message.data[3])[::-1] # LSB
            cString = aString + bString
            SPEED = round(int(cString,2)*(2.25/256),0)
            s = 'SPEED=' + str(SPEED) + ' MPH '
            #
            # AFR1
            #
            aString = '{:08b}'.format(message.data[4])       # MSB
            bString = '{:08b}'.format(message.data[5])[::-1] # LSB
            cString = aString + bString
            AFR1 = round(int(cString,2)/10,2)
            s = 'AFR1=' + str(AFR1) + ' '
            #
            # AFR2
            #
            aString = '{:08b}'.format(message.data[6])       # MSB
            bString = '{:08b}'.format(message.data[7])[::-1] # LSB
            cString = aString + bString
            AFR2 = round(int(cString,2)/10,2)
            s = 'AFR2=' + str(AFR2) + ' '
        
        # 0x1002
        #   0:1 Status
        #   2:3 Error
        #   4:5 Primary Injection
        #   6:7 Secondary Injection
        #
        if message.arbitration_id==0x1002:
        	#
        	# Status
        	#
            aString = '{:08b}'.format(message.data[0])       # MSB
            bString = '{:08b}'.format(message.data[1])[::-1] # LSB
            cString = aString + bString
            STATUS = int(cString,2)
            s = 'STATUS=' + str(STATUS)
            #
            # Errors 
            #
            aString = '{:08b}'.format(message.data[2])       # MSB
            bString = '{:08b}'.format(message.data[3])[::-1] # LSB
            cString = aString + bString
            ERROR = int(cString,2)
            s = 'ERROR=' + str(ERROR)
            #
            # Pri_inj
            #
            aString = '{:08b}'.format(message.data[4])       # MSB
            bString = '{:08b}'.format(message.data[5])[::-1] # LSB
            cString = aString + bString
            pri_inj = round(int(cString,2)* 1.526e-3,2)
            s = 'pri_inj=' + str(pri_inj) + ' '
            #
            # Sec_inj
            #
            aString = '{:08b}'.format(message.data[6])       # MSB
            bString = '{:08b}'.format(message.data[7])[::-1] # LSB
            cString = aString + bString
            sec_inj = round(int(cString,2)* 1.526e-3,2)
            s = 'sec_inj=' + str(sec_inj) + ' '
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
            s += ' GEAR ' + str(GEAR) + ' '
            # ECU_MAP = 7
            cString = message.data[6]
            ECU_MAP = cString
            s += ' ECU_MAP ' + map_names[ECU_MAP] + ' '
            # Battery = 8
            cString = message.data[7]
            BATTERY = cString/11
            s += ' BATTERY=' + str(BATTERY) + 'v '
        
        # 0x1000
        rpm_line_function(RPM)
        # map_function(MAP)
        baro_function(BARO)
        tps_function(TPS)
        coil_function(COIL_ON)
        
        # 0x1001
        #egt_function(EGT)
        speed_function(SPEED)
        afr1_function(AFR1)
        #afr2_function(AFR2)
        
        # 0x1002
        # status_function(STATUS)
        # error_function(ERRORS)
        # pri_inj_function(PRI_INJ)
        # sec_inj_function(SEC_INJ)
        
        # 0x1003
        air_function(AIR)
        clt_function(CLT)
        #aux_function(AUX)
        ign_adv_function(IGN_ADV)
        #inj_dur_function(INJ_DUR)
        gear_function(GEAR)
        ecuMap_function(ECU_MAP)
        battery_function(BATTERY)
    else : # Standalone Mode
      # Demo mode so provide data            
      speed_function(randint(0, 150))
      rpm_line_function(randint(1000, 7500))
      gear_function(randint(0, 6))
      ecuMap_function(3)
      tps_function(randint(0, 99))
      clt_function(randint(0, 105))
      air_function(randint(0, 35))
      #time.sleep(0.5)
    
    # Always draw the lines
    extra_lines()

    pygame.display.flip()
    FPSCLOCK.tick(60)
    counter += 1
    # print(str(counter))

except KeyboardInterrupt:
  print('\n'), counter

except Exception as e:
  print ('Other error or exception')
  print(e)

finally:
#  GPIO.cleanup()
  print('\nFinished ' + str(counter))
  pygame.quit()
  sys.exit()
