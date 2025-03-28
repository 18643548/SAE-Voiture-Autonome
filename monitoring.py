import psutil
import subprocess
import RPi.GPIO as GPIO
import os, signal
import threading
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(29, GPIO.IN)
GPIO.setup(31, GPIO.IN)

Start = 2
  
script_name = "voiture.py"
            

def button():
    global Start
    while(1):
        if GPIO.input(29) == 0:
            Start = 1
            print("on")
        if GPIO.input(31) == 0:
            Start = 0
            print("off")
        time.sleep(1)

def prog():
    global Start
    while 1:
        iteration = 0
        for process in psutil.process_iter(attrs=['pid','name','cmdline']):
            try:
                if 'python' in process.info['name'].lower() or 'python' in ''.join(process.info['cmdline']).lower():
                    if script_name in ''.join(process.info['cmdline']):
                        iteration = iteration + 1
            except(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if(iteration == 0 and Start == 1):
            process = subprocess.run(["python", script_name])
            print("Relaunch")
        if(Start == 0):
            process.terminate()
            #pid = process.pid
            #os.kill(pid, signal.SIGTERM)
        time.sleep(1)
     

thread_button = threading.Thread(target = button)
thread_button.start()
time.sleep(1)    
thread_prog = threading.Thread(target= prog)
thread_prog.start()

while 1 :
    try : 
        pass
    except KeyboardInterrupt: #récupération du CTRL+C
        print("arrêt du programme")
             

    thread_button.join()
    thread_prog.join()
