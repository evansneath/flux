/*
Flux

A dynamic, real-time system for the emulation of various sources of audio
effects environments.

This Arduino code is to be used in a hardware control unit that will
provide a simple and convenient method of controlling the Flux software.

Author: Paul Musgrave
*/

const int leftSwitchPin = 18;                // left switch is on interrupt 5
const int rightSwitchPin = 21;               // right switch is on interrupt 2
const int enableSwitchPin = 19;              // enable switch is on interrupt 4
boolean leftFlag = false;
boolean rightFlag = false;
boolean enableFlag = false;
int leftState = LOW;
int rightState = LOW;
int enableState = LOW;

void setup() {
  Serial.begin(9600);
  pinMode(leftSwitchPin, INPUT);        // left pushbutton is input
  pinMode(enableSwitchPin, INPUT);      // enable / disable pushbutton is input
  pinMode(rightSwitchPin, INPUT);       // right pushbutton is input
  pinMode(13,OUTPUT);                   // LED is an output pin for testing
  // create interrupt routines for each pushbutton
  attachInterrupt(5, leftSwitchInterrupt, CHANGE);
  attachInterrupt(2, rightSwitchInterrupt, CHANGE);
  attachInterrupt(4, enableSwitchInterrupt, CHANGE);
}

void loop() {
  if (leftFlag == true){leftSwitch();}
  if (rightFlag == true){rightSwitch();}
  if (enableFlag == true){enableSwitch();}
}

int debounce(int pin, int currentState) {
  int temp = digitalRead(pin);          // read the value of the switch
  delay(100);                           // wait for switch to settle
  int state = digitalRead(pin);         // read value of switch again
  if (temp == state){
    if (state != currentState){
      return state;        // debounced if same value after waiting
    }
  }
  else{return currentState;}     // otherwise return the first value
}

void leftSwitchInterrupt() {
  if (leftState == LOW){
    leftState = debounce(leftSwitchPin, LOW);
    if (leftState == HIGH){
      leftFlag = true;
    }
  }
  else if (leftState == HIGH){
    leftState = debounce(leftSwitchPin, HIGH);
    if (leftState == LOW){
      leftFlag = true;
    }
  }
}

void leftSwitch(){
  leftFlag = false;
  Serial.print("L");
  Serial.println(leftState);
  /*
  if(switchState == 1){
     digitalWrite(13, HIGH);
  } else{
     digitalWrite(13, LOW); 
  } 
  */
}

void rightSwitchInterrupt() {
  if (rightState == LOW){
    rightState = debounce(rightSwitchPin, LOW);
    if (rightState == HIGH){
      rightFlag = true;
    }
  }
  else if (rightState == HIGH){
    rightState = debounce(rightSwitchPin, HIGH);
    if (rightState == LOW){
      rightFlag = true;
    }
  }
}

void rightSwitch(){
  rightFlag = false;
  Serial.print("R");
  Serial.println(rightState);
  /*
  if(switchState == 1){
     digitalWrite(13, HIGH);
  } else{
     digitalWrite(13, LOW); 
  } */
}

void enableSwitchInterrupt() {
  if (enableState == LOW){
    enableState = debounce(enableSwitchPin, LOW);
    if (enableState == HIGH){
      enableFlag = true;
    }
  }
  else if (enableState == HIGH){
    enableState = debounce(enableSwitchPin, HIGH);
    if (enableState == LOW){
      enableFlag = true;
    }
  }
}

void enableSwitch(){
  enableFlag = false;
  Serial.print("E");
  Serial.println(enableState);
  /*
  if(switchState == 1){
     digitalWrite(13, HIGH);
  } else{
     digitalWrite(13, LOW); 
  } 
  */
}
