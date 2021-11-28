# vanee-controller
raspberry pi relay controller for a vanee air exchanger

This is a simple project to keep an old unsupported vanee usable. The circuit board in it fried and no replacements parts are available, so we're faking it with a raspberry pi. The house is wired with buttons that would trigger the air exchanger to run at high speed for a time. The blower motor has separate wires for low, medium, and high speed. We'll just use low and high, connected to a relay expansion board (RPi Relay Board: https://www.amazon.com/dp/B07CZL2SKN) on a raspberry pi 3. 

The relay board uses BCM pin 25 / board pin 37 to control the channel 1 relay. So we use that as an output pin in the controller program when we want to switch from low to high speed. 

We also want to watch for button presses in order to know when the fan should run at high speed for a time, so we use a GPIO pin as an input (with a pulldown resistor so default value is false). We hook 5V on the wire (with a 1k resistor in series, plus a .1uF ceramic capacitor from input to ground for transient voltage protection) and watch for the pin to go high. 

For each button press, 15 minutes of high-speed time is added, up to a maximum of 1 hour. When the timer is set, the relay switches to high speed. When the timer runs out or the program is terminated, the relay switches back to low speed.
