# Medical Appointment Scheduling AI Agent

## Overview
This AI agent automates patient appointment scheduling for medical practices. It handles patient lookup, scheduling, insurance collection, and appointment confirmation through a conversational interface.

## Features
- Patient greeting and information collection
- Automatic determination of new vs. returning patients
- Smart scheduling based on patient type (60min for new, 30min for returning)
- Calendar integration with available slot management
- Insurance information collection
- Appointment confirmation and export
- Patient intake form distribution
- Automated reminder system

## Technical Stack
- LangChain & LangGraph for agent orchestration
- OpenAI for language model capabilities
- Streamlit for user interface
- Pandas for data management

## Setup Instructions

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation
1. Clone the repository
```bash
git clone https://github.com/ladesai123/medical-scheduling-agent.git
cd medical-scheduling-agent