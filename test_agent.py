#!/usr/bin/env python3
"""
Test script for the medical scheduling agent
"""
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import get_llm
from app.agents.scheduler_agent import SchedulerAgent

def test_intent_detection():
    """Test intent detection specifically"""
    print("Testing intent detection...")
    
    # Initialize agent
    llm = get_llm()
    agent = SchedulerAgent(llm=llm)
    
    test_inputs = [
        "I want to cancel my appointment Jane Doe",
        "cancel my appointment",
        "reschedule appointment",
        "I need to cancel", 
        "modify my appointment"
    ]
    
    for test_input in test_inputs:
        analysis = agent.analyze_user_input(test_input)
        print(f"\nInput: '{test_input}'")
        print(f"Intent: {analysis['intent']}")
        print(f"Entities: {analysis['entities']}")

def test_agent():
    """Test the agent functionality"""
    print("\n\nTesting Medical Scheduling Agent...")
    
    # Initialize agent
    llm = get_llm()
    agent = SchedulerAgent(llm=llm)
    
    # Test conversations
    test_conversations = [
        {
            "name": "Cancel appointment test",
            "inputs": [
                "I want to cancel my appointment Jane Doe"
            ]
        },
        {
            "name": "Check appointments test", 
            "inputs": [
                "I want to check my appointments Jane Doe"
            ]
        },
        {
            "name": "Reschedule appointment test",
            "inputs": [
                "I want to reschedule my appointment Jane Doe"
            ]
        }
    ]
    
    for test in test_conversations:
        print(f"\n{'='*50}")
        print(f"Test: {test['name']}")
        print(f"{'='*50}")
        
        # Reset agent state
        agent.conversation_state = {}
        
        for user_input in test["inputs"]:
            print(f"\nUser: {user_input}")
            response = agent.generate_response(user_input)
            print(f"Agent: {response}")

def test_full_workflows():
    """Test complete workflows"""
    print("\n\nTesting complete workflows...")
    
    # Initialize agent
    llm = get_llm()
    agent = SchedulerAgent(llm=llm)
    
    # Test cancellation workflow
    print(f"\n{'='*50}")
    print(f"Test: Full cancellation workflow")
    print(f"{'='*50}")
    
    agent.conversation_state = {}
    
    inputs = [
        "I want to cancel my appointment Jane Doe",
        "2",  # Select second appointment
    ]
    
    for user_input in inputs:
        print(f"\nUser: {user_input}")
        response = agent.generate_response(user_input)
        print(f"Agent: {response}")
    
    # Test rescheduling workflow
    print(f"\n{'='*50}")
    print(f"Test: Full rescheduling workflow") 
    print(f"{'='*50}")
    
    agent.conversation_state = {}
    
    inputs = [
        "I want to reschedule my appointment Jane Doe",
        "1",  # Select first appointment  
        "next Friday afternoon"  # New date/time
    ]
    
    for user_input in inputs:
        print(f"\nUser: {user_input}")
        response = agent.generate_response(user_input)
        print(f"Agent: {response}")

if __name__ == "__main__":
    test_intent_detection()
    test_agent()
    test_full_workflows()