# Import the pygame library and initialise the game engine
from dash_config import *
import pygame
import RPi.GPIO as GPIO
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
(width, height) = (640, 480)

try:
    bus = can.interface.Bus(channel='can0', bustype='socketcan_native', can_filters=[{"can_id": 0, "can_mask": 100, "extended": True}])
except OSError:
    print('\nCannot find CAN board.')
    exit()

try:
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((width, height))
    pygame.mouse.set_visible(False)
    FPSCLOCK = pygame.time.Clock()
    #myfont = pygame.font.SysFont('MS Comic Sans', 62)
    datafont = pygame.font.Font('/home/pi/python/fonts/Righteous-Regular.ttf', 16)
    speedofont = pygame.font.Font('/home/pi/python/fonts/DSEG7ClassicMini-Bold.ttf', 96)
    myfont2 = pygame.font.Font('/home/pi/python/fonts/Righteous-Regular.ttf', 36)
    update_screen_time = pygame.time.get_ticks()
    # Set up display dimming
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Power trigger
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP) # TBD
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP) # TBD
    pwm = GPIO.PWM(18, 1000)
    pwm.start(80) # Start at 80%, range is 0-100
except Exception as e:
    print ('\nOther error or exception')
    print(e)
    exit()
except OSError:
    print('\nPygame initialisation issue.')
    raise
    exit()

def set_brightness(brightness):
    #Valid range is 0-100, lower = darker!
    pwm.ChangeDutyCycle(brightness)

def warning_lights(tl, bm, tr):
    # tl = turn left
    # tr = turn right
    # bm = beam
    x = (width/2) - 150
    y = 340
    # Left Green Arrow
    pygame.draw.polygon(screen, OLIVE, ((x, y), (x+30, y-30), (x+30, y-10), (x+70, y-10), (x+70, y+10), (x+30, y+10), (x+30, y+30), (x, y)), width = 1)
    # Right Green Arrow
    x = (width/2) + 150
    pygame.draw.polygon(screen, OLIVE, ((x, y), (x-30, y-30), (x-30, y-10), (x-70, y-10), (x-70, y+10), (x-30, y+10), (x-30, y+30), (x, y)), width = 1)
    img = myfont2.render( 'BEAM' , True, BLUE)
    rect = img.get_rect()
    rect.center = (width/2,y)
    screen.blit(img,rect)

