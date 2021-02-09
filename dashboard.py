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
max_counter = 5000

try:
    bus = can.interface.Bus(channel='can0', bustype='socketcan_native', can_filters=[{"can_id": 0, "can_mask": 100, "extended": True}])
except OSError:
    print('Cannot find CAN board.')
    exit()

try:
    pygame.display.init()
    pygame.font.init()
    (width, height) = (640, 480)
    screen = pygame.display.set_mode((width, height))
    pygame.mouse.set_visible(False)
    FPSCLOCK = pygame.time.Clock()
    #myfont = pygame.font.SysFont('MS Comic Sans', 62)
    datafont = pygame.font.Font('/home/pi/python/Righteous-Regular.ttf', 16)
    speedofont = pygame.font.Font('/home/pi/python/DSEG7ClassicMini-Bold.ttf', 96)
    myfont2 = pygame.font.Font('/home/pi/python/Righteous-Regular.ttf', 36)
except Exception as e:
    print ('Other error or exception')
    print(e)
    exit()
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
shift_point = 5650

map_names = ['Loud','Road','Test']
x = 50
y = 50
width = 40
height = 60
vel = 5
pointer_width = 5
counter = 0
update_screen_time = pygame.time.get_ticks()
screen_update_interval = 100 # minor information update interval in ms

# Define some colors
BLACK = ( 0, 0, 0)
WHITE = ( 255, 255, 255)
GREEN = ( 0, 255, 0)
RED = ( 255, 0, 0)
BLUE = ( 0, 0, 255)
YELLOW = ( 255, 255, 0)
SILVER = ( 192, 192, 192)
TURQUOISE = ( 64, 224, 208)

