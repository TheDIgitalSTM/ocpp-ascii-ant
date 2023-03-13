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
from ocpp.routing import after
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.v16 import call
from ocpp.v16.enums import Action, RegistrationStatus, ChargePointStatus, AuthorizationStatus, ChargePointErrorCode
from ocpp.v16.enums import ChargingProfilePurposeType
from ocpp.v16.enums import ChargingRateUnitType
from ocpp.v16.enums import ChargingProfileKindType
from ocpp.v16.enums import ChargingProfileStatus



# logging.basicConfig(level=logging.DEBUG)
# import logging

handler = LogtailHandler(source_token="BSXaSs6o9fZqsAJnrzecWd7n")
logger = logging.getLogger(__name__)
logger.handlers = []
logger.setLevel(logging.DEBUG)
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
        return call_result.StatusNotificationPayload(
            # connectorId=kwargs['connector_id'],
            # errorCode=kwargs['error_code'],
            # status=kwargs['status']
        )
    
    #     id_tag = kwargs['id_tag']
    #     connector_id = kwargs['connector_id']
    # # Check if the ID tag is valid
    #     if id_tag == "123456":
    #         # If the ID tag is valid, start the transaction
    #         transaction_id = 1
    #         start_time = datetime.utcnow().isoformat() + "Z"
    #         registration_status = RegistrationStatus.accepted
    #         id_token_info = {
    #             "status": AuthorizationStatus.accepted,
    #             "expiryDate": "2022-02-24T23:59:59.000Z",
    #             "parentIdTag": None,
    #             "groupIds": None
    #         }
            
    #         # Update the state of the charging point to reflect the started transaction
    #         self.transaction_id = transaction_id
    #         self.connector_status[connector_id] = ChargePointStatus.charging
    #         self.meter_start[connector_id] = self.current_meter_value()
    #         self.current_transaction_id[connector_id] = transaction_id
            
    #         # Send a StatusNotification to the central system to indicate that charging has started
    #         status_notification_payload = {
    #             "connectorId": connector_id,
    #             "status": ChargePointStatus.charging,
    #             "errorCode": ChargePointErrorCode.noError,
    #             "info": None,
    #             "timestamp": datetime.utcnow().isoformat() + "Z",
    #             "vendorId": "my_vendor_id",
    #             "vendorErrorCode": None,
    #             "meterValue": [{
    #                 "timestamp": start_time,
    #                 "sampledValue": [{
    #                     "value": self.meter_start[connector_id],
    #                     "context": "Sample.Periodic",
    #                     "format": "Raw",
    #                     "measurand": "Energy.Active.Import.Register",
    #                     "location": None,
    #                     "unit": "Wh"
    #                 }]
    #             }]
    #         }
            
    #         self.call_result("StatusNotification", status_notification_payload)
            
    #         # Return a StartTransactionPayload with the transaction ID and other information
    #         return {
    #             "transactionId": transaction_id,
    #             "idTagInfo": {
    #                 "status": registration_status,
    #                 "expiryDate": None,
    #                 "parentIdTag": None,
    #                 "idToken": {
    #                     "idToken": id_tag,
    #                     "type": IdTokenType.rfid
    #                 },
    #                 "groupIds": None,
    #                 "expiryReason": None,
    #                 "transactionId": transaction_id,
    #                 "id": None,
    #                 "location": None,
    #                 "language1": None,
    #                 "language2": None
    #             },
    #             "timestamp": start_time,
    #             "id": None,
    #             "meterStart": self.meter_start[connector_id],
    #             "reservationId": None,
    #             "status": registration_status
    #         }
    #     else:
    #         # If the ID tag is not valid, reject the transaction
    #         registration_status = RegistrationStatus.invalid
    #         id_token_info = {
    #             "status": AuthorizationStatus.invalid,
    #             "expiryDate": None,
    #             "parentIdTag": None,
    #             "groupIds": None
    #         }
            
    #         # Return a StartTransactionPayload with the registration status and ID token information
    #         return {
    #             "transactionId": None,
    #             "idTagInfo": {
    #                 "status": registration_status,
    #                 "expiryDate": None,
    #                 "parentIdTag": None,
    #                 "idToken": {
    #                     "idToken": id_tag,
    #                     "type": IdTokenType.rf
    #                 }
    #             }
    #         }
    @on(Action.MeterValues)
    def on_meter_values(self, **kwargs):
        print('Received MeterValues:')
        print(kwargs)
        logger.info("Received MeterValues: "+str(kwargs))

        if 'MeterValues' in kwargs:
            # Do something with the meter values
            # For example, you can log the current meter values
            return call_result.MeterValuesPayload(
                # connector_id=kwargs['connector_id'],
                # transaction_id=kwargs.get('transaction_id', None),
                # meter_value=[{
                #     'timestamp': kwargs['MeterValues'][0]['timestamp'],
                #     'sampled_value': kwargs['MeterValues'][0]['sampledValue']
                # }]
            )
        else:
            # Handle the case where the MeterValues key is missing from the payload
            # return call_result.GenericPayload(
            #     error='Missing MeterValues key in payload'
            # )
            return call_result.MeterValuesPayload()
    @on(Action.Authorize)
    def on_authorize(self, **kwargs):
        
        print('Received Authorize:')
        print(kwargs)

        # Check if the user is authorized to start a charging session
        logger.info("Received Authorize: "+str(kwargs))

        if kwargs['id_tag'] == 'F698DABC':
            print("You are authorized to charge")
            # Define the values for the charging profile
            # charging_rate_unit = ChargingRateUnitType.A
            # charging_profile_purpose = ChargingProfilePurposeType("TxProfile")
            # stack_level = 1
            # charging_profile_kind = ChargingProfileKindType("Absolute")
            # # charging_profile_status = ChargingProfileStatus.Accepted
            # # charging_schedule_period_start = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            # charging_schedule_period_start = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
            # # charging_schedule_period_duration = 60  # in minutes
            # charging_schedule_period_limit = 1000  # in Wh
            # charging_schedule = [
            #     {
            #         'startPeriod': charging_schedule_period_start,
            #         'limit': charging_schedule_period_limit
            #     }
            # ]
            # start_response =  call.RemoteStartTransactionPayload(
            #         connector_id=1, # Replace with the connector ID you want to use
            #         id_tag=kwargs['id_tag'],
            #         charging_profile={
            #             'chargingProfileId': '1',
            #             'transactionId': 1234,
            #             'stackLevel': stack_level,
            #             'chargingProfilePurpose': charging_profile_purpose,
            #             'chargingProfileKind': charging_profile_kind,
            #             'chargingSchedule': charging_schedule,
            #             'recurrencyKind': 0
            #         }
            #     )
            
            # print("start charge response")
            # print(start_response)

            # logger.info("start charge response")
            # logger.info(start_response)

            return call_result.AuthorizePayload(
                id_tag_info={
                    'status': 'Accepted'
                }
            )
            
        else:
            print("You are not authorized to charge")
            return call_result.AuthorizePayload(
                id_tag_info={
                    'status': 'Invalid'
                }
            )

    @after(Action.Authorize)
    def after_authorize(self,  **kwargs):
        print("After authorize order ")
        charging_profile_purpose = ChargingProfilePurposeType("TxProfile")
        stack_level = 1
        charging_profile_kind = ChargingProfileKindType("Absolute")
        # charging_profile_status = ChargingProfileStatus.Accepted
        # charging_schedule_period_start = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        charging_schedule_period_start = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        # charging_schedule_period_duration = 60  # in minutes
        charging_schedule_period_limit = 1000  # in Wh
        charging_schedule = [
            {
                'startPeriod': charging_schedule_period_start,
                'limit': charging_schedule_period_limit
            }
        ]
        start_response =  call.RemoteStartTransactionPayload(
                connector_id=1, # Replace with the connector ID you want to use
                id_tag= kwargs['id_tag'],
                charging_profile={
                    'chargingProfileId': '1',
                    'transactionId': 1234,
                    'stackLevel': stack_level,
                    'chargingProfilePurpose': charging_profile_purpose,
                    'chargingProfileKind': charging_profile_kind,
                    'chargingSchedule': charging_schedule,
                    'recurrencyKind': 0
                }
            )
        
        print("start charge response")
        print(start_response)

        logger.info("start charge response")
        logger.info(start_response)
        
    @on(Action.StartTransaction)
    def on_start_transaction(self, **kwargs):
        print('Received on start transaction:')
        print(kwargs)
        # Do something with the status notification
        # For example, you can log the current status of the charging session
        logger.info("Received StatusNotification: "+str(kwargs))
        # expire_date datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        return call_result.StartTransactionPayload(
            transaction_id=1,
            id_tag_info={"status": RegistrationStatus.accepted
                       }
        )
    @on(Action.StopTransaction)
    def on_stop_transaction(self, **kwargs):
        print("Received stop transaction")
        print(kwargs)

        logger.info("Received stop transaction: "+ str(kwargs))
        return call_result.StopTransactionPayload(
            id_tag_info={"status": RegistrationStatus.accepted}
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
