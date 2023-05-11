#!/usr/bin/env python3
'''
Maintain NVdia GPU temperature by dynamically throtlling Idrac (7) fan speed thought IPMI
'''

import pynvml
import subprocess
import shutil
from simple_pid import PID
from time import sleep
import sys

# TODO: as script argument (argparse)
TARGET_TEMP=70


IPMI_MANUAL_FAN_SPEED='ipmitool raw 0x30 0x30 0x01 0x00'
IPMI_AUTO_FAN_SPEED='ipmitool raw 0x30 0x30 0x01 0x01'
# TODO: catch ipmitool command not found
IPMI_BIN=shutil.which('ipmitool')

if sys.argv[1] == "reset":
    subprocess.run(IPMI_AUTO_FAN_SPEED, check=True, stdout=None, capture_output=True)

# TODO: REMOTE CONTROL
# IPMI config for remote control over network
# IDRAC_IP=''
# IDRAC_USER=''
# IDRAC_PASS=''
# REMOTE_IPMI_MANUAL_FAN_SPEED='ipmitool -I lanplus -H %s -U %s -P %s raw 0x30 0x30 0x01 0x00' % (IDRAC_IP, IDRAC_USER, IDRAC_PASS)
# REMOTE_RESTORE_AUTO_CONTROL='ipmitool -I lanplus -H $IDRAC_IP -U $IDRAC_USER -P $IDRAC_PASS raw 0x30 0x30 0x01 0x01'


'''PID CONFIG, hight values (-0.04 > -0.05) for more agressive control, values need to be negatives'''
PID_Kp=-0.001
PID_Ki=-0.001
PID_Kd=-0.001
# PID check and adjust freq
SAMPLE_TIME=10 # in sec

# TODO: as script argument (argparse)
'''FAN SPEED RANGE'''
LOWER_SPEED=45
HIGHER_SPEED=100

PREVIOUS_VALUE = 0

'''Get all GPU temperature'''
def gpus_get_temp():
    pynvml.nvmlInit()
    gpus_temp = []
    for i in range(pynvml.nvmlDeviceGetCount()):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        gpus_temp.append(pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU))
    return(gpus_temp)

'''Return hightest GPU temperature'''
def get_max_temp():
    return(max(gpus_get_temp()))

#TODO: def main()
pid = PID(PID_Kp, PID_Ki, PID_Kd, setpoint=TARGET_TEMP)
pid.output_limits = (LOWER_SPEED, HIGHER_SPEED)
pid.sample_time = SAMPLE_TIME
pid.proportional_on_measurement = True
# pid.set_auto_mode(True, last_output=100)
pid.set_auto_mode(True)


'''Main loop'''
while True:

    temp = int(get_max_temp())

    '''Compute new output from the PID according to the systems current value'''
    raw_control = pid(temp)
    control = round(raw_control)

    '''Gather PID values'''
    p, i, d = pid.components
    log=("TARGET= %s, ACTUAL= %s , FAN_SPEED_SETTING= %s/%s, p=%s, i=%s, d=%s" % (TARGET_TEMP, temp, control, raw_control, p, i, d))

    '''In odrer to not spam the BMC every sample, throtling is skiped when fan speed control stay unchanged'''
    if (p + d) == 0 or PREVIOUS_VALUE == control:
        #TODO: print temp only
        print('NOT THROTTLING', log)
        pass
    else:
        FAN_SPEED=hex(round(control))
        print('THROTTLING', log)
        # TODO: move static args outside loop
        # REMOTE_IPMI_CMD=[IPMI_BIN, '-I', 'lanplus', '-H', IDRAC_IP, '-U', IDRAC_USER, '-P', IDRAC_PASS, 'raw', '0x30', '0x30', '0x02', '0xff', FAN_SPEED ]
        IPMI_CMD=[IPMI_BIN, 'raw', '0x30', '0x30', '0x02', '0xff', FAN_SPEED ]

        # TODO: try / catch errors
        subprocess.run(IPMI_CMD, check=True, stdout=None, capture_output=True)

    PREVIOUS_VALUE=control

    sys.stdout.flush()
    sleep(SAMPLE_TIME)
