#!/usr/bin/env python3
"""
Example of how to scale agents for production.
This shows different approaches for handling multiple concurrent calls.
"""

import asyncio
import logging
import os
from typing import Dict, List
from livekit.agents import JobContext, WorkerOptions, cli

logger = logging.getLogger(__name__)

class ScalableSalesAgent:
    """
    Example of an agent that can handle multiple conversations
    This is more complex but allows fewer instances to handle more calls
    """
    
    def __init__(self):
        self.max_conversations = int(os.getenv("MAX_CONVERSATIONS", "10"))
        self.active_conversations: Dict[str, asyncio.Task] = {}
        
    async def handle_room(self, ctx: JobContext):
        """Handle a single room/conversation"""
        room_id = ctx.room.name
        logger.info(f"Starting conversation in room: {room_id}")
        
        try:
            # Your existing agent logic here
            # This is where the actual conversation happens
            await self.run_conversation(ctx)
            
        except Exception as e:
            logger.error(f"Error in room {room_id}: {e}")
        finally:
            # Clean up
            if room_id in self.active_conversations:
                del self.active_conversations[room_id]
            logger.info(f"Finished conversation in room: {room_id}")
    
    async def run_conversation(self, ctx: JobContext):
        """Actual conversation logic - same as your current agent"""
        # This would contain your existing conversation code
        # from the main agent.py file
        pass
    
    async def entrypoint(self, ctx: JobContext):
        """Main entrypoint - handles scaling logic"""
        room_id = ctx.room.name
        
        # Check if we're at capacity
        if len(self.active_conversations) >= self.max_conversations:
            logger.warning(f"Agent at capacity ({self.max_conversations}), rejecting room: {room_id}")
            await ctx.room.disconnect()
            return
        
        # Start conversation in background
        task = asyncio.create_task(self.handle_room(ctx))
        self.active_conversations[room_id] = task
        
        try:
            await task
        except asyncio.CancelledError:
            logger.info(f"Conversation cancelled for room: {room_id}")
        finally:
            if room_id in self.active_conversations:
                del self.active_conversations[room_id]

# Production scaling strategies:
def create_agent_instances(count: int = 10):
    """
    Create multiple agent instances for scaling
    Each instance handles 1 conversation at a time
    """
    for i in range(count):
        # In production, you'd use Docker/Kubernetes
        # This is just to show the concept
        agent = ScalableSalesAgent()
        print(f"Created agent instance {i+1}")

def docker_scaling_example():
    """
    Example Docker commands for scaling
    """
    commands = [
        "# Scale to 10 instances",
        "docker-compose up --scale sales-agent=10",
        "",
        "# Or with Docker Swarm",
        "docker service create --name sales-agents --replicas 100 sales-agent",
        "",
        "# Or with Kubernetes",
        "kubectl scale deployment sales-agents --replicas=100"
    ]
    
    for cmd in commands:
        print(cmd)

if __name__ == "__main__":
    print("=== Agent Scaling Examples ===")
    print("\n1. Multiple Instances (Recommended):")
    print("   - Same agent code")
    print("   - Multiple containers")
    print("   - LiveKit load balances")
    print("   - Easy to scale up/down")
    
    print("\n2. Single Instance Multi-Conversation:")
    print("   - More complex code")
    print("   - Fewer containers")
    print("   - More resource efficient")
    print("   - Harder to debug")
    
    print("\n3. Production Commands:")
    docker_scaling_example()



