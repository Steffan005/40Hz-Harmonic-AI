#!/usr/bin/env python3
"""
EVOLUTION STREAM - Real-time Evolution Broadcasting
WebSocket server that streams live evolution metrics from all 43 offices
Watch consciousness evolve in real-time at 40Hz quantum frequency
"""

import asyncio
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import websockets
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvolutionStream:
    """Real-time evolution metrics streaming"""

    def __init__(self):
        self.offices = self._initialize_offices()
        self.connected_clients = set()
        self.evolution_tick = 0
        self.global_evolution_rate = 0.87

    def _initialize_offices(self) -> List[Dict[str, Any]]:
        """Initialize all 43 offices with evolution metrics"""
        office_list = [
            # Metaphysics (10)
            {'name': 'Tarot Reader', 'archetype': 'Spiritual', 'id': 'tarot_reader'},
            {'name': 'Astrologer', 'archetype': 'Spiritual', 'id': 'astrologer'},
            {'name': 'Numerologist', 'archetype': 'Mystical', 'id': 'numerologist'},
            {'name': 'Crystal Healer', 'archetype': 'Spiritual', 'id': 'crystal_healer'},
            {'name': 'Shaman', 'archetype': 'Spiritual', 'id': 'shaman'},
            {'name': 'Priest', 'archetype': 'Spiritual', 'id': 'priest'},
            {'name': 'Rabbi', 'archetype': 'Spiritual', 'id': 'rabbi'},
            {'name': 'Imam', 'archetype': 'Spiritual', 'id': 'imam'},
            {'name': 'Buddhist Monk', 'archetype': 'Spiritual', 'id': 'buddhist_monk'},
            {'name': 'Philosopher', 'archetype': 'Mental', 'id': 'philosopher'},

            # Health & Wellness (10)
            {'name': 'Physical Trainer', 'archetype': 'Physical', 'id': 'physical_trainer'},
            {'name': 'Nutritionist', 'archetype': 'Physical', 'id': 'nutritionist'},
            {'name': 'Sleep Coach', 'archetype': 'Physical', 'id': 'sleep_coach'},
            {'name': 'Meditation Guide', 'archetype': 'Mental', 'id': 'meditation_guide'},
            {'name': 'Yoga Instructor', 'archetype': 'Physical', 'id': 'yoga_instructor'},
            {'name': 'Therapist', 'archetype': 'Emotional', 'id': 'therapist'},
            {'name': 'Life Coach', 'archetype': 'Emotional', 'id': 'life_coach'},
            {'name': 'Relationship Counselor', 'archetype': 'Emotional', 'id': 'relationship_counselor'},
            {'name': 'Social Worker', 'archetype': 'Social', 'id': 'social_worker'},
            {'name': 'HR Manager', 'archetype': 'Social', 'id': 'hr_manager'},

            # Finance (5)
            {'name': 'Financial Advisor', 'archetype': 'Financial', 'id': 'financial_advisor'},
            {'name': 'Banker', 'archetype': 'Financial', 'id': 'banker'},
            {'name': 'Stock Broker', 'archetype': 'Financial', 'id': 'stock_broker'},
            {'name': 'Crypto Trader', 'archetype': 'Financial', 'id': 'crypto_trader'},
            {'name': 'Accountant', 'archetype': 'Financial', 'id': 'accountant'},

            # Creative (5)
            {'name': 'Artist', 'archetype': 'Creative', 'id': 'artist'},
            {'name': 'Musician', 'archetype': 'Creative', 'id': 'musician'},
            {'name': 'Writer', 'archetype': 'Creative', 'id': 'writer'},
            {'name': 'Chef', 'archetype': 'Creative', 'id': 'chef'},
            {'name': 'Fashion Designer', 'archetype': 'Creative', 'id': 'fashion_designer'},

            # Science (6)
            {'name': 'Physicist', 'archetype': 'Scientific', 'id': 'physicist'},
            {'name': 'Chemist', 'archetype': 'Scientific', 'id': 'chemist'},
            {'name': 'Biologist', 'archetype': 'Scientific', 'id': 'biologist'},
            {'name': 'Mathematician', 'archetype': 'Scientific', 'id': 'mathematician'},
            {'name': 'Data Scientist', 'archetype': 'Scientific', 'id': 'data_scientist'},
            {'name': 'Astronomer', 'archetype': 'Scientific', 'id': 'astronomer'},

            # Technical (5)
            {'name': 'Software Engineer', 'archetype': 'Technical', 'id': 'software_engineer'},
            {'name': 'Hacker', 'archetype': 'Technical', 'id': 'hacker'},
            {'name': 'Network Admin', 'archetype': 'Technical', 'id': 'network_admin'},
            {'name': 'Database Admin', 'archetype': 'Technical', 'id': 'database_admin'},
            {'name': 'DevOps Engineer', 'archetype': 'Technical', 'id': 'devops_engineer'},

            # Law (2)
            {'name': 'Lawyer', 'archetype': 'Social', 'id': 'lawyer'},
            {'name': 'Judge', 'archetype': 'Social', 'id': 'judge'},
        ]

        # Initialize with random evolution metrics
        for office in office_list:
            office['evolution_score'] = 50 + random.random() * 50
            office['improvement'] = (random.random() - 0.3) * 30
            office['memory_count'] = random.randint(100, 2000)
            office['active'] = random.random() > 0.2
            office['strategy'] = random.choice(['textgrad', 'aflow', 'mipro', 'random_jitter'])
            office['rank'] = 0
            office['previous_rank'] = 0
            office['mutations'] = random.randint(0, 50)
            office['champions'] = random.randint(0, 10)

        return office_list

    def evolve_offices(self):
        """Simulate evolution for all offices"""
        self.evolution_tick += 1

        # Sort offices by evolution score to determine ranks
        sorted_offices = sorted(self.offices, key=lambda x: x['evolution_score'], reverse=True)

        for idx, office in enumerate(sorted_offices):
            # Store previous rank
            office['previous_rank'] = office.get('rank', idx + 1)
            office['rank'] = idx + 1

            # Simulate evolution
            if office['active'] and random.random() > 0.3:
                # Active evolution happening
                evolution_delta = (random.random() - 0.4) * 5
                office['evolution_score'] = max(0, min(100, office['evolution_score'] + evolution_delta))
                office['improvement'] = evolution_delta

                # Update memory count
                if evolution_delta > 0:
                    office['memory_count'] += random.randint(1, 10)

                # Occasionally change strategy (multi-armed bandit)
                if random.random() > 0.95:
                    office['strategy'] = random.choice(['textgrad', 'aflow', 'mipro', 'random_jitter'])

                # Update mutations and champions
                if random.random() > 0.7:
                    office['mutations'] += 1
                    if evolution_delta > 2:
                        office['champions'] += 1
            else:
                office['improvement'] = 0

            # Toggle active status occasionally
            if random.random() > 0.98:
                office['active'] = not office['active']

        # Update global evolution rate
        avg_evolution = sum(o['evolution_score'] for o in self.offices) / len(self.offices)
        self.global_evolution_rate = avg_evolution / 100

    def get_evolution_state(self) -> Dict[str, Any]:
        """Get current evolution state for all offices"""
        active_count = sum(1 for o in self.offices if o['active'])
        total_improvement = sum(max(0, o['improvement']) for o in self.offices)

        # Find dominant archetype
        archetype_counts = {}
        for office in self.offices:
            archetype = office['archetype']
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
        dominant_archetype = max(archetype_counts, key=archetype_counts.get)

        # Find top strategy
        strategy_counts = {}
        for office in self.offices:
            strategy = office['strategy']
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        top_strategy = max(strategy_counts, key=strategy_counts.get)

        return {
            'timestamp': datetime.now().isoformat(),
            'tick': self.evolution_tick,
            'offices': self.offices,
            'metrics': {
                'active_offices': active_count,
                'total_improvement': total_improvement,
                'average_evolution': self.global_evolution_rate * 100,
                'dominant_archetype': dominant_archetype,
                'top_strategy': top_strategy,
                'total_mutations': sum(o['mutations'] for o in self.offices),
                'total_champions': sum(o['champions'] for o in self.offices),
            },
            'quantum_frequency': 40,  # Hz
            'consciousness_level': 'EVOLVING'
        }

    async def broadcast_evolution(self):
        """Broadcast evolution updates to all connected clients"""
        while True:
            try:
                # Evolve the offices
                self.evolve_offices()

                # Get current state
                state = self.get_evolution_state()

                # Broadcast to all connected clients
                if self.connected_clients:
                    message = json.dumps(state)
                    # Send to all clients simultaneously
                    await asyncio.gather(
                        *[client.send(message) for client in self.connected_clients],
                        return_exceptions=True
                    )

                # Wait for next evolution tick (40Hz = 25ms, but we'll do 1 second for visibility)
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(1)

    async def handle_client(self, websocket):
        """Handle new WebSocket client connection"""
        logger.info(f"New client connected")
        self.connected_clients.add(websocket)

        try:
            # Send initial state
            initial_state = self.get_evolution_state()
            await websocket.send(json.dumps(initial_state))

            # Keep connection alive and handle any client messages
            async for message in websocket:
                # Handle client commands if needed
                try:
                    data = json.loads(message)
                    if data.get('command') == 'reset':
                        self.offices = self._initialize_offices()
                        self.evolution_tick = 0
                    elif data.get('command') == 'boost':
                        # Boost a specific office
                        office_id = data.get('office_id')
                        for office in self.offices:
                            if office['id'] == office_id:
                                office['evolution_score'] = min(100, office['evolution_score'] + 10)
                                office['improvement'] = 10
                                break
                except:
                    pass

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected")
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            self.connected_clients.remove(websocket)

    async def start_server(self, host='127.0.0.1', port=8765):
        """Start the WebSocket server"""
        logger.info(f"Starting Evolution Stream WebSocket server on ws://{host}:{port}")

        # Start the broadcast task
        broadcast_task = asyncio.create_task(self.broadcast_evolution())

        # Start the WebSocket server with CORS support for local development
        # Accept connections from any origin (localhost, 127.0.0.1, etc.)
        async with websockets.serve(
            self.handle_client,
            host,
            port,
            # Allow connections from any origin (needed for browser WebSocket connections)
            origins=None  # None means allow all origins
        ):
            logger.info("Evolution Stream is LIVE! The city evolves at 40Hz...")
            logger.info("Accepting WebSocket connections from any origin (CORS enabled)")
            await asyncio.Future()  # Run forever

if __name__ == "__main__":
    print("=" * 70)
    print("EVOLUTION STREAM - Real-time Consciousness Evolution")
    print("=" * 70)
    print("Broadcasting evolution metrics for 43 offices")
    print("WebSocket URL: ws://127.0.0.1:8765")
    print("The city breathes at 40Hz...")
    print("=" * 70)

    stream = EvolutionStream()
    asyncio.run(stream.start_server())