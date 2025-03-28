from rplidar import RPLidar
import numpy as np
import time
import serial
import spidev

lidar = RPLidar("/dev/ttyUSB0",baudrate=256000)

lidar.stop_motor()
lidar.stop()
time.sleep(1)
lidar.disconnect()
    
lidar.connect()
print (lidar.get_info())
lidar.start_motor()
time.sleep(1)

PreviousAngle = 30
PreviousSpeed = 1550
donnees_lidar = [0]*360 #création d'un tableau de 360 zéros

bus = 0
device = 1
flag_turn = 0

spi = spidev.SpiDev()
spi.open(bus, 1)
spi.max_speed_hz = 1000000
spi.mode = 0

# vitesse en ms
speed = 0
maxSpeed = 8
PWMStop = 7.7
SpeedRatioMax = 0.14

distanceMax = 0
distanceMoy = 0
Direction = 0
Backward = 0
# angle de la direction
angle = 0
maxangle = 45

# mise a zéro de la vitesse et de la direction
Working = 1
while 1:
    while Working:
        try:
            for scan in lidar.iter_scans(scan_type='express',max_buf_meas = 3650) : 
                for i in range(len(scan)) :
                    angle = min(359,max(0,359-int(scan[i][1]))) #scan[i][1] : angle 
                    donnees_lidar[angle]=scan[i][2]          #scan[i][2] : distance
                    
                newarray = np.array(donnees_lidar)
                distanceMoy = (((newarray[0] + newarray[339] + newarray[20])/3)/1000)
                speed = ((PWMStop+((newarray[0])/maxSpeed))/2.5)*500
                if((newarray[0])/maxSpeed > SpeedRatioMax):
                    speed = ((PWMStop+SpeedRatioMax)/2.5)*500
                distanceRecule = (newarray[0] + newarray[320] + newarray[40])/3
                if((newarray[0] or newarray[340] or newarray[20]) < 400):
                    speed = 1250
                    Backward = 1
                else:
                    Backward = 0
                if(newarray[0] < 0.5 and not Backward):
                    speed -= 20 # -= 15
                if(distanceMoy > distanceMax):
                    distanceMax = distanceMoy
                else:
                    if(distanceMax > distanceMoy + 1 and not Backward):
                        speed = 1550
                        distanceMax = distanceMoy
                Ddroite = 0
                Dgauche = 0

                for i in range(90): #85
                    Ddroite += (newarray[359-i]/1000) 
                    Dgauche += (newarray[i]/1000)                
                        
                Direction = Dgauche - Ddroite
                Correctif = newarray[60] - newarray[300]
                
                
                #Coef = 0.0058 * abs(Direction) + 0.2331 #Bon début
                Coef = -0.0001 * abs(Direction) * abs(Direction) + 0.0155 * abs(Direction) + 0.0441
                #Coef = 0.0077 * abs(Direction) + 0.1981 #Bon mais demande de ralentir plus dans les virages
                #Coef = 6 * 10**(-5)*abs(Direction)**2 + 0.0031* abs(Direction)+ 0.2529
                #print("Coef : ",Coef)
                if(Direction < 50 and Direction > 0):
                    if(Direction < 15):
                        angle = 0
                    else:
                        angle = maxangle * Coef
                else:
                    if(Direction >= -50 and Direction < 0):
                        if(abs(Direction) < 15):
                            angle = 0
                        else:
                            angle = -maxangle * Coef
                    else:
                        angle = Direction * 180/np.pi
                        speed -= 10
                print("Direction : ",Direction)
                Correctif = Correctif * 180/np.pi
                #angle = angle * 0.1 + Correctif * 0.9
                #angle = Correctif
                
                
                #print("angle : ",angle)
                if(angle > maxangle):
                    angle = maxangle
                if(angle < -maxangle):
                    angle = -maxangle
                #if(np.abs(angle) >= maxangle/2):
                    #speed -= 5
                
                angle += maxangle + 1
                #angle = 0.9 * PreviousAngle + 0.1 * angle #lissage exponentiel
                #speed = 0.2 * PreviousSpeed + 0.8 * speed #05 1 3 non 2 mieux
                SpeedVal = int(np.round(speed,0))
                AngleVal = int(np.round(angle,0))
                #print("Speed : ", speed)
                if((SpeedVal < 1550) and SpeedVal > 1500):
                    SpeedVal = 1550
                #SpeedVal = 1500
                print("Speed : ",SpeedVal)
                print("Angle : ", AngleVal)
                speed1 = int(SpeedVal / 100)
                speed2 = int(SpeedVal) - speed1*100
                speed1 += 200
                speed2 += 100
                message_tx = [speed1, speed2, AngleVal]
                message_rx = spi.xfer(message_tx)
                PreviousAngle = angle
                PreviousSpeed = SpeedVal
                
                try:
                    pass
                except RPLidarException:
                    lidar.clear_input()
                
        except KeyboardInterrupt:
            Working = 0
            message_tx = [215, 100, 30]
            message_rx = spi.xfer(message_tx)
            message_rx = spi.xfer(message_tx)
            
    lidar.stop_motor()
    lidar.stop()
    time.sleep(1)
    lidar.disconnect()
