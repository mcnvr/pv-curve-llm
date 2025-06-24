"""
This file is to test input collection, interaction, and command processing through an AI interface.

Eventually this will be used to collect inputs for PV-Curve analysis and input validation through natural language.

Current method: Specify commands to AI and have it respond with those commands. 
"""

import json
import os
import threading
import time
import sys
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

model = OllamaLLM(model="deepseek-r1:1.5b")

# File to store collected inputs
INPUTS_FILE = "collected_inputs.json"

# Define required inputs
REQUIRED_INPUTS = {
    "Input 1": "Please provide Input 1 (describe what you want for the first parameter)",
    "Input 2": "Please provide Input 2 (describe what you want for the second parameter)", 
    "Input 3": "Please provide Input 3 (describe what you want for the third parameter)",
    "Input 4": "Please provide Input 4 (describe what you want for the fourth parameter)",
    "Input 5": "Please provide Input 5 (describe what you want for the fifth parameter)"
}

# Global variables for processing animation
processing_active = False
processing_thread = None

def processing_animation():
    """Display processing animation with dots"""
    global processing_active
    print("\n🔄 Processing", end="", flush=True)
    dot_count = 0
    
    while processing_active:
        time.sleep(3)
        if processing_active:
            print(".", end="", flush=True)
            dot_count += 1

def start_processing():
    """Start the processing animation"""
    global processing_active, processing_thread
    processing_active = True
    processing_thread = threading.Thread(target=processing_animation, daemon=True)
    processing_thread.start()

def stop_processing():
    """Stop the processing animation"""
    global processing_active
    processing_active = False
    if processing_thread:
        processing_thread.join(timeout=0.1)
    print()

