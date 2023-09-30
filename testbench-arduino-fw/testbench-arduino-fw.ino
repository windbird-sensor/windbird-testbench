#define VBAT_PORT A0
#define VCAP_PORT A1
#define VMAIN_PORT A2
#define VLED_PORT A3
#define VBATPROT_PORT A4
#define VAUX_PORT A5

#define PULSE_PORT 12

#define VOLTAGE(port) analogRead(port) * 5.0 / 1023.0

void setup() {
  Serial.begin(9600);
  pinMode(PULSE_PORT, OUTPUT);
  digitalWrite(PULSE_PORT, LOW);
  while (!Serial) {}
}

void loop() {
  if (Serial.available() > 0) {
      switch(Serial.read()) {
        case 'h': // hello
          Serial.println("hello");
          break;
        case 'b': // Vbat
          Serial.println(VOLTAGE(VBAT_PORT));
          break;
        case 'p': // Vbatprot
          Serial.println(VOLTAGE(VBATPROT_PORT));
          break;
        case 'c': // Vcap
          Serial.println(VOLTAGE(VCAP_PORT));
          break;
        case 'm': // Vmain
          Serial.println(VOLTAGE(VMAIN_PORT));
          break;
        case 'x': // Vaux
          Serial.println(VOLTAGE(VAUX_PORT));
          break;
        case 'l': // Vled
          Serial.println(VOLTAGE(VLED_PORT));
          break;
        case 's': // pulse
          int i;
          delay(500);
          for (i=0; i<10;i++) {
            digitalWrite(PULSE_PORT, HIGH);
            delay(10);
            digitalWrite(PULSE_PORT, LOW);
            delay(10);
          }
          break;
      }
  }
}
