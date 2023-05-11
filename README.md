# Tested env:

* Ubuntu 22.04
* Dell PowerEdge R720xd / iDrac7
* nvidia driver 525.105.17

# Installation

* install pip requirement:  pip install pynvml simple-pid
* install ipmitool: apt-get install ipmitool 
* (other stuffs I forgot)

# Usage

Start kisscool.py inside a screen or tmux.
To send log to system journal, add " | logger -t SOMETAG "

# Testimonial

Don't pay attention to code quality, its actually a quick and dirty thing, but could change if needed, feel free to contribute.