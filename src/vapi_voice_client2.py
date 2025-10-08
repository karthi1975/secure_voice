#!/usr/bin/env python3
import json
import time
from vapi_python import Vapi

class VoiceAssistant:
    def __init__(self):
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        
        self.vapi = Vapi(api_key=config['vapi_api_key'])
        self.assistant_id = config['vapi_assistant_id']
        self.customer_id = config['customer_id']
        self.password = config['password']
    
    def start(self):
        """Start authenticated voice session."""
        print(f"🎤 Starting session...")
        print(f"🔐 Customer: {self.customer_id}")
        print("🗣️  Start speaking!\n")
        
        # Start with authentication in metadata
        self.vapi.start(
            assistant_id=self.assistant_id,
            assistant_overrides={
                'firstMessage': "Hi! How can I help?",
                
                # Send credentials for validation
                'metadata': {
                    'customer_id': self.customer_id,
                    'password': self.password,
                    'authenticated': True
                },
                
                # Better transcription
                'transcriber': {
                    'provider': 'deepgram',
                    'model': 'nova-2'
                }
            }
        )
        
        print("✅ Session active! Press Ctrl+C to stop.\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Stopping...")
            self.vapi.stop()
            print("✅ Done!")

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.start()