#!/usr/bin/env python3
"""
Generate visual documentation for the Medical Scheduling Agent
"""

import os
import subprocess
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_system_architecture_diagram():
    """Create a visual system architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define colors
    colors = {
        'user': '#4CAF50',      # Green
        'ui': '#2196F3',        # Blue  
        'agent': '#FF9800',     # Orange
        'business': '#9C27B0',  # Purple
        'data': '#607D8B',      # Blue Grey
        'external': '#F44336'   # Red
    }
    
    # Title
    ax.text(5, 9.5, 'Medical Scheduling Agent - System Architecture', 
            fontsize=20, fontweight='bold', ha='center')
    
    # User Layer
    user_box = FancyBboxPatch((0.5, 8), 2, 0.8, 
                             boxstyle="round,pad=0.1", 
                             facecolor=colors['user'], 
                             edgecolor='black', linewidth=2)
    ax.add_patch(user_box)
    ax.text(1.5, 8.4, 'User\nInterface', fontsize=12, fontweight='bold', 
            ha='center', va='center')
    ax.text(1.5, 7.7, '• CLI\n• Streamlit\n• REST API', fontsize=9, 
            ha='center', va='top')
    
    # Agent Layer
    langchain_box = FancyBboxPatch((0.5, 6), 2, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['agent'], 
                                  edgecolor='black', linewidth=2)
    ax.add_patch(langchain_box)
    ax.text(1.5, 6.8, 'LangChain\nAgent', fontsize=12, fontweight='bold', 
            ha='center', va='center')
    ax.text(1.5, 6.3, '• Tool Execution\n• Conversation\n• AI Integration', 
            fontsize=9, ha='center', va='center')
    
    scheduler_box = FancyBboxPatch((3, 6), 2, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['agent'], 
                                  edgecolor='black', linewidth=2)
    ax.add_patch(scheduler_box)
    ax.text(4, 6.8, 'Scheduler\nAgent', fontsize=12, fontweight='bold', 
            ha='center', va='center')
    ax.text(4, 6.3, '• Rule-based\n• Fallback\n• Offline Mode', 
            fontsize=9, ha='center', va='center')
    
    # Business Logic Layer
    calendar_box = FancyBboxPatch((0.5, 4), 1.8, 1, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=colors['business'], 
                                 edgecolor='black', linewidth=2)
    ax.add_patch(calendar_box)
    ax.text(1.4, 4.5, 'Calendar\nManager', fontsize=11, fontweight='bold', 
            ha='center', va='center', color='white')
    
    notification_box = FancyBboxPatch((2.6, 4), 1.8, 1, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor=colors['business'], 
                                     edgecolor='black', linewidth=2)
    ax.add_patch(notification_box)
    ax.text(3.5, 4.5, 'Notification\nManager', fontsize=11, fontweight='bold', 
            ha='center', va='center', color='white')
    
    tools_box = FancyBboxPatch((4.7, 4), 1.8, 1, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['business'], 
                              edgecolor='black', linewidth=2)
    ax.add_patch(tools_box)
    ax.text(5.6, 4.5, 'Agent\nTools', fontsize=11, fontweight='bold', 
            ha='center', va='center', color='white')
    
    # Data Layer
    data_box = FancyBboxPatch((1.5, 2), 3, 1.2, 
                             boxstyle="round,pad=0.1", 
                             facecolor=colors['data'], 
                             edgecolor='black', linewidth=2)
    ax.add_patch(data_box)
    ax.text(3, 2.8, 'Data Layer', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(3, 2.3, 'Patients • Doctors • Appointments\nJSON Persistence • State Management', 
            fontsize=10, ha='center', va='center', color='white')
    
    # External Services
    gemini_box = FancyBboxPatch((6.5, 7.5), 1.5, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor=colors['external'], 
                               edgecolor='black', linewidth=2)
    ax.add_patch(gemini_box)
    ax.text(7.25, 7.9, 'Gemini API', fontsize=10, fontweight='bold', 
            ha='center', va='center', color='white')
    
    openai_box = FancyBboxPatch((8.2, 7.5), 1.5, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor=colors['external'], 
                               edgecolor='black', linewidth=2)
    ax.add_patch(openai_box)
    ax.text(8.95, 7.9, 'OpenAI API', fontsize=10, fontweight='bold', 
            ha='center', va='center', color='white')
    
    email_box = FancyBboxPatch((6.5, 6.5), 1.5, 0.8, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['external'], 
                              edgecolor='black', linewidth=2)
    ax.add_patch(email_box)
    ax.text(7.25, 6.9, 'Email/SMS', fontsize=10, fontweight='bold', 
            ha='center', va='center', color='white')
    
    calendar_api_box = FancyBboxPatch((8.2, 6.5), 1.5, 0.8, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor=colors['external'], 
                                     edgecolor='black', linewidth=2)
    ax.add_patch(calendar_api_box)
    ax.text(8.95, 6.9, 'Calendar APIs', fontsize=10, fontweight='bold', 
            ha='center', va='center', color='white')
    
    # Arrows and connections
    # User to Agents
    ax.arrow(1.5, 7.9, 0, -0.6, head_width=0.1, head_length=0.1, 
             fc='black', ec='black', linewidth=2)
    
    # Agent to Business Logic
    ax.arrow(1.5, 5.9, 0, -0.8, head_width=0.1, head_length=0.1, 
             fc='black', ec='black', linewidth=1.5)
    ax.arrow(4, 5.9, 0, -0.8, head_width=0.1, head_length=0.1, 
             fc='black', ec='black', linewidth=1.5)
    
    # Business Logic to Data
    ax.arrow(3, 3.9, 0, -0.6, head_width=0.1, head_length=0.1, 
             fc='black', ec='black', linewidth=1.5)
    
    # External API connections
    ax.arrow(2.5, 6.6, 3.8, 1, head_width=0.1, head_length=0.1, 
             fc='gray', ec='gray', linewidth=1, linestyle='--')
    ax.arrow(4.5, 4.5, 1.8, 2, head_width=0.1, head_length=0.1, 
             fc='gray', ec='gray', linewidth=1, linestyle='--')
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color=colors['user'], label='User Interface'),
        mpatches.Patch(color=colors['agent'], label='Agent Layer'),
        mpatches.Patch(color=colors['business'], label='Business Logic'),
        mpatches.Patch(color=colors['data'], label='Data Layer'),
        mpatches.Patch(color=colors['external'], label='External APIs')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    # Add flow indicators
    ax.text(0.2, 5, 'Request\nFlow', fontsize=9, fontweight='bold', 
            rotation=90, ha='center', va='center')
    ax.text(9.8, 5, 'API\nCalls', fontsize=9, fontweight='bold', 
            rotation=90, ha='center', va='center')
    
    plt.tight_layout()
    plt.savefig('medical_scheduling_architecture.png', dpi=300, bbox_inches='tight')
    plt.savefig('medical_scheduling_architecture.pdf', dpi=300, bbox_inches='tight')
    print("✅ System architecture diagram created: medical_scheduling_architecture.png/pdf")

def create_data_flow_diagram():
    """Create a detailed data flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(5, 7.5, 'Medical Scheduling Agent - Data Flow Diagram', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Define positions and create flow steps
    steps = [
        (1, 6.5, "User\nInput", '#4CAF50'),
        (3, 6.5, "Intent\nAnalysis", '#2196F3'),
        (5, 6.5, "Agent\nSelection", '#FF9800'),
        (7, 6.5, "Tool\nExecution", '#9C27B0'),
        (9, 6.5, "Response\nGeneration", '#607D8B'),
        
        (2, 4.5, "Patient\nLookup", '#E91E63'),
        (4, 4.5, "Doctor\nAvailability", '#E91E63'),
        (6, 4.5, "Appointment\nBooking", '#E91E63'),
        (8, 4.5, "Notification\nSending", '#E91E63'),
        
        (3, 2.5, "Data\nPersistence", '#795548'),
        (5, 2.5, "State\nManagement", '#795548'),
        (7, 2.5, "Confirmation\nGeneration", '#795548'),
    ]
    
    # Draw boxes and labels
    for x, y, label, color in steps:
        box = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6, 
                            boxstyle="round,pad=0.05", 
                            facecolor=color, alpha=0.8,
                            edgecolor='black', linewidth=1)
        ax.add_patch(box)
        ax.text(x, y, label, fontsize=9, fontweight='bold', 
                ha='center', va='center', color='white')
    
    # Draw arrows for main flow
    main_flow = [(1, 6.5), (3, 6.5), (5, 6.5), (7, 6.5), (9, 6.5)]
    for i in range(len(main_flow)-1):
        x1, y1 = main_flow[i]
        x2, y2 = main_flow[i+1]
        ax.arrow(x1+0.4, y1, x2-x1-0.8, y2-y1, 
                head_width=0.1, head_length=0.1, 
                fc='black', ec='black', linewidth=2)
    
    # Draw arrows to sub-processes
    sub_arrows = [
        ((7, 6.2), (2, 4.8)),  # Tool to Patient Lookup
        ((7, 6.2), (4, 4.8)),  # Tool to Doctor Availability
        ((7, 6.2), (6, 4.8)),  # Tool to Booking
        ((7, 6.2), (8, 4.8)),  # Tool to Notification
        
        ((5, 4.2), (3, 2.8)),  # Processes to Data
        ((6, 4.2), (5, 2.8)),  # Processes to State
        ((8, 4.2), (7, 2.8)),  # Processes to Confirmation
    ]
    
    for (x1, y1), (x2, y2) in sub_arrows:
        ax.arrow(x1, y1, x2-x1, y2-y1, 
                head_width=0.08, head_length=0.08, 
                fc='gray', ec='gray', linewidth=1.5, alpha=0.7)
    
    # Add process descriptions
    ax.text(5, 1.5, 'Data Flow: User Request → Processing → Tool Execution → Data Updates → Response', 
            fontsize=12, ha='center', style='italic')
    ax.text(5, 1, 'All operations include error handling, retry logic, and fallback mechanisms', 
            fontsize=10, ha='center', style='italic', color='gray')
    
    plt.tight_layout()
    plt.savefig('medical_scheduling_dataflow.png', dpi=300, bbox_inches='tight')
    plt.savefig('medical_scheduling_dataflow.pdf', dpi=300, bbox_inches='tight')
    print("✅ Data flow diagram created: medical_scheduling_dataflow.png/pdf")

