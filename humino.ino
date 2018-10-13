#include <SPI.h>

const int POWER = 3;
const int MEASUREMENT_DELAY = 5 * 60 * 1000;
int output_value;
String dataString;

void setup() {
  pinMode(POWER, OUTPUT);
  digitalWrite(POWER, LOW);
  Serial.begin(9600);
  while (!Serial) ; // wait for serial
  delay(2000);
  Serial.println("status setup complete");
}

void loop() {
  Serial.println("status measuring... ");
  // Switch transistor  
  digitalWrite(POWER, HIGH);
  delay(5);
  // dataString will contain each measurement in CSV format
  dataString = "";
  for (int sensorPin = A0; sensorPin <= A5; sensorPin++) {
    output_value = analogRead(sensorPin);
    if (output_value > 999) {
      output_value = 999;
    }
    dataString += output_value;
    if (sensorPin != A5) {
      dataString += ',';
    }
  }
  digitalWrite(POWER, LOW);
  Serial.print("measurement ");
  Serial.println(dataString);
  delay(MEASUREMENT_DELAY);
}
