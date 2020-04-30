# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import sys
import asyncio
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient
from azureml.accel import PredictionClient
from datetime import datetime, timedelta
import requests

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()


        prediction_client = PredictionClient(address='resnet50', port=50051)
        classes_entries = requests.get("https://raw.githubusercontent.com/Lasagne/Recipes/master/examples/resnet50/imagenet_classes.txt").text.splitlines()

        image_dir = "./assets/"
        for image in os.listdir(image_dir):
            try:
                start_time = time.time()
                results = prediction_client.score_file(path=os.path.join(image_dir, image), 
                                                        input_name='Placeholder:0', 
                                                        outputs='classifier/resnet_v1_50/predictions/Softmax:0')
                inference_time = (time.time() - start_time) * 1000
                # map results [class_id] => [confidence]
                results = enumerate(results)
                # sort results by confidence
                sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
                top_result = sorted_results[0]
                msg_string = "(%.0f ms) The image %s was classified as %s with confidence %s." % (inference_time, os.path.join(image_dir, image), 
                                                                                            classes_entries[top_result[0]], 
                                                                                            top_result[1])
                print(msg_string)
            except: 
                print('except')





        # define behavior for receiving an input message on input1
        async def input1_listener(module_client):
            while True:
                input_message = await module_client.receive_message_on_input("input1")  # blocking call
                print("the data in the message received on input1 was ")
                print(input_message.data)
                print("custom properties are")
                print(input_message.custom_properties)
                print("forwarding mesage to output1")
                await module_client.send_message_to_output(input_message, "output1")

        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)

        # Schedule task for C2D Listener
        listeners = asyncio.gather(input1_listener(module_client))

        print ( "The sample is now waiting for messages. ")

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())