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

## BOM
### Adafruit
| QTY | Item                                                  | Price  |
| --- | ----------------------------------------------------- | ------:|
| 1   | 5V 2.4A Raspi PS [ID:1995]                            |  $7.95 |
| 1   | Raspberry Pi 3 [ID:3055]                              | $39.95 |
| 1   | 5mm IR LED (940nm) [ID:387]                           |  $0.75 |
| 1   | IR Receiver (TSOP38238) [ID:157]                      |  $1.95 |
| 1   | Adafruit Pi Dish [ID:942]                             | $17.50 |
| 1   | Transistors (PN2222) - 10 pack[ID:756]                |  $1.95 |
| 1   | Resistors 10K ohm 5% 1/4W Pack of 25[ID:2784]         |  $0.75 |

### PIPlates
| QTY | Item                                                  | Price  |
| --- | ----------------------------------------------------- | ------:|
| 1   | PROTOplate                                            |  $9.99 |
| 1   | RELAYplate                                            | $39.99 |
| 1   | BASEplate                                             |  $9.99 |

### Mouser
| QTY | Item                                                  | Price  |
| --- | ----------------------------------------------------- | ------:|
| 2   | PCH175 (right angle led holders)                      |  $0.54 |
| 1   | OED-EL-1L2 (35 degree IR emitter)                     |  $0.35 |

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
