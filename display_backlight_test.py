import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 1000)

pwm.start(100)
for x in range (100): 
	pwm.ChangeDutyCycle(x)
	print('PWM: ' +str(x))
	time.sleep(0.1)

pwm.stop()
GPIO.output(18, GPIO.LOW)
GPIO.setup(18, GPIO.IN)
