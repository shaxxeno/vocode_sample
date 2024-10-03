import logging
import os
import sys
from typing import Optional

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from vocode.logging import configure_pretty_logging
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.telephony.conversation.outbound_call import OutboundCall
from vocode.streaming.telephony.server.base import TwilioInboundCallConfig, TelephonyServer
from vocode.streaming.models.synthesizer import AzureSynthesizerConfig
from vocode.streaming.models.transcriber import (
    DeepgramTranscriberConfig,
    PunctuationEndpointingConfig,
)
from vocode.streaming.telephony.config_manager.in_memory_config_manager import InMemoryConfigManager

load_dotenv()

configure_pretty_logging()

app = FastAPI(docs_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="templates")

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    from pyngrok import ngrok
    ngrok_auth = os.getenv("NGROK_AUTH_TOKEN")
    if ngrok_auth is not None:
        ngrok.set_auth_token(ngrok_auth)
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 3000
    public_url = ngrok.connect(port).public_url
    BASE_URL = public_url.replace("https://", "").replace("http://", "")
    logger.info(f'ngrok tunnel "{BASE_URL}" -> "http://127.0.0.1:{port}"')

TWILIO_CONFIG = TwilioConfig(
    account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
    auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
)


TWILIO_PHONE = os.getenv("OUTBOUND_CALLER_NUMBER")

CONFIG_MANAGER = InMemoryConfigManager()

AGENT_CONFIG = ChatGPTAgentConfig(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    initial_message=BaseMessage(text="What up guys, its me - Mario!"),
    prompt_preamble="The AI is having a pleasant conversation about life",
    generate_responses=True,
)

SYNTH_CONFIG = AzureSynthesizerConfig.from_telephone_output_device(
    azure_speech_key=os.getenv("AZURE_SPEECH_KEY"),
    azure_speech_region=os.getenv("AZURE_SPEECH_REGION"),
)

TRANSCRIBER_CONFIG = DeepgramTranscriberConfig(
    api_key=os.getenv("DEEPGRAM_API_KEY"),
    sampling_rate=8000,
    audio_encoding="mulaw",
    endpointing_config=PunctuationEndpointingConfig(),
    chunk_size=1000
)

telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=CONFIG_MANAGER,
    inbound_call_configs=[
        TwilioInboundCallConfig(
            url="/inbound_call",
            agent_config=AGENT_CONFIG,
            twilio_config=TWILIO_CONFIG,
            synthesizer_config=SYNTH_CONFIG,
            transcriber_config=TRANSCRIBER_CONFIG,
        )
    ],
)
app.include_router(telephony_server.get_router())

async def start_outbound_call(to_phone: Optional[str]):
    if to_phone:
        outbound_call = OutboundCall(
            base_url=BASE_URL,
            to_phone=to_phone,
            from_phone=TWILIO_PHONE,
            telephony_config=TWILIO_CONFIG,
            config_manager=CONFIG_MANAGER,
            agent_config=AGENT_CONFIG,
            synthesizer_config=SYNTH_CONFIG,
            transcriber_config=TRANSCRIBER_CONFIG,
        )
        await outbound_call.start()

@app.get("/")
async def root(request: Request):

    env_vars = {
        "BASE_URL": BASE_URL,
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "DEEPGRAM_API_KEY": os.getenv("DEEPGRAM_API_KEY"),
        "AZURE_SPEECH_KEY": os.getenv("AZURE_SPEECH_KEY"),
        "AZURE_SPEECH_REGION": os.getenv("AZURE_SPEECH_REGION"),
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID"),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN"),
        "OUTBOUND_CALLER_NUMBER": os.getenv("OUTBOUND_CALLER_NUMBER"),
    }
    return templates.TemplateResponse("index.html", {"request": request, "env_vars": env_vars})

@app.post("/start_outbound_call")
async def api_start_outbound_call(to_phone: Optional[str] = Form(None)):
    await start_outbound_call(to_phone)
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)

