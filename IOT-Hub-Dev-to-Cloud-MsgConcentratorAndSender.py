# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import random
import time
import sys

# Using the Python Device SDK for IoT Hub:
#   https://github.com/Azure/azure-iot-sdk-python
# Needs: 
# pip install azure-iothub-device-client
# pip install azure-iothub-service-client
# This implementation connects to a device-specific MQTT endpoint on your IoT Hub.
import iothub_client
# pylint: disable=E0611
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue
import http.client, urllib.request, urllib.parse, urllib.error, base64, json, urllib

# The User and IP address for the HUE API
HueUser = "CMwpYxbZxA0jc71uUsqROdbwT23udYeB7IZxcdy3"
HueAPI = "192.168.1.33"

# The device connection string to authenticate the device with your IoT hub.
# Using the Azure CLI:
# az iot hub device-identity show-connection-string --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table
CONNECTION_STRING = "HostName=IOTHubEdzard2.azure-devices.net;DeviceId=HUELampColor1;SharedAccessKey=ZsRkTyfZHBsfPjin8OlNQa7VLIufo9hzjpiA26wIdLs="

MSG_TXT = "{\"LightNo\": %s,\"LightOn\": %i,\"Brightness\": %s, \"MinBri\": 0, \"MaxBri\": 255, \"Color\": %s, \"MinColor\": 0, \"MaxColor\": 65535, \"Saturation\": %s, \"MinSat\": 0, \"MaxSat\": 256}"

# Using the MQTT protocol.
PROTOCOL = IoTHubTransportProvider.MQTT
MESSAGE_TIMEOUT = 10000

#Set to True to use mock-up values
TEST = True

# Define some functions
def send_confirmation_callback(message, result, user_context):
    print ( "IoT Hub responded to message with status: %s" % (result) )

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    return client

def iothub_client_telemetry_sample_run():

    try:
        client = iothub_client_init()
        print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )

        while True:
            if not TEST :
                # Define the request headers.
                headers = {}
                # Define the parameters
                # params = urllib.parse.urlencode({})
                # Define the request body
                body = { }
                # Execute the REST API call and get the response.
                conn = http.client.HTTPConnection(HueAPI)
                #print(conn)
                conn.request("GET", "/api/%s/lights" % HueUser, str(body), headers)
                response = conn.getresponse()
                data = response.read().decode("UTF-8")
                # 'data' contains the JSON data. The following formats the JSON data for display.
                parsed = json.loads(data)
                #print(parsed)
                # Build the message from the values received
                lampe = '3'
                if parsed['3']['state']['on'] :
                    lichtan = 1
                else :
                    lichtan = 0
                helligkeit = parsed['3']['state']['bri']
                farbe = parsed['3']['state']['hue']
                sat = parsed['3']['state']['sat']
                msg_txt_formatted = MSG_TXT % (lampe,lichtan,helligkeit,farbe,sat)
                message = IoTHubMessage(msg_txt_formatted)
                # Send the message.
                #print( "Sending message: %s" % message.get_string() )
                client.send_event_async(message, send_confirmation_callback, None)
                conn.close()
                time.sleep(5)
            else :
                # Build the message with simulated telemetry values.
                lampe = '3'
                lichtan = 1
                helligkeit = 128
                farbe = 65535
                sat = random.randint(1,255)
                msg_txt_formatted = MSG_TXT % (lampe,lichtan,helligkeit,farbe,sat)
                message = IoTHubMessage(msg_txt_formatted)
                # Send the message.
                #print( "Sending message: %s" % message.get_string() )
                client.send_event_async(message, send_confirmation_callback, None)
                
                time.sleep(5)

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        return
    except Exception as e:
        print('Error:')
        print(e)
        return
    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )
    
if __name__ == '__main__':
    print ( "IoT Hub Quickstart #1 - Simulated device" )
    print ( "Press Ctrl-C to exit" )
    iothub_client_telemetry_sample_run()