#define LED1 2  //thumbs up
#define LED2 3 //thumbs down
#define LED3 4 //open palm

void setup() {
  Serial.begin(9600);
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  digitalWrite(LED1, LOW);
  digitalWrite(LED2, LOW);
  digitalWrite(LED3, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    digitalWrite(LED1, LOW);
    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);

    if (c == '1') digitalWrite(LED1, HIGH);
    else if (c == '2') digitalWrite(LED2, HIGH);
    else if (c == '3') digitalWrite(LED3, HIGH);
  }
}