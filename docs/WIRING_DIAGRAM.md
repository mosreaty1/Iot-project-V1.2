# Hardware Wiring Diagram

## GPIO Pin Layout (Raspberry Pi 4)

```
     3V3  (1) (2)  5V
   GPIO2  (3) (4)  5V
   GPIO3  (5) (6)  GND
   GPIO4  (7) (8)  GPIO14
     GND  (9) (10) GPIO15
  GPIO17 (11) (12) GPIO18
  GPIO27 (13) (14) GND
  GPIO22 (15) (16) GPIO23
     3V3 (17) (18) GPIO24
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25
  GPIO11 (23) (24) GPIO8
     GND (25) (26) GPIO7
   GPIO0 (27) (28) GPIO1
   GPIO5 (29) (30) GND
   GPIO6 (31) (32) GPIO12
  GPIO13 (33) (34) GND
  GPIO19 (35) (36) GPIO16
  GPIO26 (37) (38) GPIO20
     GND (39) (40) GPIO21
```

---

## Component Connections

### 1. HC-SR04 Ultrasonic Sensor

**WARNING: ECHO pin needs voltage divider (3.3V logic)!**

```
HC-SR04          Raspberry Pi
--------         ------------
VCC      ------> 5V (Pin 2 or 4)
TRIG     ------> GPIO 23 (Pin 16)
ECHO     ------> [Voltage Divider] -> GPIO 24 (Pin 18)
GND      ------> GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
```

**Voltage Divider for ECHO:**
```
ECHO Pin --[1kΩ]-- GPIO 24
               |
              [2kΩ]
               |
              GND

This reduces 5V to 3.3V: (2kΩ / (1kΩ + 2kΩ)) × 5V = 3.3V
```

---

### 2. 16x2 LCD Display (HD44780)

```
LCD Pin   Function    Raspberry Pi
-------   --------    ------------
1  VSS    Ground      GND
2  VDD    Power       5V
3  V0     Contrast    Potentiometer (10kΩ) middle pin
                      Pot ends: 5V and GND
4  RS     Register    GPIO 7 (Pin 26)
5  RW     Read/Write  GND (write only)
6  E      Enable      GPIO 8 (Pin 24)
7  D0     Data 0      Not connected (4-bit mode)
8  D1     Data 1      Not connected
9  D2     Data 2      Not connected
10 D3     Data 3      Not connected
11 D4     Data 4      GPIO 25 (Pin 22)
12 D5     Data 5      GPIO 24 (Pin 18)
13 D6     Data 6      GPIO 23 (Pin 16)
14 D7     Data 7      GPIO 18 (Pin 12)
15 A      Backlight+  5V via 220Ω resistor
16 K      Backlight-  GND
```

**Contrast Adjustment:**
- Use 10kΩ potentiometer for V0
- Adjust for best readability

---

### 3. Traffic Light LEDs

**Red LED:**
```
GPIO 17 (Pin 11) --[220Ω resistor]-- LED Anode (+)
LED Cathode (-) ---------------------- GND
```

**Green LED:**
```
GPIO 27 (Pin 13) --[220Ω resistor]-- LED Anode (+)
LED Cathode (-) ---------------------- GND
```

**Note:** Resistor values may vary (220Ω to 1kΩ) depending on LED specs.

---

### 4. SG90 Servo Motor (Barrier)

```
Servo Wire    Raspberry Pi
----------    ------------
Red (VCC)     5V (Pin 2 or 4)
Brown (GND)   GND
Orange (PWM)  GPIO 22 (Pin 15)
```

**Important:**
- For larger servos (MG995), use external 5V power supply
- Connect grounds together (common ground)
- RPi 5V pin can only provide ~1A total

**With External Power:**
```
External 5V+ -> Servo VCC
External GND -> Servo GND + RPi GND (common ground)
GPIO 22 -> Servo Signal
```

---

### 5. Pi Camera Module V2

```
Camera Ribbon Cable -> CSI Port (between HDMI and audio jack)

Note: Blue side faces toward audio jack
```

**Enable Camera:**
```bash
sudo raspi-config
# Interface Options -> Camera -> Enable
sudo reboot
```

---

## Complete Wiring Summary

