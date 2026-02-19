#!/bin/bash

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY is not set."
    echo "Please export your API key first:"
    echo "  export GOOGLE_API_KEY='your_api_key_here'"
    exit 1
fi

# Run the judge script
echo "Running Judge Agent..."
python3 judge.py

# Check if report was generated
if [ -f "compliance_report.json" ]; then
    echo "Success! Compliance report generated at compliance_report.json"
    cat compliance_report.json
else
    echo "Failed to generate compliance report."
fi
