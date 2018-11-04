#include <SPI.h>

const int MEASUREMENT_DELAY = 5 * 60 * 1000;
const int NUM_SENSORS = 16;

int measurement;
String outputString;

void setup() {

  Serial.begin(9600);
  while (!Serial) ; // wait for serial
  delay(500);
  Serial.println("status setup complete");
}

void loop() {
  Serial.println("status measuring... ");

  outputString = "";
  for (int sensorPin = 0; sensorPin < NUM_SENSORS; sensorPin++) {
    measurement = analogRead(sensorPin);
    if (measurement > 999) {
      measurement = 999;
    }
    outputString += measurement;
    if (sensorPin != (NUM_SENSORS - 1)) {
      outputString += ',';
    }
  }
  Serial.print("measurement ");
  Serial.println(outputString);
  delay(MEASUREMENT_DELAY);
}