def convert_markdown_to_formats():
    """Convert markdown to PDF and DOCX using pandoc if available"""
    try:
        # Check if pandoc is available
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
        
        # Convert to PDF
        subprocess.run([
            'pandoc', 'TECHNICAL_ARCHITECTURE.md',
            '-o', 'TECHNICAL_ARCHITECTURE.pdf',
            '--pdf-engine=xelatex',
            '--variable', 'geometry:margin=1in',
            '--variable', 'fontsize=11pt',
            '--toc'
        ], check=True)
        print("✅ PDF created: TECHNICAL_ARCHITECTURE.pdf")
        
        # Convert to DOCX
        subprocess.run([
            'pandoc', 'TECHNICAL_ARCHITECTURE.md',
            '-o', 'TECHNICAL_ARCHITECTURE.docx',
            '--toc'
        ], check=True)
        print("✅ DOCX created: TECHNICAL_ARCHITECTURE.docx")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Pandoc not available. Creating alternative formats...")
        create_html_version()

def create_html_version():
    """Create an HTML version that can be easily converted to PDF"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Medical Scheduling Agent - Technical Architecture</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; }
        h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; }
        h3 { color: #7f8c8d; }
        code { background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
        pre { background-color: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #3498db; color: white; }
        .diagram { text-align: center; margin: 20px 0; }
        .mermaid { background-color: #f8f9fa; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
"""
    
    # Read the markdown content and convert to HTML (basic conversion)
    with open('TECHNICAL_ARCHITECTURE.md', 'r') as f:
        content = f.read()
    
    # Basic markdown to HTML conversion
    content = content.replace('# ', '<h1>').replace('\n## ', '</h1>\n<h2>')
    content = content.replace('\n### ', '</h2>\n<h3>').replace('\n#### ', '</h3>\n<h4>')
    content = content.replace('**', '<strong>').replace('**', '</strong>')
    content = content.replace('`', '<code>').replace('`', '</code>')
    content = content.replace('\n\n', '</p>\n<p>')
    
    html_content += f"<p>{content}</p>"
    html_content += """
</body>
</html>
"""
    
    with open('TECHNICAL_ARCHITECTURE.html', 'w') as f:
        f.write(html_content)
    
    print("✅ HTML created: TECHNICAL_ARCHITECTURE.html (can be printed to PDF from browser)")

def main():
    """Main function to generate all documentation"""
    print("🔧 Generating Medical Scheduling Agent Documentation...")
    
    # Install required packages if not available
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("📦 Installing matplotlib...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'matplotlib'], check=True)
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    
    # Create visual diagrams
    print("\n📊 Creating system architecture diagrams...")
    create_system_architecture_diagram()
    create_data_flow_diagram()
    
    # Convert markdown to other formats
    print("\n📄 Converting documentation to multiple formats...")
    convert_markdown_to_formats()
    
    print("\n✅ Documentation generation complete!")
    print("\nGenerated files:")
    print("- TECHNICAL_ARCHITECTURE.md (Source)")
    print("- TECHNICAL_ARCHITECTURE.html (Browser viewable)")
    print("- medical_scheduling_architecture.png/pdf (System diagram)")
    print("- medical_scheduling_dataflow.png/pdf (Data flow diagram)")
    print("- TECHNICAL_ARCHITECTURE.pdf (if pandoc available)")
    print("- TECHNICAL_ARCHITECTURE.docx (if pandoc available)")

if __name__ == "__main__":
    main()