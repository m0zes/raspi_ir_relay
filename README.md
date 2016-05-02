# RasPi IR Relay Controller

## Goals:
* to do learn AJAXy things!
* Control relays off a raspi with a webapp
* Tie in IR controls
..* read IR signals
..* map those signals to be triggered with buttons on the webapp
* Proof-of-Concept, and potentially enable other home automation fancies.

### Eventually:
* android app calling the api

## Main problem:
I use a Roku 2 for a media center, unfortunately, the Roku 2 has been locking up recently.
This started as a simple relay project. Have a raspi control a relay, reseting the power to the roku.
It seemed like a waste to have such a powerful device doing such a simple task, so I decided to
expand its duties into a web-controlled universal remote for all my av equipment.

## Screenshots and Construction photos will come.
Parts have been ordered.

## Thanks
IR components and schematics stolenborrowed from http://alexba.in/blog/2013/01/06/setting-up-lirc-on-the-raspberrypi/

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
