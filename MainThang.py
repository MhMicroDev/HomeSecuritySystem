#!/usr/bin/python

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*


# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

#import
import RPi.GPIO as GPIO
import time
import threading
from threading import Thread

GPIO.setmode(GPIO.BOARD)
  
# Define GPIO to LCD mapping
LCD_RS = 37
LCD_E  = 35
LCD_D4 = 33 
LCD_D5 = 31
LCD_D6 = 29
LCD_D7 = 23
LED_ON = 10

# System Bool
systemActivated = True

# Initial Passcode
passcode = '1738'

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line 

# Timing constants
E_PULSE = 0.00005
E_DELAY = 0.00005

def wrongPass():
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string("Wrong passcode", 1)
    time.sleep(1)

def igniteAlarm():
    GPIO.setup(40, GPIO.OUT)
    for i in range(6):
        GPIO.output(40, 1)
        time.sleep(0.5)
        GPIO.output(40, 0)
        time.sleep(0.5)  
            
def obstacleHere(pin_1, pin_2, pin_3, pin_4):
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_1, GPIO.IN)
    GPIO.setup(pin_2, GPIO.IN)
    GPIO.setup(pin_3, GPIO.IN)
    GPIO.setup(pin_4, GPIO.IN)

    try:
        while True:
            i = GPIO.input(pin_1)
            j = GPIO.input(pin_2)
            k = GPIO.input(pin_3)
            l = GPIO.input(pin_4)

            if i == 0 or j == 0 or k == 0 or l == 0:
                print("Obstacle Detected")
                time.sleep(0.1)
                igniteAlarm()
                systemActivated = False
                
            else:
                print("No Obstacle")
                systemActivated = True
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        GPIO.cleanup()

def getMatrixCode(myBool):
    MATRIX = [ [1,2,3,'A'],
           [4,5,6,'B'],
           [7,8,9,'C'],
           ['*',0,'#','D'] ]

    ROW = [7,11,13,15]
    COL = [12,16,18,22]

    code = ''
    

    for j in range(4):
        GPIO.setup(COL[j], GPIO.OUT)
        GPIO.output(COL[j], 1)

    for i in range(4):
        GPIO.setup(ROW[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)


    while len(code) < 4 and myBool != False:
        for j in range(4):
            GPIO.output(COL[j], 0)

            for i in range(4):
                if GPIO.input(ROW[i]) == 0:
                    time.sleep(0.5)
                    
                    print MATRIX[i][j]
                    
                    code += str(MATRIX[i][j])
                    print "code is:", code

                    lcd_byte(LCD_LINE_1, LCD_CMD)
                    lcd_string("Enter code: "+code, 1)
                    print(myBool)

                    #if len(code) == 4:
                        #break

               # else:
                    #pass
        
                #while GPIO.input(ROW[i]) == 0:
                    #pass
            
            GPIO.output(COL[j], 1)
    
    else:
        
        myBool = False
        print(code)
        print(myBool)
        """
        if code == passcode:
          systemActivated = False
          print("Test")
          lcd_byte(LCD_LINE_1, LCD_CMD)
          lcd_string("Welcome Master", 1)

          time.sleep(3)
          
          lcd_byte(LCD_LINE_1, LCD_CMD)
          lcd_string("Press A to activate", 1)

          lcd_byte(LCD_LINE_2, LCD_CMD)
          lcd_string("Press B to activate", 1)

        else:

          lcd_byte(LCD_LINE_1, LCD_CMD)
          lcd_string("Wrong passcode", 1)
          obstacleHere(38, 36, 32, 3)
          
        """
    return code
  
def main():

  # Main program block
  
  # Using BOARD GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  GPIO.setup(LED_ON, GPIO.OUT) # Backlight enable
  
  # Initialise display
  lcd_init()

  time.sleep(2)

  while True:
  
      lcd_byte(LCD_LINE_1, LCD_CMD)
      lcd_string("Enter code:", 1)

      something = getMatrixCode(True)
      
      lcd_byte(LCD_LINE_1, LCD_CMD)
      lcd_string("Enter code: " + something,1)
      time.sleep(2)

      #something = getMatrixCode(True)
      #print(something)

      if something == passcode:
          lcd_byte(LCD_LINE_1, LCD_CMD)
          lcd_string("Welcome master", 1)
          time.sleep(3)
          GPIO.cleanup()
          break

      else:
          wrongPass()
          time.sleep(1)
          #Thread(target = obstacleHere(38, 36, 32, 3)).start()
          #GPIO.cleanup()
          
          
      
  GPIO.cleanup()

  
def lcd_init():

 # Initialise display  lcd_byte(0x33,LCD_CMD)
  lcd_byte(0x32,LCD_CMD)
  lcd_byte(0x28,LCD_CMD)
  lcd_byte(0x0C,LCD_CMD)  
  lcd_byte(0x06,LCD_CMD)
  lcd_byte(0x01,LCD_CMD)  

def lcd_string(message,style):
  # Send string to display
  # style=1 Left justified
  # style=2 Centred
  # style=3 Right justified

  if style==1:
    message = message.ljust(LCD_WIDTH," ")  
  elif style==2:
    message = message.center(LCD_WIDTH," ")
  elif style==3:
    message = message.rjust(LCD_WIDTH," ")

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)    
  GPIO.output(LCD_E, True)  
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)  
  time.sleep(E_DELAY)      

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)    
  GPIO.output(LCD_E, True)  
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)  
  time.sleep(E_DELAY)   

if __name__ == '__main__':
  try:
    Thread(target = main).start()
    Thread(target = obstacleHere(38, 36, 32, 3)).start()
  except KeyboardInterrupt:
      GPIO.cleanup()

