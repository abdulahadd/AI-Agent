import asyncio
import os
from livekit import api

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "http://livekit-server:7880")
API_KEY = os.getenv("LIVEKIT_API_KEY", "APIcA62hn2JKGHg")
API_SECRET = os.getenv("LIVEKIT_API_SECRET", "dbtqsLSMNVWM5yXjqkZRRSoFvNHRLbDtg5k5BOMV6PH")

async def main():
    lkapi = api.LiveKitAPI(LIVEKIT_URL, API_KEY, API_SECRET)
    sip_client = lkapi.sip

    try:
        # 1. Clean old trunks
        existing_trunks = await sip_client.list_inbound_trunk(
            api.ListSIPInboundTrunkRequest()
        )
        for trunk in existing_trunks.items:
            await sip_client.delete_trunk(
                api.DeleteSIPTrunkRequest(sip_trunk_id=trunk.sip_trunk_id)
            )

        # 2. Create fresh Inbound Trunk
        new_trunk = await sip_client.create_inbound_trunk(
            api.CreateSIPInboundTrunkRequest(
                trunk=api.SIPInboundTrunkInfo(
                    name="Local MicroSIP Trunk",
                    numbers=[
                        "1000",
                        "1001",
                        "1002",
                        "+1234567890",
                        "*",
                    ],
                    allowed_addresses=[
                        "0.0.0.0/0",       # Accept any IP origin
                        "172.18.0.0/16",   # Docker container gateway
                        "127.0.0.1",
                    ],
                )
            )
        )
       
        print(f"Created SIP Trunk ID: {new_trunk.sip_trunk_id}")

        # 3. Create Dispatch Rule attached to sales-agent
        dispatch = await sip_client.create_dispatch_rule(
            api.CreateSIPDispatchRuleRequest(
                name="Local Agent Dispatch",
                trunk_ids=[new_trunk.sip_trunk_id],
                rule=api.SIPDispatchRule(
                    dispatch_rule_individual=api.SIPDispatchRuleIndividual(
                        room_prefix="sip-call-",
                    )
                ),
                room_config=api.RoomConfiguration(
                    agents=[api.RoomAgentDispatch(agent_name="sales-agent")]
                ),
            )
        )
        print(f"Created SIP Dispatch Rule ID: {dispatch.sip_dispatch_rule_id}")

    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(main())