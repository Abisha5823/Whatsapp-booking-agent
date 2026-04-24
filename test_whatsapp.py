import httpx
import json

async def send_whatsapp_message():
    token = "EAAcuyzxKpxkBReSXeNywfYS9p3njaqcZC1vs8w15MpE6H3o3skpKFTEcBVLp5bHl9DLqpTOlYJ7FcVk4DV87RmY5ZB0WB7JwReNcZB8G4ZA7pXdQz04D2NCgIJOZCBkmDG1GffM7rAt4ZAZAlFUunNyk3pVZAGTTqtLVXTPPpFYkwWKBaWNyU6hZCBMVim7vCDu0UsiLMpZCVkI2shZCCmQSYq5gOWPxsIokr973dqGVyOCNXsuYtQQwIOFvLQ0MFH6VgLBocUrp6R4ZCt3vYtJUG8pn"
    phone_id = "1128769140300257"
    
    url = f"https://graph.facebook.com/v25.0/{phone_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": "919791744224",
        "type": "text",
        "text": {
            "body": "Hello! Your booking assistant is ready! 🎉 Send 'I need appointment' to start."
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Message sent successfully! Check your WhatsApp!")
        else:
            print(f"\n❌ Error: {response.text}")

# Run it
import asyncio
asyncio.run(send_whatsapp_message())