#! /usr/bin/python3
#========================================================================
#
#   Poll a list of cameras and if they report motion detected, 
#   user the ZMTrigger socket interface to trigger recording.
#
#========================================================================
#
# Don't forget to activate the trigger port on ZoneMinder before 
#   starting this app. See https://wiki.zoneminder.com/ZMTrigger
# 
# To start this script at boot enter at the command line:
#   sudo crontab -e
#
# Select your editor is prompted and add to the end of the file:
#   @reboot /path/to/you/script/ext_trigger.py
#
import requests
import time
import socket
import logging
from logging.handlers import RotatingFileHandler

#========================================================================
# Control values 
#
log_file = r'/var/log/ext_trigger.log'

# If running this app on a different machine to the ZoneMinder app then
#  specify the IPv4 address of ZoneMinder
# zm_ipaddress = 'X.X.X.X'
zm_ipaddress = '127.0.0.1'
zm_port = 6802

#========================================================================
# Populate this array of dictionaries with you camera data
# You can customise the motion_query string per camera if you have
# a mixed instalation.
# 
# Make sure the zoneminder_id matches the associated camera
#
Cameras = [ 
    { 
    'name': 'A Cam',
    'ipaddr': 'X.X.X.X',
    'zoneminder_id': 1,
    'motion_query': 'http://{ip}/api.cgi?cmd=GetMdState&user={user}&password={passwd}',
    'username': 'your_username',
    'password': 'your_password'
    },
    { 
    'name': 'B Cam',
    'ipaddr': 'X.X.X.X',
    'zoneminder_id': 2,
    'motion_query': 'http://{ip}/api.cgi?cmd=GetMdState&user={user}&password={passwd}',
    'username': 'your_username',
    'password': 'your_password'
    }
    ]

Initial_Boot_Delay = 60     # Units: seconds Allows ZoneMinder to fully boot
Trigger_Time = 20           # Units: seconds
Inter_Camera_Delay = 0.5    # Units: seconds Specifies the delay between checking cameras. 
                            #        Total polling interval will be this x No. of cameras.

#========================================================================
# Setup logging
#
logger = logging.getLogger('ext_trigger_log')
handler = RotatingFileHandler(log_file, maxBytes=20000, backupCount=5)
logger.addHandler(handler)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'))
logger.setLevel(logging.INFO) # DEBUG INFO WARNING ERROR

#========================================================================
# Query a camera to se if motion has been detected
# Returns:
#   0 No motion reported
#   1 Motion reported
#   2 Error getting data
#
def check_cam_for_motion( Camera ):
    headers = {'Accept': 'application/json'}

    url = Camera['motion_query'].format( ip=Camera['ipaddr'], user=Camera['username'], passwd=Camera['password'] )

    try:
        resp = requests.get(url, headers=headers)
    except Exception as error:
        logger.error('Error checking motion state. Camera {} IPv4 {} Username {} Response {}'.format(
            Camera['name'], Camera['ipaddr'], Camera['username'], error
        ))
        return 2
    
    #=======================================================================
    # For a Reolink camera the response to the query is JSON in the format:
    #
    # Good response:
    #   [{'cmd': 'GetMdState', 'code': 0, 'value': {'state': 0}}]
    # Failure response (example):
    #   [{'cmd': 'GetMdState', 'code': 1, 'error': {'detail': 'invalid user', 'rspCode': -27}}]
    #
    # Check your cameras documentation for the response it gives and then
    #   customise this section for your system.
    #
    # This code is deliberatly verbose to make customisation quicker & easier.
    #
    logger.debug("Response to motion query: {}".format(resp.json()))
    data = resp.json()
    data = data[0]
    logger.debug("Data from motion query: {}".format(data))

    if 'cmd' not in data:
        # The query response was not understood, no cmd element was returned
        logger.error('Error the response to the motion query was not understood (cmd attr). Camera {} IPv4 {} Username {} Response {}'.format(
        Camera['name'], Camera['ipaddr'], Camera['username'], data
        ))
        return 2

    if data['cmd'] != 'GetMdState':
        # The query response was not understood, the command answered does not match the expected one
        logger.error('Error the response to the motion query was not understood (cmd value). Camera {} IPv4 {} Username {} Response {}'.format(
        Camera['name'], Camera['ipaddr'], Camera['username'], data
        ))
        return 2

    if 'code' not in data:
        # The query response was not understood, the camera didn't respond in the expected format
        logger.error('Error the response to the motion query was not understood (code attr). Camera {} IPv4 {} Username {} Response {}'.format(
        Camera['name'], Camera['ipaddr'], Camera['username'], data
        ))
        return 2

    if data['code'] == 1:
        # The query command did not execute, the camera wouldn't execute the command. This is often caused by bad credentials
        logger.error('Error the response to the motion query was not executed. Camera {} IPv4 {} Username {} Response {}'.format(
        Camera['name'], Camera['ipaddr'], Camera['username'], data[0]['error']
        ))
        return 2

    if 'value' not in data:
        # The query response was not understood, the camera didn't respond in the expected format
        logger.error('Error the response to the motion query was not understood. Camera {} IPv4 {} Username {} Response {}'.format(
        Camera['name'], Camera['ipaddr'], Camera['username'], data
        ))
        return 2

    # The query command executed, test if motion was detected value->state = 0 or 1 (on Reolink)
    if data['value']['state'] == 1:
        return 1
    
    return 0

