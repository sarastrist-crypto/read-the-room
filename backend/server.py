from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class StrategyRequest(BaseModel):
    event_type: str
    room_size: str
    audience_context: str

class StrategyResponse(BaseModel):
    room_energy: str
    opening_move: str
    engagement_anchor: str
    recovery_move: str
    thing_to_avoid: str

# Strategy generation endpoint
@api_router.post("/generate-strategy", response_model=StrategyResponse)
async def generate_strategy(request: StrategyRequest):
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")
        
        system_message = """You are a veteran speaker coach and hospitality expert who has worked thousands of rooms across every format imaginable. Your advice is direct, practical, and specific to the exact room you're asked about. No generic tips. No filler. Strategy only.

When given an event type, room size, and audience context, you provide a concise engagement strategy with exactly these five elements:

1. ROOM ENERGY READ: What to expect walking in. The vibe, the body language patterns, the likely energy level. Be specific.

2. OPENING MOVE: The first 60 seconds. Exactly what to do, say, or establish. Not theory—action.

3. ENGAGEMENT ANCHOR: One technique to build or hold attention throughout. Something you can return to.

4. RECOVERY MOVE: What to do if energy drops. One specific tactical move.

5. ONE THING TO AVOID: The most common mistake for this specific context. Be direct about why.

Your tone is like a trusted stage manager giving notes before curtain. Confident, experienced, zero bullshit."""

        chat = LlmChat(
            api_key=api_key,
            session_id=str(uuid.uuid4()),
            system_message=system_message
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        prompt = f"""Event Type: {request.event_type}
Room Size: {request.room_size}
Audience Context: {request.audience_context}

Provide your engagement strategy. Be specific to THIS room, not rooms in general. Format your response as JSON with these exact keys:
- room_energy: (2-3 sentences)
- opening_move: (2-3 sentences)
- engagement_anchor: (2-3 sentences)
- recovery_move: (2-3 sentences)
- thing_to_avoid: (1-2 sentences)

Return ONLY the JSON object, no markdown formatting."""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse the response
        import json
        try:
            # Clean response if wrapped in markdown
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("```", 1)[0]
                cleaned = cleaned.strip()
            
            strategy_data = json.loads(cleaned)
            return StrategyResponse(**strategy_data)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse AI response: {response}")
            raise HTTPException(status_code=500, detail="Failed to parse AI response")
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Strategy generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/")
async def root():
    return {"message": "Room Reader API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
