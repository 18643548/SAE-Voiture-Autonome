//////////////////////////////////////////////////////////////////////////////////////////////////////////////
//
//Programme pour gérer les moteurs en fonction du message reçu, et fait l'aquisition de données graces aux 
//capteurs avant de les envoyer.
// 
//Finir la fonction d'envoie des données.
//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <Servo.h>
#include <SPI.h>
#include <Wire.h>

Servo Moteur;                      // creation de l'objet Moteur de type Servo pour controller le moteur
Servo Direction;                   //creation de l'objet Direction de type Servo pour controller la direction

int Tab[2];                        // tab contenant la vitesse et la direction ([0] = vitesse ; [1] = direction
int Valeurs[6];                    // contient les valeurs récupérées des capteurs
const int sensorPin[] = {A0, A1};  // Broches pour les capteurs
float distance[2];                 // Tableaux de distances
const int AVERAGE_OF = 50;         // Nombre de lectures pour la moyenne
int command[3]; 
int reading = 0;

int message;
int i = 0;
int j = 0;
int l = 0;
bool flag = false;
volatile byte indx =0;
int VitesseMax = 10;
int AngleOldValue;
int Vitesse_ant = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Wire.begin();
  pinMode(MISO, OUTPUT);                  // have to send on master in so it set as output
  SPCR |= _BV(SPE);                       //Turn on SPI in Slave Mode
  SPI.attachInterrupt();                  //Interrupt ON is set for SPI commnucation
  
  Moteur.attach(9);                       //affectation du pin 9 a Moteur
  Direction.attach(10);                   //affectation du pin 10 a direction
  Moteur.write(90);                       //init moteurs
  delay(2000);
}

ISR (SPI_STC_vect) {                      //Interrupt routine function 
  message = SPDR;
  //Serial.println(message);
  if(SPDR = 100){
    flag = true;
  }
  if(SPDR != 0 and flag){
    command[l] = SPDR;
    if(l == 3){
      l = 0;
      if(command[0] == 230 || command[1] == 230 || command[2] == 230){
        Tab[0] = 1500;
        Tab[1] = 0;
      }
      if(command[0]< 90){
        Tab[1] = command[0]-1;
        if(command[1] <200){
          Tab[0] = (command[2] - 200)*100 + command[1] - 100;
        } else {
          Tab[0] = (command[2] - 100) + (command[1] - 200)*100;
        }
      }
      if(command[1]< 90){
        Tab[1] = command[1]-1;
        if(command[0] <200){
          Tab[0] = (command[2] - 200)*100 + command[0] - 100;
        } else {
          Tab[0] = (command[2] - 100) + (command[0] - 200)*100;
        }
      }
      if(command[2]< 90){
        Tab[1] = command[2]-1;
        if(command[1] <200){
          Tab[0] = (command[0] - 200)*100 + command[1] - 100;
        } else {
          Tab[0] = (command[0] - 100) + (command[1] - 200)*100;
        }
      }
      //Tab[0] = 1300;
      Serial.print("Vitesse : ");
      Serial.println(Tab[0]);
      Serial.print("Direction : ");
      Serial.println(Tab[1]);
      flag = false;
    }else{
      l++;
    }
  }

}

int BackSensor(){
   Wire.beginTransmission(112);         // transmit to device #112 (0x70)
  // the address specified in the datasheet is 224 (0xE0)
  // but i2c adressing uses the high 7 bits so it's 112
  Wire.write(byte(0x00));               // sets register pointer to the command register (0x00)
  Wire.write(byte(0x51));               // command sensor to measure in "inches" (0x50)

  Wire.endTransmission();               // stop transmitting

  // step 2: wait for readings to happen
  delay(70);                            // datasheet suggests at least 65 milliseconds

  // step 3: instruct sensor to return a particular echo reading
  Wire.beginTransmission(112);         // transmit to device #112
  Wire.write(byte(0x02));              // sets register pointer to echo #1 register (0x02)
  Wire.endTransmission();              // stop transmitting

  // step 4: request reading from sensor
  Wire.requestFrom(112, 2);            // request 2 bytes from slave device #112

  // step 5: receive reading from sensor
  if (2 <= Wire.available()) {        // if two bytes were received
    reading = Wire.read();            // receive high byte (overwrites previous reading)
    reading = reading << 8;           // shift high byte to be high 8 bits
    reading |= Wire.read();           // receive low byte as lower 8 bits
    return reading;
  }
}

void avancer (int valeur){
  
  if(valeur < 1500){
    Moteur.write(1500);
    Direction.write(90);
    delay(20);
    Moteur.write(valeur);
    delay(250);
    //Moteur.write(valeur);
    //delay(500);
  } else {
    if(((valeur > Vitesse_ant + 50) || (valeur < Vitesse_ant - 50))&& (Vitesse_ant != 0)){
      Moteur.write(Vitesse_ant);
    } else {
        Moteur.write(valeur);
        Vitesse_ant = valeur;
    }
  }
  //Moteur.write(1200);
  }

void tourner (int valeur){
  valeur = valeur + 70; 
  Direction.write(valeur);
  }

float readDistance(int sensor) {
float voltage_temp_average = 0;

  // Moyennage des lectures du capteur pour réduire le bruit
  for (int i = 0; i < AVERAGE_OF; i++) {
    int sensorValue = analogRead(sensorPin[sensor]);
    voltage_temp_average += sensorValue * (3.3 / 1023.0);
    delay(5);  // Laisse un peu de temps entre les lectures pour la stabilité
  }
  voltage_temp_average /= AVERAGE_OF;
  // Calcul de la distance en fonction de la tension pour le capteur GP2Y0A21YK0F

 return (4.50322854691145 *(voltage_temp_average*voltage_temp_average) - 17.9788686376543 * voltage_temp_average + 21.7396028761264);
}

void loop() {
  // put your main code here, to run repeatedly:
  avancer(Tab[0]);
  tourner(Tab[1]);
  //Valeurs[0] = readDistance(A0); //lecture capteur gauche
  //Valeurs[1] = readDistance(A1); //lecture capteur droite
}