#========================================================================
# Open a socket to the ZoneMinder machine and send the trigger record
#   command.
#
# Returns:
#   0 Command sent
#   1 Error while sending command. 
#
def send_trigger( cam ):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((zm_ipaddress, zm_port))
        except Exception as error:
            logger.error("Can't open socket to ZoneMinder address {} port {} respose {}".format(zm_ipaddress, zm_port, error))
            return 1

        id_bytes = bytearray(str(cam['zoneminder_id']), 'utf8')
        Time = bytearray(str(Trigger_Time), 'utf8')
        cmd = id_bytes + b'|on+' + Time + b'|1|External Motion|Ext Python trigger|'

        logger.debug("Sending trigger for {} id {} command {}".format(cam['name'], cam['zoneminder_id'], cmd))
        try:
            s.sendall(cmd)
        except Exception as error:
            logger.error("Can't transfer command to ZoneMinder address {} port {} respose {}".format(zm_ipaddress, zm_port, error))
            return 1

        try:
            reply = s.recv(1024) # The server has received the command
        except Exception as error:
            logger.error("No response after trigger command address {} port {} respose {}".format(zm_ipaddress, zm_port, error))
            return 1

        logger.debug("Reply {}".format(reply))

    return 0

#=============================================================
# Main function 
#
def main():
    logger.info('External camera trigger app starting.')
    time.sleep(Initial_Boot_Delay)
    logger.info('Checking configuration.')
    Checked_Cameras = []
    App_Running = True

    #=============================================================
    # Initial parameter check, 
    #   Check all cameras are accessable and respond as expected 
    #   to a query
    for cam in Cameras:
        if check_cam_for_motion(cam) != 2:
            Checked_Cameras.append(cam)
            logger.debug("Camera checked ok: {}".format(cam['name']))
        else:
            logger.error("Camera failed test check: {}".format(cam['name']))

    if len(Checked_Cameras) == 0:
        App_Running = False
        logger.info('External camera trigger app exiting, no cameras to check.')

    #=============================================================
    # Initial parameter check, 
    #   Check that the ZoneMinder machine accepts a trigger signal
    #
    trigger_rnt = send_trigger( Checked_Cameras[0] )
    if trigger_rnt != 0:
        logger.error("Failed to send trigger to ZoneMinder: {}".format( zm_ipaddress ))
        App_Running = False

    #=============================================================
    # Run continuous checking
    while App_Running:
        for cam in Checked_Cameras:
            rtn = check_cam_for_motion(cam)

            if rtn == 2:
                logger.warning("Camera failed motion poll: {}".format(cam['name']))
            else:
                if rtn == 1:
                    logger.debug("Motion reported: {}".format(cam['name']))
                    trigger_rnt = send_trigger( cam )
                    if trigger_rnt != 0:
                        logger.warning("Failed to send trigger to ZoneMinder: {}".format( zm_ipaddress ))
            time.sleep( Inter_Camera_Delay )
 
    return

if __name__ == '__main__':
    main()
