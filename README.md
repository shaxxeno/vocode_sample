
# Telephony AI Assistant with FastAPI

This application sets up a telephony server that leverages AI to handle inbound and outbound phone calls. It uses FastAPI for the web framework, Twilio for telephony services, OpenAI's GPT for conversational AI, Deepgram for speech-to-text transcription, and Azure Cognitive Services for text-to-speech synthesis.

## Features

- **Inbound and Outbound Calls**: Handle incoming calls and initiate outgoing calls via Twilio.
- **Conversational AI**: Engage callers with AI-generated responses using OpenAI's GPT models.
- **Speech Recognition**: Transcribe caller's speech in real-time using Deepgram.
- **Speech Synthesis**: Respond to callers with synthesized speech using Azure Cognitive Services.
- **Web Interface**: Simple web interface to start outbound calls.

## Prerequisites

Before running the application, ensure you have the following:

- **Python 3.7+**
- **Twilio Account**: For telephony services.
- **OpenAI API Key**: For GPT models.
- **Deepgram API Key**: For speech-to-text transcription.
- **Azure Speech Services Key and Region**: For text-to-speech synthesis.
- **Ngrok Account (Optional)**: For exposing local server to the internet.
- **Environment Variables**: Set up required API keys and configurations.

## Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/your-repo.git

2. Create a Virtual Environment

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install Dependencies
    ```bash
    pip install -r requirements.txt

## Configuration

Rename .env.sample to .env set fill in hte environment variables:
    ```bash
    # Base URL (Optional)
    BASE_URL=

    # Ngrok (Optional)
    NGROK_AUTH_TOKEN=

    # Twilio Configuration
    TWILIO_ACCOUNT_SID=your_twilio_account_sid
    TWILIO_AUTH_TOKEN=your_twilio_auth_token
    OUTBOUND_CALLER_NUMBER=your_twilio_phone_number

    # OpenAI Configuration
    OPENAI_API_KEY=your_openai_api_key

    # Deepgram Configuration
    DEEPGRAM_API_KEY=your_deepgram_api_key

    # Azure Speech Services Configuration
    AZURE_SPEECH_KEY=your_azure_speech_key
    AZURE_SPEECH_REGION=your_azure_speech_region


## Running the Application

### Option 1: Automatic Ngrok Setup (Using pyngrok)
1. Start the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 3000
```
If BASE_URL is not set in your .env file, the application will automatically use Ngrok to expose the local server to the internet using pyngrok.
The Ngrok public URL will replace BASE_URL in the application.
The Ngrok URL will be displayed in the console logs (e.g., ngrok tunnel "your-ngrok-url.ngrok.io" -> "http://127.0.0.1:3000").
Access the Web Interface

Open your browser and navigate to http://localhost:3000 for local access.
For external access, use the Ngrok URL displayed in the console logs (e.g., http://your-ngrok-url.ngrok.io).

### Option 2: Manual Ngrok Setup
Start Ngrok Manually

Open a new terminal window and run:

```bash
ngrok http 3000
```
This will expose your local server on port 3000 to the internet.
Copy the forwarding URL provided by Ngrok (e.g., http://your-ngrok-url.ngrok.io).
Set BASE_URL

In your .env file, set the BASE_URL to the Ngrok URL:

```bash
BASE_URL=your-ngrok-url.ngrok.io
```
Ensure you remove http:// or https:// from the URL.

Start the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 3000
```
Access the Web Interface

Open your browser and navigate to http://localhost:3000 for local access.
For external access, use the Ngrok URL you set in BASE_URL (e.g., http://your-ngrok-url.ngrok.io).