def fuel_guage():
    pygame.draw.rect(screen,GREEN,(10,150,35,205),2)
    img = datafont.render( 'Fuel' , True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (10,360)
    screen.blit(img,rect)
    pygame.draw.rect(screen, GREEN, pygame.Rect(10, 220, 35, 135))
        
def oil_pressure():
    pygame.draw.rect(screen,BLUE,(580,150,35,205),2)
    img = datafont.render( 'Oil P' , True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (580,360)
    screen.blit(img,rect)
    
def speed_function(speed):
    # SPEED gauge
    # Speedo 320,200
    img = speedofont.render(str(speed), True, WHITE )
    rect = img.get_rect()
    rect.topright = (320, 200)
    pygame.draw.rect(screen,WHITE,(100,180,230,140),3)
    screen.blit(img,rect)

def gear_function(gear):
    # Gear Indicator 450,200
    pygame.draw.rect(screen,WHITE,(440,180,100,140),3)
    # Gear Indicator
    img = speedofont.render(str(gear), True, YELLOW, BLACK)
    rect = img.get_rect()
    rect.topleft = (450, 200)
    screen.blit(img,rect)

def rpm_line_function(rpm):
    # RPM Range is 0-7500
    # screen width = 640
    # 640/7500 = 0.85pixels per rpm
    # RPM Seperator
    pygame.draw.line(screen, SILVER, (0,65), (640,65), 1)
    pygame.draw.rect(screen, BLACK, pygame.Rect(10, 10, (640), 50))
    # Less than shiftpoint minus 500 = Green
    if rpm <= shift_point - 500:
        colour = (0,255,0) # Green
    if rpm > (shift_point - 500) and rpm < shift_point:
        colour = (255,255,0) # Yellow
    if rpm >= shift_point:
        colour = (255,0,0) # Red
    # Drawing Rectangle
    pygame.draw.rect(screen, colour, pygame.Rect(10, 10, (rpm/12), 50))
    textsurface_RPM_bar = myfont2.render(str(rpm), True, WHITE)
    textRect_RPM_bar = textsurface_RPM_bar.get_rect()
    textRect_RPM_bar.center = (80, 30)
    screen.blit(textsurface_RPM_bar,textRect_RPM_bar)
# ------------------------------------------------------------------------
# ecu map      | IAT Temp C     | TPS %      | BARO        | Coil On
# Battery    v | CLT Temp C     | AFR        | Ign BTDC    | Inj dur
#
# 10            150              290          430           550

# Lower dash positions
lower_gauge_h = [5, 135, 270, 360, 500]
lower_gauge_v = [420, 455]

def lower_data(top, left, data):
    img = datafont.render( data , True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (lower_gauge_h[top], lower_gauge_v[left])
    screen.blit(img,rect)

def extra_lines():
    # Lower Details
    line_middle = ((lower_gauge_v[0] +lower_gauge_v[1])/2)+5
    pygame.draw.line(screen, SILVER, ( 0, lower_gauge_v[0]-10 ), ( 640, lower_gauge_v[0]-10 ), 1)
    pygame.draw.line(screen, SILVER, ( 0, line_middle ), ( 640, line_middle  ), 1)
    pygame.draw.line(screen, SILVER, ( 0, lower_gauge_v[1]+20 ), ( 640, lower_gauge_v[1]+20 ), 1)
    pygame.draw.line(screen, SILVER, ( lower_gauge_h[1]-5, lower_gauge_v[0]-10 ), (lower_gauge_h[1]-5, lower_gauge_v[1]+20), 1)
    pygame.draw.line(screen, SILVER, ( lower_gauge_h[2]-5, lower_gauge_v[0]-10 ), (lower_gauge_h[2]-5, lower_gauge_v[1]+20), 1) #(285,425), (285,475), 1)
    pygame.draw.line(screen, SILVER, ( lower_gauge_h[3]-5, lower_gauge_v[0]-10 ), (lower_gauge_h[3]-5, lower_gauge_v[1]+20), 1) #(425,425), (425,475), 1)
    pygame.draw.line(screen, SILVER, ( lower_gauge_h[4]-5, lower_gauge_v[0]-10 ), (lower_gauge_h[4]-5, lower_gauge_v[1]+20), 1) #(605,425), (605,475), 1)
 
def UpdateScreen_Loop():
    # Change this to intermittent changes
    lower_data(0, 0, 'ECU Map: ' + map_names[ECU_MAP] )
    lower_data(1, 0, 'IAT: ' + str(randint(5, 45)) + ' C') #map_names[ECU_MAP] )
    lower_data(2, 0, 'TPS: ' + str(TPS) + ' %')
    lower_data(3, 0, 'P: ' + str(BARO) + ' mbar')
    lower_data(4, 0, 'Coil On: ' + str(COIL_ON) + ' ms')
    lower_data(0, 1, 'Battery: ' + str(BATTERY) + ' v')
    lower_data(1, 1, 'CLT: ' + str(randint(0, 105)) + ' C') #CLT) + ' C')
    lower_data(2, 1, 'AFR1: ' + str(AFR1))
    lower_data(3, 1, 'Ign: ' + str(IGN_ADV) + ' BTDC')
    lower_data(4, 1, 'INJ: ' + str(INJ_DUR) + ' %')
    fuel_guage()
    oil_pressure()

    # Not used
    # egt_function(EGT)
    # afr2_function(AFR2)
    # status_function(STATUS)
    # error_function(ERRORS)
    # pri_inj_function(PRI_INJ)
    # sec_inj_function(SEC_INJ)
    # map_function(MAP)
        

done = False
run_count = 0


try:
  print('Main routine starting ')
  while counter < max_counter:
    if update_screen_time:
        if (pygame.time.get_ticks() - update_screen_time) > screen_update_interval:
            # only repaint the full screen every xms (See Screen_update_interval)
            screen.fill((0, 0, 0))
            UpdateScreen_Loop()
            extra_lines()
            update_screen_time = pygame.time.get_ticks()
    # Instant Update
    # *** Using dummy data atm ***
    speed_function(randint(100, 150)) #(SPEED)
    rpm_line_function(randint(900, 7500)) #RPM)
    gear_function(randint(1, 6)) #GEAR)
            
    if standalone==0:
        message = bus.recv()
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
            COIL_ON = round(cString*0.0488,2)
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
            SPEED = round(int(cString,2)*(2.25/256))
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
            BATTERY = round(cString/11,2)
            s += ' BATTERY=' + str(BATTERY) + 'v '
        
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

    pygame.display.flip()
    FPSCLOCK.tick(30) # set to 30 FPS
    counter += 1

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
