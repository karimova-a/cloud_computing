import os
import sys
from x.interviewer import Interviewer
from x.prd_generator import generate_prd

def main():
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Please export it: export GOOGLE_API_KEY='your_key'")
        sys.exit(1)
        
    print("--- Starting JTBD Interviewer Agent ---")
    try:
        interviewer = Interviewer()
        transcript = interviewer.start_interview()
        
        print("\n--- Interview Complete ---")
        print("Generating PRD based on our conversation...")
        
        prd_content = generate_prd(transcript)
        
        output_file = "output_prd.md"
        with open(output_file, "w") as f:
            f.write(prd_content)
            
        print(f"Success! PRD saved to {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
