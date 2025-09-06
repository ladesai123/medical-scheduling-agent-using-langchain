"""
Enhanced LangChain-powered conversation system for medical scheduling
"""
from typing import Dict, Any, Optional
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging

logger = logging.getLogger(__name__)


class MedicalSchedulingChain:
    """LangChain-powered conversation chain for medical scheduling."""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.conversation_history = []
        
        # System prompt for medical scheduling
        self.system_prompt = """You are a professional and empathetic medical scheduling assistant for HealthCare+ Medical Center. Your role is to help patients schedule, reschedule, or cancel medical appointments in a warm, human-friendly manner.

Key Guidelines:
- Always be warm, professional, and empathetic 
- Ask one question at a time to avoid overwhelming patients
- Use natural, conversational language 
- Show genuine care for the patient's health needs
- Provide clear, step-by-step guidance
- Be patient with elderly or anxious patients
- Acknowledge their concerns and validate their feelings

Conversation Flow:
1. Greet warmly and ask how you can help
2. For scheduling: Get name → specialty preference → date/time → insurance → email → confirm
3. For modifications: Get name → identify specific appointment → perform action
4. Always end with asking if there's anything else you can help with

Available Specialties: Anesthesiology, Dermatology, Emergency Medicine, Orthopedics, Pediatrics, Psychiatry, Radiology

Sample Natural Responses:
- "Hello! I'm here to help you with your medical appointments. What can I assist you with today?"
- "Of course! I'd be happy to help you schedule an appointment. Could you please tell me your full name?"
- "Thank you, [Name]. What type of specialist would you like to see? We have excellent doctors in cardiology, dermatology, and many other specialties."
- "Perfect! When would work best for you? I can check our availability for any day that's convenient."

Remember: Be conversational, not robotic. Use phrases like "I'd be happy to", "Of course", "Absolutely", and show genuine interest in helping the patient.
"""
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{conversation_context}\n\nPatient: {user_input}\n\nCurrent conversation state: {conversation_state}\n\nPlease respond naturally and helpfully as a medical scheduling assistant."),
        ])
        
        # Check if LLM is compatible with LangChain
        if self.llm and hasattr(self.llm, 'invoke'):
            try:
                self.chain = self.prompt_template | self.llm | StrOutputParser()
                self.is_langchain_compatible = True
            except Exception as e:
                logger.warning(f"LLM not compatible with LangChain: {e}")
                self.chain = None
                self.is_langchain_compatible = False
        else:
            self.chain = None
            self.is_langchain_compatible = False
    
    def generate_response(self, user_input: str, conversation_state: Dict, conversation_history: list = None) -> str:
        """Generate a natural, LangChain-powered response."""
        
        if not self.chain or not self.is_langchain_compatible:
            # Fallback to rule-based if LangChain not available or compatible
            return self._generate_fallback_response(user_input, conversation_state)
        
        try:
            # Prepare conversation context
            if conversation_history:
                context_parts = []
                for msg in conversation_history[-6:]:  # Last 6 messages for context
                    role = "Assistant" if msg.get("role") == "assistant" else "Patient"
                    context_parts.append(f"{role}: {msg.get('content', '')}")
                conversation_context = "\n".join(context_parts)
            else:
                conversation_context = "This is the start of a new conversation."
            
            # Generate response using LangChain
            response = self.chain.invoke({
                "user_input": user_input,
                "conversation_context": conversation_context,
                "conversation_state": self._format_conversation_state(conversation_state)
            })
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating LangChain response: {e}")
            return self._generate_fallback_response(user_input, conversation_state)
    
    def _format_conversation_state(self, state: Dict) -> str:
        """Format conversation state for LangChain context."""
        if not state:
            return "No previous conversation state"
        
        parts = []
        if "patient_name" in state:
            parts.append(f"Patient name: {state['patient_name']}")
        if "conversation_step" in state:
            parts.append(f"Current step: {state['conversation_step']}")
        if "specialty" in state:
            parts.append(f"Requested specialty: {state['specialty']}")
        if "date_preference" in state:
            parts.append(f"Preferred date: {state['date_preference']}")
        if "time_preference" in state:
            parts.append(f"Preferred time: {state['time_preference']}")
        if "insurance_provider" in state:
            parts.append(f"Insurance: {state['insurance_provider']}")
        
        return "; ".join(parts) if parts else "No conversation context"
    
    def _generate_fallback_response(self, user_input: str, conversation_state: Dict) -> str:
        """Fallback response generator when LangChain is not available."""
        current_step = conversation_state.get("conversation_step", "initial")
        
        # More natural fallback responses
        if current_step == "initial" or not conversation_state:
            return ("Hello! I'm here to help you with your medical appointments. "
                   "Whether you need to schedule a new appointment, reschedule an existing one, "
                   "or make any changes, I'm happy to assist you. What can I help you with today?")
        
        elif current_step == "name_requested":
            return ("I'd be delighted to help you with that! To get started, "
                   "could you please tell me your full name?")
        
        elif current_step == "appointment_type":
            name = conversation_state.get("patient_name", "")
            return (f"Thank you, {name}! Now, what type of doctor would you like to see? "
                   f"We have wonderful specialists in areas like dermatology, orthopedics, "
                   f"psychiatry, and many others. What specialty are you interested in?")
        
        elif current_step == "datetime_preference":
            specialty = conversation_state.get("specialty", "specialist")
            return (f"Excellent! I'll help you find a great {specialty}. "
                   f"When would be the most convenient time for you? "
                   f"I can check our availability for any day and time that works with your schedule.")
        
        elif current_step == "insurance_info":
            date_pref = conversation_state.get("date_preference", "your preferred time")
            return (f"Perfect! I can see availability for {date_pref}. "
                   f"To make sure everything goes smoothly with your visit, "
                   f"could you tell me what insurance provider you have?")
        
        elif current_step == "email_collection":
            return ("Almost done! To send you a confirmation with all your appointment details, "
                   "what's the best email address to reach you at?")
        
        else:
            return ("I'm here to help with any questions about your medical appointments. "
                   "Feel free to ask me anything!")