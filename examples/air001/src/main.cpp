#include <Arduino.h>

void setup() {
  pinMode(PB_1, OUTPUT);
  pinMode(PB_0, OUTPUT);
  pinMode(PB_3, OUTPUT);
}


void loop() {
  digitalWrite(PB_3, LOW);
  digitalWrite(PB_1, HIGH);
  delay(200);
  digitalWrite(PB_1, LOW);
  digitalWrite(PB_0, HIGH);
  delay(200);
  digitalWrite(PB_0, LOW);
  digitalWrite(PB_3, HIGH);
  delay(200);
}
