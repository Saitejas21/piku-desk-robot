/* Piku the sleepy bunny - a tiny touch-reactive desk friend.
   Board: ESP32C3 Dev Module; USB CDC On Boot: Enabled; flash: 4 MB.
   Libraries: Adafruit SSD1306 and Adafruit GFX (install dependencies too).
   Keep piku_faces.h beside this sketch; it contains the full-face artwork.
   OLED: 3V3, GND, SDA GPIO4, SCL GPIO5. TTP223: 3V3, GND, OUT GPIO3.
   TTP223 must use active-high MOMENTARY mode, not toggle mode.
   Source reviewed; not compiled or tested on physical hardware here.
*/
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <esp_system.h>
#include "piku_faces.h"

constexpr int SDA_PIN=4,SCL_PIN=5,TOUCH_PIN=3;
constexpr uint32_t SLEEP_AFTER_MS=60000;
Adafruit_SSD1306 face(128,64,&Wire,-1);
uint32_t bootAt=0,lastFrame=0,lastInteraction=0,lastTap=0,emotionStart=0;
uint32_t gazeStart=0,gazeWait=2500,blinkStart=0,blinkWait=3000,rawChanged=0;
bool rawTouch=false,touching=false,seenTap=false,hearts=false;
bool displayReady=false,sensorReady=false,waking=false;
PikuExpression gaze=PIKU_IDLE;

bool i2cPresent(uint8_t address) {
  Wire.beginTransmission(address);
  return Wire.endTransmission()==0;
}

void setup() {
  Serial.begin(115200);
  pinMode(TOUCH_PIN,INPUT_PULLDOWN);
  randomSeed(esp_random());
  Wire.begin(SDA_PIN,SCL_PIN);
  Wire.setTimeOut(30);
  uint8_t address=i2cPresent(0x3C)?0x3C:(i2cPresent(0x3D)?0x3D:0);
  if (!address || !face.begin(SSD1306_SWITCHCAPVCC,address,true,false)) {
    Serial.println("Piku: OLED not found. Check 3V3, GND, SDA=4, SCL=5.");
    return;
  }
  displayReady=true;
  face.clearDisplay();
  face.setRotation(0); // Change to 2 if the display is installed upside down.
  face.ssd1306_command(SSD1306_SETCONTRAST);
  face.ssd1306_command(0x60);
  face.display();
  bootAt=lastInteraction=emotionStart=gazeStart=blinkStart=millis();
  Serial.println("Piku ready. Leave the touch pad alone for two seconds.");
}

void loop() {
  const uint32_t now=millis();
  if (!displayReady) {delay(20);return;}
  if (!sensorReady && now-bootAt>=2000) sensorReady=true;
  const bool sensed=sensorReady && digitalRead(TOUCH_PIN)==HIGH;
  if (sensed!=rawTouch) {rawTouch=sensed;rawChanged=now;}
  if (now-rawChanged>=25 && touching!=rawTouch) {
    touching=rawTouch;
    if (touching) {
      waking=now-lastInteraction>=SLEEP_AFTER_MS;
      hearts=seenTap && now-lastTap<450;
      seenTap=true;
      lastTap=emotionStart=lastInteraction=now;
    } else {
      emotionStart=now; // Keep the smile for a moment after release.
      waking=false;
    }
  }
  if (touching) lastInteraction=now;
  if (now-lastFrame<33) return;
  lastFrame=now;
  if (now-gazeStart>=gazeWait) {
    gazeStart=now;gazeWait=random(2200,6000);
    gaze=static_cast<PikuExpression>(random(0,3));
  }
  if (now-blinkStart>=blinkWait+140) {
    blinkStart=now;blinkWait=random(2200,5200);
  }
  PikuExpression expression=gaze;
  if (now-lastInteraction>=SLEEP_AFTER_MS) expression=PIKU_SLEEP;
  else if (waking && now-emotionStart<300) expression=PIKU_SURPRISED;
  else if (touching && now-lastTap>=2000) expression=PIKU_SHY;
  else if (hearts && (touching || now-emotionStart<1200)) expression=PIKU_LOVE;
  else if (touching || now-emotionStart<1200) expression=PIKU_HAPPY;
  else if (now-blinkStart>=blinkWait) expression=PIKU_BLINK;
  face.clearDisplay();
  face.drawBitmap(0,0,PIKU_FACES[expression],128,64,SSD1306_WHITE);
  face.display();
  delay(1);
}
