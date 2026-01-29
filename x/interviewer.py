import google.generativeai as genai
import os

class Interviewer:
    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        self.system_instruction = """
        You are an expert Product Manager and User Researcher conducting a Jobs to be Done (JTBD) interview. 
        Your goal is to understand the underlying progress the user is trying to make.
        
        You strictly follow this process:
        1. Start by asking the user what problem they are trying to solve or what task they are trying to accomplish.
        2. Once they answer, apply the "5 Whys" technique. You must dig deep into their motivation.
        3. Do NOT ask "Why" 5 times in a row mechanically. incorporate it conversationally (e.g., "What makes that important to you?", "What happens if you can't do that?", "Why is that a blocker?").
        4. Continue this back-and-forth until you have peeled back at least 5 layers of depth or reached a fundamental emotional/social driver.
        5. Once you feel you have enough information (after at least 5-7 turns), politely conclude the interview by saying "Thank you, I have enough information to generate your PRD."
        
        Keep your responses concise and inquisitive. Do not solve the problem for them yet. Just listen and probe.
        """
        
        self.model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=self.system_instruction)
        self.chat = self.model.start_chat(history=[])
        self.transcript = []

    def start_interview(self):
        print("Agent: Hello! I'm your JTBD Interviewer. Tell me, what problem or idea are you thinking about today?")
        self.transcript.append("Agent: Hello! I'm your JTBD Interviewer. Tell me, what problem or idea are you thinking about today?")
        
        while True:
            user_input = input("You: ")
            self.transcript.append(f"User: {user_input}")
            
            response = self.chat.send_message(user_input)
            print(f"Agent: {response.text}")
            self.transcript.append(f"Agent: {response.text}")
            
            if "generate your PRD" in response.text or "have enough information" in response.text:
                break
        
        return "\n".join(self.transcript)
