/* 
 * read state of pir sensor hc-sr501
 * 
 * this program based on scetch from 
 * Kristian Gohlke / krigoo (_) gmail (_) com / http://krx.at,
 * http://playground.arduino.cc//Code/PIRsense
 * and
 * 
 *  
 */

//the time we give the sensor to calibrate (10-60 secs according to the datasheet)
unsigned int calibrationTime = 30;        

int pirPin = 2;    //the digital pin connected to the PIR sensor's output
int ledPin = 13;

/////////////////////////////
//SETUP
void setup()
{
	Serial.begin(9600);
	pinMode(pirPin, INPUT);
	pinMode(ledPin, OUTPUT);
	digitalWrite(pirPin, LOW);

	//give the sensor some time to calibrate
	for(int i = 0; i < calibrationTime; i++)
	{
		digitalWrite(ledPin, HIGH);
		delay(100);
		digitalWrite(ledPin, LOW);
		delay(900);
	}
	delay(50);
}

////////////////////////////
//LOOP
void loop()
{
	if(digitalRead(pirPin) == HIGH)
	{
		digitalWrite(ledPin, HIGH);   //the led visualizes the sensors output pin state
		int Calc = millis()/1000 % 60;
		/*
		 * sensor ist firing,
		 * change value every second to see sensor firing for calibration and debugging
		 * if you have more than one sensor, you can take another value than 100 for differentiation
		 */
		Serial.println ((int) 100 + millis()/1000 % 60, DEC);
		delay(1000);
	}

	if(digitalRead(pirPin) == LOW)
	{       
		digitalWrite(ledPin, LOW);  //the led visualizes the sensors output pin state
		Serial.println (0, DEC);
		delay(1000);
	}
}
