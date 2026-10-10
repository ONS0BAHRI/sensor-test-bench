/*
 * Firmware du banc de test MPU6050 — ESP32 (Arduino core)
 *
 * Rôle : exécuter les ordres du PC (servo, vibreur, acquisition) et renvoyer des mesures
 * horodatées. Toute l'analyse est faite en Python côté PC.
 *
 * Câblage :
 *   MPU6050 VCC -> 3V3      GND -> GND      SDA -> GPIO21      SCL -> GPIO22
 *   Servo signal -> GPIO18  (alimentation 5 V séparée, masses communes)
 *   Vibreur : GPIO19 -> 1 kΩ -> base 2N2222 ; moteur entre 3V3 et collecteur ;
 *             diode 1N4007 en parallèle du moteur (cathode côté +)
 *
 * Protocole série (921600 bauds, une commande par ligne) :
 *   ID?            -> ID 0x68
 *   FS?            -> FS 500
 *   VER?           -> VER 1.0.0
 *   SERVO <deg>    -> OK                (-80..80, 0 = capteur à plat)
 *   VIB <hz>       -> OK                (0..100, 0 = arrêt)
 *   READ <n>       -> DATA <n> / n lignes "t_us,ax,ay,az,gx,gy,gz,temp" (brut) / END
 *   STEP <deg> <n> -> idem READ ; le servo reçoit l'ordre à l'échantillon n/10
 *   erreur         -> ERR <message>
 *
 * Bibliothèque à installer : ESP32Servo (Kevin Harrington).
 */
#include <Wire.h>
#include <ESP32Servo.h>

const char *FW_VERSION = "1.0.0";
const int PIN_SDA = 21, PIN_SCL = 22, PIN_SERVO = 18, PIN_VIB = 19;
const uint8_t MPU_ADDR = 0x68;
const uint32_t SAMPLE_PERIOD_US = 2000;  // 500 Hz
const float SERVO_ZERO = 90.0;           // position du servo pour laquelle le capteur est à plat
const int READ_MAX = 4000;

struct Sample {
  uint32_t t;
  int16_t v[7];  // ordre des registres : ax ay az temp gx gy gz
};
Sample buf[READ_MAX];  // 72 ko : tient dans la RAM de l'ESP32, pas dans celle d'un Arduino Uno

Servo servo;
float vibFreq = 0;

// ---------------------------------------------------------------- MPU6050 (registres bruts)
bool writeReg(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.write(val);
  return Wire.endTransmission() == 0;
}

int readReg(uint8_t reg) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return -1;
  if (Wire.requestFrom(MPU_ADDR, (uint8_t)1) != 1) return -1;
  return Wire.read();
}

bool mpuInit() {
  return writeReg(0x6B, 0x01)    // PWR_MGMT_1 : réveil, horloge PLL gyro X
      && writeReg(0x19, 0x01)    // SMPLRT_DIV : 1 kHz / (1 + 1) = 500 Hz
      && writeReg(0x1A, 0x01)    // CONFIG : filtre interne (DLPF) à 184 Hz
      && writeReg(0x1B, 0x00)    // GYRO_CONFIG : ±250 °/s
      && writeReg(0x1C, 0x00);   // ACCEL_CONFIG : ±2 g (16384 LSB/g)
}

bool readSample(Sample &s) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);  // ACCEL_XOUT_H : 14 octets consécutifs
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom(MPU_ADDR, (uint8_t)14) != 14) return false;
  for (int i = 0; i < 7; i++) {
    uint8_t hi = Wire.read(), lo = Wire.read();
    s.v[i] = (int16_t)((hi << 8) | lo);
  }
  return true;
}

// ---------------------------------------------------------------- actionneurs
void setServo(float angle) {
  float pos = constrain(SERVO_ZERO + angle, 0.0f, 180.0f);
  servo.writeMicroseconds(500 + (int)(pos * 1900.0f / 180.0f));  // 500..2400 µs
}

