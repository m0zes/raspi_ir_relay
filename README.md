# RasPi IR Relay Controller

## Goals:
* to do learn AJAXy things!
* Control relays off a raspi with a webapp
* Tie in IR controls
  * read IR signals
  * map those signals to be triggered with buttons on the webapp
* Proof-of-Concept, and potentially enable other home automation fancies

### Eventually:
* android app calling the api

## Main problem:
I use a Roku 2 for a media center, unfortunately, the Roku 2 has been locking up recently.
This started as a simple relay project. Have a raspi control a relay, reseting the power to the roku.
It seemed like a waste to have such a powerful device doing such a simple task, so I decided to
expand its duties into a web-controlled universal remote for all my av equipment.

## Screenshots and Construction photos will come.
![Using a protoplate to breakout the raspberry pi's header](http://i.imgur.com/o1Sqi7B.jpg)
![Proto Plate with the complete IR Circuit](http://i.imgur.com/sMnoEb9.jpg)
![Completed Device](http://i.imgur.com/Pcskmng.jpg)
![The outlet that will be controlled by the relay plate](http://i.imgur.com/zjCbX7E.jpg)
http://imgur.com/a/UbdQC

## Thanks
~~IR components and schematics borrowed from http://alexba.in/blog/2013/01/06/setting-up-lirc-on-the-raspberrypi/~~
Do not use the above IR schematics. This has led to at least 4 blown IR LEDs in my testing alone. I'll post a ~~fixed~~completed schematic soon
![This is my new circuit diagram](http://i.imgur.com/nNh1x7l.png)
### Diagram Components
| Diagram Location | Type | Part Number / Value | Quantity | Price (each) |
| ---------------- | ---- | ------------------- | --------:| ------------:|
| D1, D2 | DIODE | 1N4148 | 2 | $0.05 |
| R1-R4 | RESISTOR | 10 | 4 | $0.07 |
| Q1 | NPN | PN2222 | 1 | $0.20 |
| R5 | RESISTOR | 3.3k | 1 | $0.02 |
| L1 | LED | TSAL6400 | 1 | $0.48 |
| L2 | LED | TSAL6100 | 1 | $0.48 |
| IRR1 | IR RECIEVER | TSOP38238 | 1 | $1.95 |

## BOM
### Adafruit
| QTY | Item                                                  | Price  |
| --- | ----------------------------------------------------- | ------:|
| 1   | 5V 2.4A Raspi PS [ID:1995]                            |  $7.95 |
| 1   | Raspberry Pi 3 [ID:3055]                              | $39.95 |
| 1   | IR Receiver (TSOP38238) [ID:157]                      |  $1.95 |
| 1   | Adafruit Pi Dish [ID:942]                             | $17.50 |
| 1   | Transistors (PN2222) - 10 pack[ID:756]                |  $1.95 |

### PIPlates
| QTY | Item                                                  | Price  |
| --- | ----------------------------------------------------- | ------:|
| 1   | PROTOplate                                            |  $9.99 |
| 1   | RELAYplate                                            | $39.99 |
| 1   | BASEplate                                             |  $9.99 |

### Various
| QTY | Item | Price |
| --- | --- | ---:|
| 1ft | 18ga red wire | $0.36 |
| 1ft | 18ga white wire | $0.36 |
| 1ft | 18ga green wire | $0.36 |
| 1 | electrical remodel box | $0.59 |
| 1 | outlet cover plate | $0.29 |
| 3ft | 16ga 3 wire extension cord | $2.97 |
| 5ft | 16ga 2 wire extension cord | $2.95 |
| 1 | electrical outlet | $1.29 |
| 1 | grounded male electrical plug | $3.45 |
