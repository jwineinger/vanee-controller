# vanee-controller
raspberry pi relay controller for a vanee air exchanger

This is a simple project to keep an old unsupported vanee usable. The circuit board in it fried and no replacements parts are available, so I'm faking it with a raspberry pi. The house is wired with buttons that would trigger the air exchanger to run at high speed for a time. The blower motor has separate wires for low, medium, and high speed. I'll just use low and high, connected to a relay expansion board (RPi Relay Board: https://www.amazon.com/dp/B07CZL2SKN) on a raspberry pi 3. 

The relay board uses BCM pin 25 / board pin 37 to control the channel 1 relay. So I use that as an output pin in the controller program when we want to switch from low to high speed. 

I also want to watch for button presses in order to know when the fan should run at high speed for a time, so I use a GPIO pin (board pin 7) as an input (with a pulldown resistor so default value is false). I hooked the 5V rail to the switch/button wire (with a 1k resistor in series, plus a .1uF ceramic capacitor from input to ground for transient voltage protection) and watch for the pin to go high. I did experiment with a few different ways to debounce the button presses but I found that the simplest was the most effective: just sleep for 200ms whenever a press was detected. This seems to almost always be enough time for the single press to be registered, released, and have the value settle back to low/false.

For each button press, 15 minutes of high-speed time is added, up to a maximum of 1 hour. When the timer is set, the relay switches to high speed. When the timer runs out or the program is terminated, the relay switches back to low speed.
