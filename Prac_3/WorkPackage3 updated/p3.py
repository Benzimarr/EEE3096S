# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
counter = 0
guess = 0

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()


# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    global value
    end_of_game = False
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    # print out the scores in the required format
    num_range = 3
    if count < 3:
        num_range = count
    if count == 0:
        print("There are no scores")
    elif count == 1:
        print("There is 1 score")
    else:
        print("There are {} scores. Here are the top {}!".format(count,num_range))
    for i in range(num_range):
        print(str(i+1) + " - " + raw_data[i][0] + "took" + raw_data[i][1] + "guesses")
    pass


# Setup Pins
def setup():
    global PWM_acc, PWM_buz
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    GPIO.setup(LED_value[0],GPIO.OUT)
    GPIO.setup(LED_value[1],GPIO.OUT)
    GPIO.setup(LED_value[2],GPIO.OUT)

    GPIO.output(LED_value[0],0)
    GPIO.output(LED_value[1],0)
    GPIO.output(LED_value[2],0)

    GPIO.setup(3,GPIO.OUT)
    GPIO.setup(5,GPIO.OUT)
    # Setup PWM channels
    GPIO.setup(LED_accuracy,GPIO.OUT)
    GPIO.output(LED_accuracy,0)
    PWM_acc = GPIO.PWM(LED_accuracy,100000)
    PWM_acc.start(0)

    GPIO.setup(buzzer,GPIO.OUT)
    GPIO.output(buzzer,0)
    PWM_buz = GPIO.PWM(buzzer,1)
    
    # Setup debouncing and callbacks
    GPIO.setup(btn_submit,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(btn_submit,GPIO.FALLING,callback=btn_guess_pressed,bouncetime=500)
    
    GPIO.setup(btn_increase,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(btn_increase,GPIO.FALLING,callback=btn_increase_pressed,bouncetime=200)
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = eeprom.read_byte(0)
    sleep(0.01)
    # Get the scores
       
    scores = []
    for a in range(score_count):
        var = eeprom.read_block((i+1)*10,16)
        playerName = ""
        for b in range(15):
            if (var[b]!=0):
                playerName += chr(var[b])
            else:
                break
        score = var[15]
        scores.append([playerName,score])

    # convert the codes back to ascii
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    global guess
    score_count, scores = fetch_scores()
    score_count += 1
    # include new score
    name = input("Enter your name\n")
    new_score = [name, guess]
            
    # update total amount of scores
    eeprom.write_block(0,[score_count])
    scores.append(new_score)
    
    # sort
    scores.sort(key=lambda x: x[1])
        
    # write new scores
    for  a, b in enumerate(scores):
        data = []
        for letter in b[0]:
            data.append(ord(letter))
        while len(data) < 15:
            data.append(0)
        while len(data)>15:
            data.pop()
        data.append(b[1])
        eeprom.write_block((i+1)*10, data, 4)
    

# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    global counter
    counter += 1
    if counter == 1:
        GPIO.output(LED_value[0],1)
        GPIO.output(LED_value[1],0)
        GPIO.output(LED_value[2],0)
    elif counter == 2:
        GPIO.output(LED_value[0],0)
        GPIO.output(LED_value[1],1)
        GPIO.output(LED_value[2],0)
    elif counter == 3:
        GPIO.output(LED_value[0],1)
        GPIO.output(LED_value[1],1)
        GPIO.output(LED_value[2],0)
    elif counter == 4:
        GPIO.output(LED_value[0],0)
        GPIO.output(LED_value[1],0)
        GPIO.output(LED_value[2],1)
    elif counter == 5:
        GPIO.output(LED_value[0],1)
        GPIO.output(LED_value[1],0)
        GPIO.output(LED_value[2],1)
    elif counter == 6:
        GPIO.output(LED_value[0],0)
        GPIO.output(LED_value[1],1)
        GPIO.output(LED_value[2],1)
    elif counter == 7:
        GPIO.output(LED_value[0],1)
        GPIO.output(LED_value[1],1)
        GPIO.output(LED_value[2],1)
    else:
        counter = 0
        GPIO.output(LED_value[0],0)
        GPIO.output(LED_value[1],0)
        GPIO.output(LED_value[2],0)
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    global counter
    global guess
    global PWM_acc
    global PWM_buz
    global end_of_game
    begin = time.time()
    while GPIO.input(btn_submit) == GPIO.LOW:
        time.sleep(0.2)
    end = time.time()
    difference = end - begin
    if difference > 1:
        counter = 0
        GPIO.output(LED_value[0],0)
        GPIO.output(LED_value[1],0)
        GPIO.output(LED_value[2],0)
        PWM_acc.stop()
        PWM_buz.stop()
        guess = 0
        end_of_game = True
        welcome()
        print("Select an option:   H - View High Scores     P - Play Game       Q - Quit")
    else:
        if counter == value:
            counter = 0
            GPIO.output(LED_value[0],0)
            GPIO.output(LED_value[1],0)
            GPIO.output(LED_value[2],0)
            PWM_acc.stop()
            PWM_buz.start(0)
            PWM_buz.stop()
            save_scores()
            end_of_game = True
        else:
            accuracy_leds()
            trigger_buzzer()
            guess += 1



# LED Brightness
def accuracy_leds():
    global counter
    global PWM_acc
    global value

    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    
    if counter == 0:
        bright = int(round(((8 - value)/8)*100))
    elif counter < value:
        bright = int(round((counter/value)*100))
    else:
        bright = int(round(((8 - counter)/(8 - value))*100))
    PWM_acc.ChangeDutyCycle(bright)
    pass

# Sound Buzzer
def trigger_buzzer():
    global counter
    global PWM_buz
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    PWM_buz.start(50)
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    diff2 = abs(counter - value)
    if diff2 <4:
        if diff2 == 1:
            freq = 4
        elif diff2 == 2:
            freq = 2
        elif diff2 == 3:
            freq = 1
        PWM_buz.ChangeFrequency(freq)
    else:
        PWM_buz.stop()
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
