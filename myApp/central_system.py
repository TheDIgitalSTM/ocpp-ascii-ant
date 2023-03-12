import asyncio
import logging
from datetime import datetime
from logtail import LogtailHandler


try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys

    sys.exit(1)

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result, call
from ocpp.v16.enums import Action, RegistrationStatus

# logging.basicConfig(level=logging.DEBUG)
# import logging

handler = LogtailHandler(source_token="BSXaSs6o9fZqsAJnrzecWd7n")
logger = logging.getLogger(__name__)
logger.handlers = []
logger.setLevel(logging.INFO)
logger.addHandler(handler)


class ChargePoint(cp):
    @on(Action.BootNotification)
    def on_boot_notification(
        self, charge_point_vendor: str, charge_point_model: str, **kwargs
    ):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted,
        )
    @on(Action.Heartbeat)
    def on_heartbeat(self):
        # print("Got a Heartbeat!")
        logger.info("Got a Heartbeat!")
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        )
    @on(Action.StatusNotification)
    def on_status_notification(self, **kwargs):
        print('Received StatusNotification:')
        print(kwargs)

        # Do something with the status notification
        # For example, you can log the current status of the charging session
        logger.info("Received StatusNotification: "+str(kwargs))
        return call('StatusNotification', {'status': 'Accepted'})
    @on(Action.Authorize)
    def on_authorize(self, **kwargs):
        print('Received Authorize:')
        print(kwargs)

        # Check if the user is authorized to start a charging session
        logger.info("Received Authorize: "+str(kwargs))

        if kwargs['id_tag'] == 'myrfidtag':
            return call_result.AuthorizePayload(
                id_tag_info={
                    'status': 'Accepted'
                }
            )
        else:
            return call_result.AuthorizePayload(
                id_tag_info={
                    'status': 'Invalid'
                }
            )

async def on_connect(websocket, path):
    """For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers["Sec-WebSocket-Protocol"]
    except KeyError:
        logging.error("Client hasn't requested any Subprotocol. Closing Connection")
        logger.error("Client hasn't requested any Subprotocol. Closing Connection")
        return await websocket.close()
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
        logger.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning(
            "Protocols Mismatched | Expected Subprotocols: %s,"
            " but client supports  %s | Closing connection",
            websocket.available_subprotocols,
            requested_protocols,
        )
        logger.warning(
            "Protocols Mismatched | Expected Subprotocols: %s,"
            " but client supports  %s | Closing connection",
            websocket.available_subprotocols,
            requested_protocols,
        )
        return await websocket.close()

    charge_point_id = path.strip("/")
    cp = ChargePoint(charge_point_id, websocket)

    await cp.start()


async def main():
    server = await websockets.serve(
        on_connect, "0.0.0.0", 9000, subprotocols=["ocpp1.6"]
    )

    logger.info("Server Started listening to new connections...")
    print("Server Started listening to new connections...")
    await server.wait_closed()


if __name__ == "__main__":
    # asyncio.run() is used when running this example with Python >= 3.7v
    asyncio.run(main())