void updateVib(uint32_t now) {
  if (vibFreq <= 0) {
    digitalWrite(PIN_VIB, LOW);
    return;
  }
  uint32_t period = (uint32_t)(1e6f / vibFreq);
  digitalWrite(PIN_VIB, (now % period) < period / 2 ? HIGH : LOW);  // tout-ou-rien, rapport 50 %
}

// ---------------------------------------------------------------- acquisition
void acquire(int n, bool isStep, float angle) {
  uint32_t next = micros();
  for (int i = 0; i < n; i++) {
    while ((int32_t)(micros() - next) < 0) updateVib(micros());
    if (isStep && i == n / 10) setServo(angle);
    buf[i].t = micros();
    if (!readSample(buf[i])) {
      Serial.println("ERR lecture I2C impossible (capteur absent ou câble débranché)");
      return;
    }
    next += SAMPLE_PERIOD_US;
  }
  // Envoi après acquisition : l'écriture série ne perturbe pas la cadence d'échantillonnage
  Serial.printf("DATA %d\n", n);
  for (int i = 0; i < n; i++) {
    const int16_t *v = buf[i].v;
    Serial.printf("%lu,%d,%d,%d,%d,%d,%d,%d\n", (unsigned long)buf[i].t,
                  v[0], v[1], v[2], v[4], v[5], v[6], v[3]);
  }
  Serial.println("END");
}

// ---------------------------------------------------------------- commandes
void handle(String line) {
  line.trim();
  if (line.length() == 0) return;
  int sp = line.indexOf(' ');
  String cmd = sp < 0 ? line : line.substring(0, sp);
  String args = sp < 0 ? "" : line.substring(sp + 1);

  if (cmd == "ID?") {
    int id = readReg(0x75);  // WHO_AM_I
    if (id < 0) Serial.println("ERR capteur absent sur le bus I2C");
    else Serial.printf("ID 0x%02X\n", id);
  } else if (cmd == "FS?") {
    Serial.printf("FS %lu\n", 1000000UL / SAMPLE_PERIOD_US);
  } else if (cmd == "VER?") {
    Serial.printf("VER %s\n", FW_VERSION);
  } else if (cmd == "SERVO") {
    float a = args.toFloat();
    if (args.length() == 0 || a < -80 || a > 80) Serial.println("ERR angle hors plage [-80, 80]");
    else { setServo(a); Serial.println("OK"); }
  } else if (cmd == "VIB") {
    float f = args.toFloat();
    if (args.length() == 0 || f < 0 || f > 100) Serial.println("ERR frequence hors plage [0, 100]");
    else { vibFreq = f; updateVib(micros()); Serial.println("OK"); }
  } else if (cmd == "READ") {
    int n = args.toInt();
    if (n < 1 || n > READ_MAX) Serial.printf("ERR n hors plage [1, %d]\n", READ_MAX);
    else acquire(n, false, 0);
  } else if (cmd == "STEP") {
    int sp2 = args.indexOf(' ');
    float a = args.substring(0, sp2).toFloat();
    int n = sp2 < 0 ? 0 : args.substring(sp2 + 1).toInt();
    if (sp2 < 0 || n < 1 || n > READ_MAX || a < -80 || a > 80) Serial.println("ERR arguments STEP invalides");
    else acquire(n, true, a);
  } else {
    Serial.printf("ERR commande inconnue: %s\n", cmd.c_str());
  }
}

void setup() {
  Serial.begin(921600);
  Wire.begin(PIN_SDA, PIN_SCL, 400000);
  pinMode(PIN_VIB, OUTPUT);
  digitalWrite(PIN_VIB, LOW);
  servo.setPeriodHertz(50);
  servo.attach(PIN_SERVO, 500, 2400);
  setServo(0);
  mpuInit();  // en cas d'échec, ID? et READ renverront ERR : le PC le détectera
}

void loop() {
  updateVib(micros());
  if (Serial.available()) handle(Serial.readStringUntil('\n'));
}