| Component | Pin/GPIO | Connection |
|-----------|----------|------------|
| **Ultrasonic** | | |
| - Trigger | GPIO 23 | Direct connection |
| - Echo | GPIO 24 | Via voltage divider |
| **LCD** | | |
| - RS | GPIO 7 | Direct connection |
| - EN | GPIO 8 | Direct connection |
| - D4 | GPIO 25 | Direct connection |
| - D5 | GPIO 24 | Direct connection |
| - D6 | GPIO 23 | Direct connection |
| - D7 | GPIO 18 | Direct connection |
| **LEDs** | | |
| - Red | GPIO 17 | Via 220Ω resistor |
| - Green | GPIO 27 | Via 220Ω resistor |
| **Servo** | GPIO 22 | Direct to signal wire |
| **Camera** | CSI Port | Ribbon cable |

---

## Power Considerations

**Total Current Draw:**
- Raspberry Pi 4: ~600mA idle, up to 1.2A under load
- LCD with backlight: ~100mA
- Servo SG90: ~100-600mA (depending on load)
- LEDs: ~20mA each
- Ultrasonic: ~15mA
- Camera: ~250mA

**Recommended:**
- Use official Raspberry Pi 5V/3A power supply
- For heavy-duty servos, use external power
- Add decoupling capacitors for stable operation

---

## Breadboard Layout Example

```
     Raspberry Pi
         |
    ┌────┴────┐
    │  GPIO   │
    └────┬────┘
         |
    [Breadboard]
         |
    ┌────┼────┬────┬────┐
    |    |    |    |    |
  Ultra LCD  LEDs Servo
  sonic
```

**Connections on Breadboard:**
1. Power rails: Connect 5V and GND rails
2. Ultrasonic sensor with voltage divider
3. LCD with potentiometer
4. LEDs with current-limiting resistors
5. Servo (or use separate power)

---

## Testing Individual Components

### Test Ultrasonic
```python
from modules.ultrasonic import UltrasonicSensor
sensor = UltrasonicSensor(23, 24)
print(f"Distance: {sensor.get_distance()} cm")
```

### Test LCD
```python
from modules.lcd_display import LCDDisplay
lcd = LCDDisplay(rs_pin=7, en_pin=8, d4_pin=25, d5_pin=24, d6_pin=23, d7_pin=18)
lcd.display_message("Hello", "World")
```

### Test LEDs
```python
from modules.traffic_light import TrafficLight
light = TrafficLight(red_pin=17, green_pin=27)
light.green()  # Should light green
import time
time.sleep(2)
light.red()    # Should light red
```

### Test Servo
```python
from modules.barrier import BarrierControl
barrier = BarrierControl(servo_pin=22)
barrier.open()   # Should move to 90 degrees
import time
time.sleep(2)
barrier.close()  # Should move to 0 degrees
```

---

## Troubleshooting

**Problem: Ultrasonic readings erratic**
- Check voltage divider resistor values
- Ensure stable power supply
- Add 0.1µF capacitor across VCC/GND

**Problem: LCD shows blocks**
- Adjust contrast potentiometer
- Check all data line connections
- Verify 5V power

**Problem: Servo jitters**
- Use external 5V power supply
- Add 100µF capacitor across servo power
- Ensure common ground

**Problem: LEDs too bright/dim**
- Adjust resistor values (220Ω to 1kΩ)
- Check LED forward voltage rating

---

## Safety Notes

⚠️ **Important Safety Guidelines:**

1. **Power Off:** Always disconnect power before wiring
2. **Voltage Levels:** RPi GPIO is 3.3V - use voltage dividers for 5V signals
3. **Current Limits:** GPIO pins max 16mA - always use resistors with LEDs
4. **ESD Protection:** Touch grounded metal before handling components
5. **Polarity:** Double-check LED and capacitor polarity
6. **Short Circuits:** Verify connections before powering on

---

## Tools Needed

- Breadboard
- Jumper wires (M-M, M-F, F-F)
- Resistors: 220Ω (×2), 1kΩ (×1), 2kΩ (×1)
- 10kΩ potentiometer (for LCD contrast)
- Multimeter (for testing)
- Wire strippers
- Screwdriver (for potentiometer)

---

## Next Steps

After wiring:
1. Double-check all connections
2. Test each component individually
3. Run full system test
4. Adjust thresholds in config
5. Deploy!
