#!/usr/bin/env python3
"""
Multi-Agent Status Tracking System
Provides utilities for agents to update and check status
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class AgentStatusTracker:
    def __init__(self, project_root: str = "/Users/by/AIMiniGames"):
        self.project_root = Path(project_root)
        self.coordination_file = self.project_root / ".claude/agents/shared/coordination.json"
        
    def load_coordination(self) -> Dict:
        """Load current coordination state"""
        if self.coordination_file.exists():
            with open(self.coordination_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_coordination(self, data: Dict) -> None:
        """Save coordination state"""
        with open(self.coordination_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_agent_status(self, agent_id: str, status: str, current_task: str = None) -> None:
        """Update an agent's status"""
        coord = self.load_coordination()
        
        if agent_id in coord.get('agents', {}):
            coord['agents'][agent_id]['current_status'] = status
            coord['agents'][agent_id]['last_updated'] = datetime.utcnow().isoformat() + 'Z'
            
            if current_task:
                if current_task not in coord['agents'][agent_id]['current_tasks']:
                    coord['agents'][agent_id]['current_tasks'].append(current_task)
            
            self.save_coordination(coord)
    
    def complete_task(self, agent_id: str, task: str) -> None:
        """Mark a task as completed for an agent"""
        coord = self.load_coordination()
        
        if agent_id in coord.get('agents', {}):
            agent = coord['agents'][agent_id]
            
            # Move from current to completed
            if task in agent['current_tasks']:
                agent['current_tasks'].remove(task)
            
            if task not in agent['completed_tasks']:
                agent['completed_tasks'].append({
                    'task': task,
                    'completed_at': datetime.utcnow().isoformat() + 'Z'
                })
            
            self.save_coordination(coord)
    
    def add_handoff(self, from_agent: str, to_agent: str, task: str, context: str, 
                   deliverables: List[str], notes: str = "") -> None:
        """Add a task handoff entry"""
        coord = self.load_coordination()
        
        handoff_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'from_agent': from_agent,
            'to_agent': to_agent,
            'task': task,
            'context': context,
            'deliverables': deliverables,
            'notes': notes,
            'status': 'pending'
        }
        
        if 'communication' not in coord:
            coord['communication'] = {'handoff_log': [], 'shared_context': {}}
        
        coord['communication']['handoff_log'].append(handoff_entry)
        self.save_coordination(coord)
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Get current status of an agent"""
        coord = self.load_coordination()
        return coord.get('agents', {}).get(agent_id)
    
    def get_available_agents(self) -> List[str]:
        """Get list of agents with 'available' status"""
        coord = self.load_coordination()
        available = []
        
        for agent_id, agent_data in coord.get('agents', {}).items():
            if agent_data.get('current_status') == 'available':
                available.append(agent_id)
        
        return available
    
    def get_pending_handoffs(self, to_agent: str) -> List[Dict]:
        """Get pending handoffs for a specific agent"""
        coord = self.load_coordination()
        handoffs = coord.get('communication', {}).get('handoff_log', [])
        
        pending = []
        for handoff in handoffs:
            if handoff.get('to_agent') == to_agent and handoff.get('status') == 'pending':
                pending.append(handoff)
        
        return pending
    
    def accept_handoff(self, handoff_index: int) -> None:
        """Accept a handoff (mark as in progress)"""
        coord = self.load_coordination()
        handoffs = coord.get('communication', {}).get('handoff_log', [])
        
        if 0 <= handoff_index < len(handoffs):
            handoffs[handoff_index]['status'] = 'accepted'
            handoffs[handoff_index]['accepted_at'] = datetime.utcnow().isoformat() + 'Z'
            self.save_coordination(coord)
    
    def add_blocker(self, description: str, agent_id: str) -> None:
        """Add a blocker to shared context"""
        coord = self.load_coordination()
        
        if 'communication' not in coord:
            coord['communication'] = {'shared_context': {}}
        
        if 'blockers' not in coord['communication']['shared_context']:
            coord['communication']['shared_context']['blockers'] = []
        
        blocker = {
            'description': description,
            'reported_by': agent_id,
            'reported_at': datetime.utcnow().isoformat() + 'Z',
            'status': 'open'
        }
        
        coord['communication']['shared_context']['blockers'].append(blocker)
        self.save_coordination(coord)
    
    def print_status_summary(self) -> None:
        """Print a summary of all agent statuses"""
        coord = self.load_coordination()
        
        print("\\n=== Multi-Agent Status Summary ===")
        print(f"Project: {coord.get('project_name', 'Unknown')}")
        print(f"Current Phase: {coord.get('communication', {}).get('shared_context', {}).get('current_phase', 'Unknown')}")
        print()
        
        for agent_id, agent_data in coord.get('agents', {}).items():
            status_icon = "🟢" if agent_data['current_status'] == 'available' else "🔄" if agent_data['current_status'] == 'working' else "🔴"
            print(f"{status_icon} {agent_data['role']} ({agent_id})")
            print(f"   Status: {agent_data['current_status']}")
            print(f"   Current Tasks: {len(agent_data['current_tasks'])}")
            print(f"   Completed Tasks: {len(agent_data['completed_tasks'])}")
            print()
        
        # Show pending handoffs
        handoffs = coord.get('communication', {}).get('handoff_log', [])
        pending_handoffs = [h for h in handoffs if h.get('status') == 'pending']
        if pending_handoffs:
            print("📋 Pending Handoffs:")
            for handoff in pending_handoffs:
                print(f"   {handoff['from_agent']} → {handoff['to_agent']}: {handoff['task']}")
            print()
        
        # Show blockers
        blockers = coord.get('communication', {}).get('shared_context', {}).get('blockers', [])
        open_blockers = [b for b in blockers if b.get('status') == 'open']
        if open_blockers:
            print("⚠️  Open Blockers:")
            for blocker in open_blockers:
                print(f"   {blocker['description']} (reported by {blocker['reported_by']})")
            print()

def main():
    """CLI interface for status tracking"""
    import sys
    
    tracker = AgentStatusTracker()
    
    if len(sys.argv) < 2:
        tracker.print_status_summary()
        return
    
    command = sys.argv[1]
    
    if command == "status":
        if len(sys.argv) > 2:
            agent_id = sys.argv[2]
            status = tracker.get_agent_status(agent_id)
            if status:
                print(json.dumps(status, indent=2))
            else:
                print(f"Agent {agent_id} not found")
        else:
            tracker.print_status_summary()
    
    elif command == "update":
        if len(sys.argv) >= 4:
            agent_id, status = sys.argv[2], sys.argv[3]
            task = sys.argv[4] if len(sys.argv) > 4 else None
            tracker.update_agent_status(agent_id, status, task)
            print(f"Updated {agent_id} status to {status}")
        else:
            print("Usage: python status_tracker.py update <agent_id> <status> [task]")
    
    elif command == "handoff":
        if len(sys.argv) >= 6:
            from_agent, to_agent, task, context = sys.argv[2:6]
            deliverables = sys.argv[6].split(',') if len(sys.argv) > 6 else []
            notes = sys.argv[7] if len(sys.argv) > 7 else ""
            tracker.add_handoff(from_agent, to_agent, task, context, deliverables, notes)
            print(f"Added handoff from {from_agent} to {to_agent}: {task}")
        else:
            print("Usage: python status_tracker.py handoff <from> <to> <task> <context> [deliverables] [notes]")
    
    else:
        print("Available commands: status, update, handoff")

if __name__ == "__main__":
    main()