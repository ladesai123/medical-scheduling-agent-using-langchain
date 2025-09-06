# Medical Appointment Scheduling AI Agent

## Overview
This AI agent automates patient appointment scheduling for medical practices. It handles patient lookup, scheduling, insurance collection, and appointment confirmation through a conversational interface.

## 🌟 Features

### Core Functionality
- **Patient Management**: Automatic patient lookup and registration
- **Smart Scheduling**: 60min slots for new patients, 30min for returning patients
- **Doctor Management**: Multiple doctors with specialty and availability tracking
- **Insurance Integration**: Collection and validation of insurance information
- **Multiple Interfaces**: Both CLI and web-based Streamlit interface
- **Data Generation**: Automatic generation of sample patients and doctors
- **Robust Fallbacks**: Works with or without OpenAI API access
- **Offline Capability**: Full functionality even without internet connection

### LangChain Integration (NEW!)
- **Advanced AI Agent**: Full LangChain/LangGraph implementation with 11 specialized tools
- **Enhanced Conversation**: Natural language processing for complex scheduling requests
- **Multi-Agent Architecture**: Sophisticated agent orchestration for healthcare workflows
- **Tool-Based Operations**: Specialized tools for patient lookup, scheduling, and notifications

### Business Features (NEW!)
- **Calendar Management**: Real-time availability checking and smart booking
- **Notification System**: Automated email confirmations and SMS reminders
- **3-Tier Reminder System**: Automated reminders at 7, 3, and 1 days before appointments
- **Form Distribution**: Automatic patient intake form delivery
- **Excel Export**: Administrative reporting for appointment analytics
- **Interactive Reminders**: Patient response collection for form completion and visit confirmation

### Enhanced Reliability
- **Multi-Level Fallback**: 4-tier degradation system ensures 100% uptime
- **Error Recovery**: Graceful handling of API failures and network issues
- **Mock LangChain Agent**: Enhanced rule-based agent with full business logic
- **Production Ready**: Comprehensive error handling and logging

## 🚀 Quick Start

### Method 1: Instant Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/ladesai123/medical-scheduling-agent-using-langchain.git
cd medical-scheduling-agent-using-langchain

# Generate sample data
python main.py setup

# Start the CLI interface immediately
python main.py cli
```

### Method 2: With AI Integration (Gemini or OpenAI)
```bash
# 1. Get a Gemini API key (recommended - free tier available)
# Visit: https://aistudio.google.com/app/apikey
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
echo "AI_PROVIDER=gemini" >> .env

# OR get OpenAI API key (alternative option)
# Visit: https://platform.openai.com/api-keys
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
echo "AI_PROVIDER=openai" >> .env

# 2. Install dependencies (optional - app works without them)
pip install google-generativeai langchain-google-genai python-dotenv streamlit

# 3. Generate sample data
python main.py setup

# 4. Choose your interface:
python main.py cli        # Command line interface
python main.py streamlit  # Web interface
```

### Method 3: Emergency Mode
```bash
# For testing Gemini connectivity directly
python fix_gemini.py

# For testing OpenAI connectivity directly
python fix_openai.py
```

## 📋 Available Commands

| Command | Description | Requirements |
|---------|-------------|--------------|
| `python main.py setup` | Generate sample patients and doctors | None |
| `python main.py cli` | Start command-line interface | None |
| `python main.py streamlit` | Start web interface | streamlit package |
| `python fix_gemini.py` | Test Gemini connection directly | None |
| `python fix_openai.py` | Test OpenAI connection directly | None |

## 💡 Usage Examples

### CLI Interface
```
You: Hello, I need to schedule an appointment
Agent: Hello! I'm your medical scheduling assistant. How can I help you today?

You: My name is John Smith and I need to see a cardiologist
Agent: I'd be happy to help you schedule an appointment with a cardiologist. 
       Could you please provide your preferred date and time?

