import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

async def on_event(partition_context, event):
    # Print the event data.
    print("Received the event: \"{}\" from the partition with ID: \"{}\"".format(event.body_as_str(encoding='UTF-8'), partition_context.partition_id))

    # Update the checkpoint so that the program doesn't read the events
    # that it has already read when you run it next time.
    await partition_context.update_checkpoint(event)

async def main():
    # Connection string for namespace and name for event hub
    VAR_CONN_STR         = "Connection string for namespace"
    VAR_EVENTHUB_NAME    = "Name for event hub"

    # Consumer group name
    VAR_CONSUMER_GROUP   = "$Default"

    # Connectionstring for storage account and blob container name
    VAR_STORAGE_CONN_STR = "Connectionstring for storage account"
    VAR_BLOB_CONTAINER   = "Blob container name"

    # Storage service API version for Azure Stack Hub
    STORAGE_SERVICE_API_VERSION = "2017-11-09"

    # Create an Azure blob checkpoint store to store the checkpoints.
    checkpoint_store = BlobCheckpointStore.from_connection_string(VAR_STORAGE_CONN_STR, container_name=VAR_BLOB_CONTAINER, api_version=STORAGE_SERVICE_API_VERSION)

    # Create a consumer client for the event hub.
    client = EventHubConsumerClient.from_connection_string(conn_str=VAR_CONN_STR, consumer_group=VAR_CONSUMER_GROUP, eventhub_name=VAR_EVENTHUB_NAME, checkpoint_store=checkpoint_store)
    async with client:
        # Call the receive method.
        await client.receive(on_event=on_event)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # Run the main method.
    loop.run_until_complete(main())