def load_inputs():
    """Load previously collected inputs from file"""
    if os.path.exists(INPUTS_FILE):
        with open(INPUTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_inputs(inputs):
    """Save inputs to file"""
    with open(INPUTS_FILE, 'w') as f:
        json.dump(inputs, f, indent=2)

def get_missing_inputs(collected_inputs):
    """Get list of inputs that haven't been collected yet"""
    missing = []
    for input_key in REQUIRED_INPUTS.keys():
        if input_key not in collected_inputs or not collected_inputs[input_key]:
            missing.append(input_key)
    return missing

def command_detection_template():
    """Template for detecting delete/modify commands"""
    return ChatPromptTemplate.from_template("""
You are an AI assistant that detects user commands for managing inputs.

Current inputs that exist:
{existing_inputs}

User's message: {user_message}

Analyze if the user wants to:
1. Delete specific input(s)
2. Modify/change specific input(s)  
3. Delete all inputs
4. Or if this is just a regular input collection message

Respond in this exact format:
COMMAND_TYPE: [DELETE_SPECIFIC / MODIFY_SPECIFIC / DELETE_ALL / NONE]
TARGET_INPUTS: [list of input names like "Input 1, Input 3" or "ALL" or "NONE"]
NEW_VALUES: [if modifying, the new values, otherwise "NONE"]
EXPLANATION: [brief explanation of what the user wants to do]
""")

def extract_all_inputs_template():
    """Template for extracting all inputs from user response at once"""
    return ChatPromptTemplate.from_template("""
You are an AI assistant helping to extract specific inputs from a user's response.

The user needs to provide the following inputs:
{required_inputs}

Missing inputs that need to be extracted:
{missing_inputs}

User's response: {user_response}

Your task is to analyze the user's response and extract values for each missing input. 
Be intelligent about matching the user's provided information to the appropriate input categories.
NEVER include "NOT_FOUND" or similar phrases as actual values - only extract real, meaningful values.

Respond in this exact format for each missing input:
INPUT_1: [extracted value or "NOT_FOUND" if not provided]
INPUT_2: [extracted value or "NOT_FOUND" if not provided]
INPUT_3: [extracted value or "NOT_FOUND" if not provided]
INPUT_4: [extracted value or "NOT_FOUND" if not provided]
INPUT_5: [extracted value or "NOT_FOUND" if not provided]

MISSING: [list any inputs that were not found in the user's response]
NEXT_PROMPT: [what to ask the user for any missing inputs, or "COMPLETE" if all found]
""")

def general_chat_template():
    """Template for general conversation when all inputs are collected"""
    return ChatPromptTemplate.from_template("""
You are an expert in Power Systems and Electrical Engineering, more specifically in Voltage Stability
and the application of Power-Voltage PV Curves (Nose Curves).

All required inputs have been collected from the user:
{collected_inputs}

Here is relevant context: {context}

User question: {question}

Provide a helpful response using the collected inputs and context when relevant.
""")

def display_required_inputs(missing_inputs):
    """Display what inputs are needed"""
    print("📋 Required Inputs:")
    print("=" * 50)
    for i, input_key in enumerate(missing_inputs, 1):
        print(f"{i}. {input_key}: {REQUIRED_INPUTS[input_key]}")
    print("=" * 50)
    print("💡 You can provide all inputs in one response. The AI will automatically")
    print("   extract and categorize each input based on your description.")
    print("💡 You can also say things like 'delete input 2' or 'change input 1 to 220V'")
    print()

def is_valid_input_value(value):
    """Check if a value is valid (not NOT_FOUND or similar)"""
    if not value or not isinstance(value, str):
        return False
    
    value_lower = value.lower().strip()
    invalid_phrases = [
        "not_found", "not found", "insufficient context", 
        "no information", "missing", "unclear", "unknown",
        "not provided", "not specified", "not mentioned"
    ]
    
    # Check if the value contains any invalid phrases
    for phrase in invalid_phrases:
        if phrase in value_lower:
            return False
    
    # Check if it's just "NOT_FOUND" or similar patterns
    if value_lower in ["not_found", "none", "null", "n/a", ""]:
        return False
        
    return True

def process_command(user_message, collected_inputs):
    """Process delete/modify commands using AI"""
    # Allow command detection even if no inputs exist (for "clear all" type commands)
    existing_inputs_text = "\n".join([f"- {key}: {value}" for key, value in collected_inputs.items()]) if collected_inputs else "No inputs currently exist"
    
    command_chain = command_detection_template() | model
    
    try:
        response = command_chain.invoke({
            "existing_inputs": existing_inputs_text,
            "user_message": user_message
        })
        
        # Parse the response
        lines = response.strip().split('\n')
        command_type = ""
        target_inputs = ""
        new_values = ""
        explanation = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("COMMAND_TYPE:"):
                command_type = line.replace("COMMAND_TYPE:", "").strip()
            elif line.startswith("TARGET_INPUTS:"):
                target_inputs = line.replace("TARGET_INPUTS:", "").strip()
            elif line.startswith("NEW_VALUES:"):
                new_values = line.replace("NEW_VALUES:", "").strip()
            elif line.startswith("EXPLANATION:"):
                explanation = line.replace("EXPLANATION:", "").strip()
        
        if command_type == "NONE":
            return False, "No command detected."
        
        # Execute the command
        if command_type == "DELETE_ALL":
            collected_inputs.clear()
            return True, "🗑️ All inputs have been deleted."
        
        elif command_type == "DELETE_SPECIFIC":
            if target_inputs and target_inputs != "NONE":
                deleted = []
                for target in target_inputs.split(","):
                    target = target.strip()
                    if target in collected_inputs:
                        del collected_inputs[target]
                        deleted.append(target)
                
                if deleted:
                    return True, f"🗑️ Deleted: {', '.join(deleted)}"
                else:
                    return True, "❌ No matching inputs found to delete."
        
        elif command_type == "MODIFY_SPECIFIC":
            if target_inputs and target_inputs != "NONE" and new_values and new_values != "NONE":
                modified = []
                targets = [t.strip() for t in target_inputs.split(",")]
                
                # Simple modification - assume one target, one value for now
                if len(targets) == 1 and targets[0] in collected_inputs:
                    collected_inputs[targets[0]] = new_values
                    modified.append(targets[0])
                
                if modified:
                    return True, f"✏️ Modified {modified[0]}: {new_values}"
                else:
                    return True, "❌ Could not modify the specified input."
        
        return True, f"🤔 {explanation}"
        
    except Exception as e:
        return False, f"Error processing command: {e}"

def main():
    print("🔄 Interactive PV-Curve Analysis System")
    print("=" * 50)
    
    # Load existing inputs
    collected_inputs = load_inputs()
    
    # Check what's missing
    missing_inputs = get_missing_inputs(collected_inputs)
    
    if missing_inputs:
        print(f"📝 You have {len(missing_inputs)} inputs remaining to complete.")
        print("Collected so far:", list(collected_inputs.keys()) if collected_inputs else "None")
        print()
        
        display_required_inputs(missing_inputs)
        
    else:
        print("✅ All inputs have been collected!")
        print("Collected inputs:", json.dumps(collected_inputs, indent=2))
        print("\nYou can now ask questions about PV-Curves, and I'll use your inputs when relevant.\n")
    
    extract_chain = extract_all_inputs_template() | model
    chat_chain = general_chat_template() | model
    
    while True:
        # Determine what to ask for
        missing_inputs = get_missing_inputs(collected_inputs)
        
        if missing_inputs:
            # Ask for all missing inputs at once
            print(f"🎯 Please provide all {len(missing_inputs)} missing inputs in your response:")
            print("   " + ", ".join(missing_inputs))
            user_response = input("\n👤 Your response: ")
        else:
            # All inputs collected, normal chat mode
            user_response = input("\n👤 Ask anything about PV-Curves: ")
        
        if user_response.lower() in ['quit', 'exit', 'q']:
            break
            
        if user_response.lower() == 'status':
            missing = get_missing_inputs(collected_inputs)
            print(f"\n📊 Status:")
            print(f"   Collected: {list(collected_inputs.keys())}")
            print(f"   Missing: {missing}")
            if missing:
                display_required_inputs(missing)
            continue
            
        if user_response.lower() == 'reset':
            collected_inputs = {}
            save_inputs(collected_inputs)
            print("🔄 All inputs have been reset.")
            display_required_inputs(list(REQUIRED_INPUTS.keys()))
            continue
        
        # Check for delete/modify commands first (check even if no inputs exist for "clear all")
        start_processing()
        try:
            command_processed, command_result = process_command(user_response, collected_inputs)
            stop_processing()
            
            if command_processed:
                print(command_result)
                save_inputs(collected_inputs)  # This is crucial - save after any command
                
                # Update missing inputs after command
                missing_inputs = get_missing_inputs(collected_inputs)
                if missing_inputs:
                    print(f"\n📝 Remaining inputs needed: {len(missing_inputs)}")
                    display_required_inputs(missing_inputs)
                else:
                    print("✅ All inputs have been collected!")
                continue
            else:
                stop_processing()
        except Exception as e:
            stop_processing()
            print(f"❌ Error processing command: {e}")
        
        # Start processing animation
        start_processing()
        
        try:
            # Process the response
            if missing_inputs:
                # We're collecting inputs
                try:
                    # Format the required inputs for the prompt
                    required_inputs_text = "\n".join([f"- {key}: {desc}" for key, desc in REQUIRED_INPUTS.items()])
                    missing_inputs_text = ", ".join(missing_inputs)
                    
                    response = extract_chain.invoke({
                        "required_inputs": required_inputs_text,
                        "missing_inputs": missing_inputs_text,
                        "user_response": user_response
                    })
                    
                    # Stop processing animation
                    stop_processing()
                    
                    # Parse the response
                    lines = response.strip().split('\n')
                    extracted_inputs = {}
                    missing_list = []
                    next_prompt = ""
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith("INPUT_1:"):
                            value = line.replace("INPUT_1:", "").strip()
                            if value != "NOT_FOUND" and "Input 1" in missing_inputs and is_valid_input_value(value):
                                extracted_inputs["Input 1"] = value
                        elif line.startswith("INPUT_2:"):
                            value = line.replace("INPUT_2:", "").strip()
                            if value != "NOT_FOUND" and "Input 2" in missing_inputs and is_valid_input_value(value):
                                extracted_inputs["Input 2"] = value
                        elif line.startswith("INPUT_3:"):
                            value = line.replace("INPUT_3:", "").strip()
                            if value != "NOT_FOUND" and "Input 3" in missing_inputs and is_valid_input_value(value):
                                extracted_inputs["Input 3"] = value
                        elif line.startswith("INPUT_4:"):
                            value = line.replace("INPUT_4:", "").strip()
                            if value != "NOT_FOUND" and "Input 4" in missing_inputs and is_valid_input_value(value):
                                extracted_inputs["Input 4"] = value
                        elif line.startswith("INPUT_5:"):
                            value = line.replace("INPUT_5:", "").strip()
                            if value != "NOT_FOUND" and "Input 5" in missing_inputs and is_valid_input_value(value):
                                extracted_inputs["Input 5"] = value
                        elif line.startswith("MISSING:"):
                            missing_text = line.replace("MISSING:", "").strip()
                            if missing_text and missing_text != "None":
                                missing_list = [item.strip() for item in missing_text.split(",")]
                        elif line.startswith("NEXT_PROMPT:"):
                            next_prompt = line.replace("NEXT_PROMPT:", "").strip()
                    
                    if extracted_inputs:
                        # Some inputs were successfully extracted
                        for input_key, value in extracted_inputs.items():
                            collected_inputs[input_key] = value
                            print(f"✅ Extracted {input_key}: {value}")
                        
                        save_inputs(collected_inputs)
                        
                        # Check if we have more inputs to collect
                        remaining = get_missing_inputs(collected_inputs)
                        if remaining:
                            print(f"📝 {len(remaining)} inputs still needed: {remaining}")
                            if next_prompt and next_prompt != "COMPLETE":
                                print(f"💭 {next_prompt}")
                        else:
                            print("🎉 All inputs collected! You can now ask questions about PV-Curves.")
                    else:
                        # No inputs were extracted
                        if next_prompt:
                            print(f"🤔 {next_prompt}")
                        else:
                            print("🤔 I couldn't extract the required inputs from your response.")
                            print("Please try again with clearer descriptions for each input.")
                            
                except Exception as e:
                    stop_processing()
                    print(f"❌ Error processing input: {e}")
                    print("Please try again.")
                    
            else:
                # Normal chat mode - all inputs collected
                try:
                    context = retriever.invoke(user_response)
                    response = chat_chain.invoke({
                        "collected_inputs": json.dumps(collected_inputs, indent=2),
                        "context": context,
                        "question": user_response
                    })
                    
                    # Stop processing animation
                    stop_processing()
                    
                    print(f"\n🤖 AI Response:")
                    print(response)
                    
                except Exception as e:
                    stop_processing()
                    print(f"❌ Error: {e}")
        
        except KeyboardInterrupt:
            stop_processing()
            print("\n\n❌ Processing interrupted by user.")
        except Exception as e:
            stop_processing()
            print(f"\n❌ Unexpected error: {e}")
    
    print("\n👋 Session ended. Your inputs have been saved.")
    final_missing = get_missing_inputs(collected_inputs)
    if final_missing:
        print(f"📝 Still missing: {final_missing}")
        print("Run the script again to continue collecting inputs.")

if __name__ == "__main__":
    main() 