You: How about tomorrow morning?
Agent: Let me check our availability for tomorrow morning...
```

### Sample Commands to Try
- "I need to schedule an appointment"
- "My name is [Your Name]"
- "I need to see a cardiologist"
- "What doctors are available?"
- "Cancel my appointment"
- "I'm a new patient"

## 🛠️ Technical Architecture

### Core Components
- **Scheduler Agent**: Main conversation and booking logic
- **Data Generator**: Creates realistic synthetic patient/doctor data
- **Configuration System**: Handles API keys and environment setup
- **Fallback Systems**: Multiple layers of graceful degradation

### Fallback Hierarchy
1. **Enhanced LangChain Mode**: Full LangChain agent with Gemini/OpenAI + specialized tools
2. **Mock LangChain Mode**: Enhanced rule-based agent with business logic (always works)
3. **Standard AI Mode**: Gemini/OpenAI package + API key with basic agent
4. **Simple AI Mode**: Custom HTTP client + API key
5. **Offline Mode**: Rule-based responses (always works)

### File Structure
```
medical-scheduling-agent/
├── main.py                 # Main entry point
├── fix_gemini.py           # Emergency Gemini testing
├── fix_openai.py           # Emergency OpenAI testing
├── requirements.txt       # Optional dependencies
├── .env                   # Your API keys (create this)
├── app/
│   ├── config.py          # Configuration and LLM setup
│   ├── agents/
│   │   └── scheduler_agent.py  # Main scheduling logic
│   ├── ui/
│   │   └── streamlit_app.py    # Web interface
│   ├── utils/
│   │   ├── data_generator.py   # Sample data creation
│   │   ├── simple_dotenv.py    # Environment loader
│   │   └── simple_openai.py    # API client
│   └── data/              # Generated data files
│       ├── patients.json
│       ├── doctors.json
│       └── appointments.json
```

## 🔧 Configuration

### Environment Variables (.env file)
```bash
# AI Provider Configuration
AI_PROVIDER=gemini  # Options: gemini, openai

# Gemini API (recommended - free tier available)
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API (alternative/fallback)
OPENAI_API_KEY=your_openai_api_key_here

# Optional settings
MODEL_NAME=gemini-1.5-flash  # or gpt-3.5-turbo for OpenAI
DEBUG_MODE=True
```

### Dependencies
```bash
# Core (all optional - app works without them)
google-generativeai>=0.7.0      # For Gemini AI responses
langchain-google-genai>=1.0.0   # For LangChain Gemini integration
openai>=1.10.0                  # For OpenAI AI responses (fallback)
langchain-openai>=0.2.0         # For LangChain OpenAI integration
python-dotenv>=1.0.0            # For .env file loading
streamlit>=1.28.0               # For web interface

# The app includes fallback implementations for all dependencies
```

## 🔍 Troubleshooting

### Common Issues

**Problem**: "ModuleNotFoundError" when running
**Solution**: The app is designed to work without external dependencies. Make sure you're in the correct directory and using the right Python version.

**Problem**: No AI responses / only getting basic responses
**Solution**: This is normal! The app works without OpenAI. To get AI responses:
1. Get an OpenAI API key
2. Add it to your .env file
3. Optionally install `pip install openai`

**Problem**: Network timeouts during pip install
**Solution**: Skip dependencies - the app works fine without them:
```bash
python main.py setup
python main.py cli
```

**Problem**: "No address associated with hostname" error
**Solution**: This indicates network connectivity issues. The app will automatically fall back to offline mode.

### Debugging Steps
1. Try basic CLI: `python main.py cli`
2. Check if data exists: `ls app/data/`
3. Generate data if missing: `python main.py setup`
4. Test OpenAI directly: `python fix_openai.py`

## 📊 Generated Data

The system automatically creates:
- **50 synthetic patients** with realistic medical information
- **10 doctors** across various specialties with working schedules
- **Appointment tracking** system for bookings

All data is stored in JSON format for easy inspection and modification.

## 🎯 Production Deployment

For production use, consider:
1. Replace JSON files with a proper database
2. Add user authentication
3. Integrate with real calendar systems
4. Add HIPAA compliance measures
5. Implement proper logging and monitoring

## 🤝 Contributing

This project is designed to be educational and extensible. Feel free to:
- Add new specialties and doctors
- Enhance the conversation logic
- Improve the UI design
- Add integration with external systems

## 📄 License

This project is provided as-is for educational purposes.

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Ensure you're using Python 3.8+
3. Try the emergency mode: `python fix_openai.py`
4. The app is designed to work even with network/dependency issues

---

**🎉 That's it! The app should work immediately after cloning. No complex setup required!**