def fuel_guage():
    # Outline
    pygame.draw.rect(screen,GREEN,(50,400,300,35),2)
    # Label
    img = datafont.render( 'Fuel' , True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (50,400)
    screen.blit(img,rect)
    # Level
    #pygame.draw.rect(screen, GREEN, pygame.Rect(10, 350-200, 35, 200)) # Full
    pygame.draw.rect(screen, GREEN, pygame.Rect(50, 400, 150, 35)) # Half
    #pygame.draw.rect(screen, GREEN, pygame.Rect(10, 350-5, 35, 5)) # Empty

def oil_pressure():
    # Outline
    pygame.draw.rect(screen,BLUE,(580,150,35,200),2)
    # Label
    img = datafont.render( 'Oil P' , True, TURQUOISE, BLACK)
    rect = img.get_rect()
    rect.topleft = (580,360)
    screen.blit(img,rect)
    #Level
    #pygame.draw.rect(screen, BLUE, pygame.Rect(580, 350-200, 35, 200)) # Full
    pygame.draw.rect(screen, BLUE, pygame.Rect(580, 350-100, 35, 100)) # Half
    #pygame.draw.rect(screen, BLUE, pygame.Rect(580, 350-5, 35, 5)) # Empty
    
def speed_function(speed):
    # Speed Gauge surround
    pygame.draw.rect(screen,WHITE,(140,140,230,140),3)
    # SPEED gauge
    # Speedo 150,150
    img = speedofont.render(str(speed), True, WHITE, BLACK )
    rect = img.get_rect()
    rect.topleft = (150, 150)
    screen.blit(img,rect)

def gear_function(gear):
    # Gear change surround
    pygame.draw.rect(screen,BLACK,(540,150,100,140),3)
    # Gear Indicator
    # Gear Indicator 550,150
    img = speedofont.render(str(gear), True, YELLOW, BLACK)
    rect = img.get_rect()
    rect.topleft = (550, 150)
    screen.blit(img,rect)

def rpm_line_function(rpm):
    # RPM Range is 0-7500
    # screen width = 640
    # 7500 / 800 = 9.375
    # RPM Seperator
    pygame.draw.line(screen, SILVER, (0,65), (800,65), 1)
    pygame.draw.rect(screen, BLACK, pygame.Rect(0, 10, (800), 50))
    # Less than shiftpoint minus 500 = Green
    if rpm <= shift_point - 500:
        colour = (0,255,0) # Green
    if rpm > (shift_point - 500) and rpm < shift_point:
        colour = (255,255,0) # Yellow
    if rpm >= shift_point:
        colour = (255,0,0) # Red
    # Drawing Rectangle
    pygame.draw.rect(screen, colour, pygame.Rect(0, 10, (rpm/9.375), 50))
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
    lower_data(1, 0, 'IAT: ' + str(IAT) + ' C') # str(randint(5, 45))
    lower_data(2, 0, 'TPS: ' + str(TPS) + ' %')
    lower_data(3, 0, 'P: ' + str(BARO) + ' mbar')
    lower_data(4, 0, 'Coil On: ' + str(COIL_ON) + ' ms')
    lower_data(0, 1, 'Battery: ' + str(BATTERY) + ' v')
    lower_data(1, 1, 'CLT: ' + str(CLT) + ' C')
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
  print('\nMain routine starting, this is now an infinite loop until GIO26 is pulled low...')
  while 1!=0:
    if GPIO.input(26) == 0: # Pulled Low
        #counter = max_counter
        print('\nLocally forced exit.')
        break

    if update_screen_time:
        if (pygame.time.get_ticks() - update_screen_time) > screen_update_interval:
            # only repaint the full screen every xms (See Screen_update_interval)
            screen.fill((0, 0, 0))
            UpdateScreen_Loop()
            # warning_lights(0, 0, 0)
            extra_lines()
            update_screen_time = pygame.time.get_ticks()
        # Instant Update
        speed_function(SPEED) #randint(100, 150)) #(SPEED)
        rpm_line_function(RPM) #randint(900, 7500)) #RPM)
        gear_function(GEAR) #randint(1, 6)) #GEAR)
            
    if standalone==0:
        message = bus.recv()
        # print(message)
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
            # removed for now to test ARduino canbus
            # RPM = round(int(cString,2),0)
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
            aString = '{:08b}'.format(message.data[4])       # MSB
            bString = '{:08b}'.format(message.data[5])[::-1] # LSB
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
            # IAT is char 1
            cString = message.data[0]
            IAT = cString-40
            s = 'IAT=' + str(IAT) + '*C '
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
            if GEAR<0 or GEAR>6:
                GEAR = 0
            s += ' GEAR ' + str(GEAR) + ' '
            # ECU_MAP = 7
            cString = message.data[6]
            ECU_MAP = cString
            if ECU_MAP <0 or ECU_MAP >2:
                ECU_MAP=2
            s += ' ECU_MAP ' + map_names[ECU_MAP] + ' '
            # Battery = 8
            cString = message.data[7]
            BATTERY = round(cString/11,2)
            s += ' BATTERY=' + str(BATTERY) + 'v '
        # 0x1009
        #   * 0 Key State
        #   * 1 Left Turn
        #   * 2 Right Turn
        #   * 3 Beam
        #   * 4 Lights
        #   * 5 Oil Pressure
        #   * 6 Fuel Level
        #   * 7 Spare
        #
        if message.arbitration_id==0x1009 or message.arbitration_id==0xFF0009:
            # Key_sate is char 0
            # cString = message.data[0]
            # KEY_STATE = cString
            # s = 'KEY_STATE=' + str(KEY_STATE)
            
            # added for test
            # Joystick value is 0 to 254 (Analogue read)
            # 7500 / 254 = 
            cString = message.data[0]
            # multiply and round to no digits
            RPM = round(cString)*30
            # LEFT_TURN is char 1
            cString = message.data[1]
            #LEFT_TURN = cString
            #s = 'Left Turn=' + str(LEFT_TURN)
            # RIGHT_TURN is char 2
            cString = message.data[2]
            #RIGHT_TURN = cString
            #s = 'Right Turn=' + str(LEFT_TURN)
            # BEAM is char 3
            cString = message.data[3]
            #BEAM = cString
            #s = 'Beam=' + str(BEAM)
            # LIGHTS is char 4
            cString = message.data[4]
            #LIGHTS = cString
            #s = 'Lights=' + str(Lights)
            # OIL_PRESSURE is char 5
            cString = message.data[5]
            #OIL_PRESSURE = cString
            #s = 'Oil Pressure=' + str(OIL_PRESSURE)
            # FUEL_LEVEL is char 6
            cString = message.data[6]
            #FUEL_LEVEL = cString
            #s = 'Fuel Level=' + str(FUEL_LEVEL)
            cString = message.data[7]
        
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
    FPSCLOCK.tick(120) # set to 30 FPS
    #counter += 1

except KeyboardInterrupt:
    print('\nKeyboard Interrupt')
    pwm.stop()
    GPIO.setup(18, GPIO.IN)

except Exception as e:
    pwm.stop()
    GPIO.setup(18, GPIO.IN)
    print ('\nOther error or exception')
    print(e)

finally:
    print('\nExiting and cleaning up.')
    pygame.quit()
    pwm.stop()
    GPIO.setup(18, GPIO.IN)
    sys.exit()
