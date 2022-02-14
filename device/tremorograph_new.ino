#include <SparkFun_ADXL345.h>         // SparkFun ADXL345 Library
#include <ArduinoJson.h>

ADXL345 adxl = ADXL345();             // USE FOR I2C COMMUNICATION

int interruptPin = 2;                 // Setup pin 2 to be the interrupt pin (for most Arduino Boards)
volatile int a;

int b;
volatile byte interruptFlag = false;
byte startFlag = false;
byte standbyFlag = true;
volatile long count = 0;
byte conFlag = false;
int dataRate;
int gRange;
volatile int duration;
boolean rateFlag;
boolean rangeFlag;

void setup(){
  
  Serial.begin(115200);                 // Start the serial terminal
  Serial.println("Tremorograph ADXL345 v1.0");
  Serial.println();
  adxl.powerOn();                     // Power on the ADXL345
  adxl.dataReadyINT(0);

//  adxl.setRangeSetting(2);           // Give the range settings
                                      // Accepted values are 2g, 4g, 8g or 16g
                                      // Higher Values = Wider Measurement Range
                                      // Lower Values = Greater Sensitivity

 
// Setting all interupts to take place on INT1 pin
//adxl.setImportantInterruptMapping(1, 1, 1, 1, 1);     // Sets "adxl.setEveryInterruptMapping(single tap, double tap, free fall, activity, inactivity);" 
                                                        // Accepts only 1 or 2 values for pins INT1 and INT2. This chooses the pin on the ADXL345 to use for Interrupts.
                                                        // This library may have a problem using INT2 pin. Default to INT1 pin.
  

//  adxl.dataReadyINT(1);    // Turn on Interrupts for each mode (1 == ON, 0 == OFF)
//adxl.setRate(100);
//  double a = adxl.getRate();
//  Serial.print("Rate: ");
//  Serial.println(a, DEC);

  adxl.setInterruptMapping(ADXL345_INT_DATA_READY_BIT, ADXL345_INT1_PIN );
//pinMode(interruptPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(interruptPin), ADXL_ISR, RISING);   // Attach Interrupt
  pinMode(33, OUTPUT);
}




void configuration(void)
  {  // json for settings example: {"g-range":2,"d-rate":100}; {"stop":10}
    if (Serial.available()) 
      {
    //    while (Serial.available() > 0)
    //      {
    //        char i = Serial.read();
    //        Serial.print(i);
    //      }
       
          
          
          
          // Allocate the JSON document
        DynamicJsonDocument doc(40);
        // Read the JSON document from the "link" serial port
        DeserializationError err = deserializeJson(doc, Serial);
        if (err == DeserializationError::Ok) 
          {
            if (doc["g-range"] && doc["d-rate"])          //     {"g-range":2,"d-rate":100}
              {
                gRange = doc["g-range"].as<int>();
                dataRate = doc["d-rate"].as<int>();
                rangeFlag = rateFlag = true;
                adxl.setRangeSetting(gRange);
                adxl.setRate(dataRate);
                StaticJsonDocument<10> doc;
                doc["rate"] = adxl.getRate();;
                serializeJson(doc, Serial);
                conFlag = true;
//                while (Serial.available() == 0)
//                  {
//                    delay(100);
//                  }
                deserializeJson(doc, Serial);
              }
            else if (doc["start"])    //{"start":15}
              {
                duration = doc["start"].as<int>();
                count = dataRate * duration;
                startFlag = true;
                StaticJsonDocument<10> doc;
                doc["count"] = count;
                serializeJson(doc, Serial);
//                while (Serial.available() == 0)
//                  {
//                    delay(100);
//                  }
                deserializeJson(doc, Serial);
                standbyFlag = false;
                adxl.dataReadyINT(1);    // Turn on Interrupts for each mode (1 == ON, 0 == OFF)
              }
            else if (doc["stop"])        // {"stop":1}
              {
                adxl.dataReadyINT(0);
                count = 0;
                startFlag = false;
                StaticJsonDocument<10> doc;
                doc["manualstop"] = 1;
                serializeJson(doc, Serial);
//                while (Serial.available() == 0)
//                  {
//                    delay(100);
//                  }
                deserializeJson(doc, Serial);      
              }
            else if (doc["led"])
              {
                digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
                StaticJsonDocument<20> doc;
                doc["led"] = digitalRead(LED_BUILTIN);
                serializeJson(doc, Serial);
//                while (Serial.available() == 0)
//                  {
//                    delay(100);
//                  }
                }
            else 
              {
                Serial.println("Incorrect JSON data: wrong query or count");
              }
          } 
        else 
          {
            // Print error to the "debug" serial port
            Serial.print("deserializeJson() returned ");
            Serial.println(err.c_str());
            // Flush all bytes in the "link" serial port buffer
            while (Serial.available() > 0)
             {
              Serial.read();
              }
            Serial.println("...waiting for configuration settings...");
          }
      }
  }


void loop(){
  configuration(); 
  if (standbyFlag == true){
    return;
  }
  else if (startFlag && interruptFlag){
    int x,y,z;   
    adxl.readAccel(&x, &y, &z);         // Read the accelerometer values and store them in variables declared above x,y,z
    StaticJsonDocument<200> doc;
    doc["count"] = count;
    doc["x"] = x;
    doc["y"] = y;
    doc["z"] = z;
    serializeJson(doc, Serial);
    interruptFlag = false;
  }
  else if (startFlag == false){
    standbyFlag = true;
    adxl.dataReadyINT(0);    // Turn on Interrupts for each mode (1 == ON, 0 == OFF)
  }
}


void ADXL_ISR() {
  if(count <= 0)
    {
      startFlag = false;
    }
  else
    {
//    if (digitalRead(LED_BUILTIN) == LOW)
//    {
//      digitalWrite(LED_BUILTIN, HIGH);
//    }
//    else 
//    {
//      digitalWrite(LED_BUILTIN, LOW);
//    }
      interruptFlag = true;
      count--;
    } 
}
