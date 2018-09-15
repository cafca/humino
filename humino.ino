#include <DS1307RTC.h>
#include <Time.h>
#include <TimeLib.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

int output_value;
tmElements_t tm;
const int chipSelect = 10;
const int power = 3;
String dataString;
String timestamp;

void setup() {
  pinMode(power, OUTPUT);
  digitalWrite(power, LOW);
  Serial.begin(9600);
  Serial.println("# Setup...");
  while (!Serial) ; // wait for serial
  delay(2000);

  Serial.print("Initializing SD card...");
  if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    while (1);
  } else {
    Serial.println("card initialized.");
  }
}

void loop() {
  Serial.print("Reading ");
  // Switch transistor  
  digitalWrite(power, HIGH);
  delay(300);
  // dataString will contain each measurement in CSV format
  dataString = "";
  dataString += dt();
  for (int sensorPin = A0; sensorPin <= A3; sensorPin++) {
    Serial.print(sensorPin);
    Serial.print("-");
    output_value = analogRead(sensorPin);
    dataString += ',';
    dataString += output_value;
  }
  digitalWrite(power, LOW);
  writeLog(dataString);
  Serial.println(dataString);
  delay(300000);
}

void writeLog(String dataString) {
  File dataFile = SD.open("HUMINO.CSV", FILE_WRITE);

  if (dataFile) {
    dataFile.println(dataString);
    dataFile.close();
  } else {
    Serial.println("error opening humino.log");
  }
}

String dt() {
  // Return ISO8601 formatted datetime string
  String rv = "";
  RTC.read(tm);
  rv += tmYearToCalendar(tm.Year);
  rv += '-';
  rv += pad2(tm.Month);
  rv += '-';
  rv += pad2(tm.Day);
  rv += 'T' + pad2(tm.Hour) + ':' + pad2(tm.Minute) + ':' + pad2(tm.Second);
  return rv;
}

String pad2(int number) {
  // Pad numbers to two chars  
  String rv = "";
  if (number >= 0 && number < 10) {
    rv += "0";
  }
  rv += number;
  return rv;
}
