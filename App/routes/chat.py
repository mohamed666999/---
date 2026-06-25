from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, Conversation, Message
from app.models import ChatRequest, ChatResponse, MessageResponse
from app.aggregator import Aggregator
from datetime import datetime

router = APIRouter(prefix="/api", tags=["chat"])
aggregator = Aggregator()

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    # محادثة
    if req.conversation_id:
        conv = db.query(Conversation).filter_by(id=req.conversation_id).first()
        if not conv:
            raise HTTPException(404, "محادثة غير موجودة")
    else:
        conv = Conversation(title=req.title or "جلسة جديدة")
        db.add(conv)
        db.commit()
        db.refresh(conv)
    
    # جلب الردود
    agg = await aggregator.fetch_all(req.question, req.thinking_enabled)
    
    # تخزين
    msg = Message(
        conversation_id=conv.id,
        user_question=req.question,
        openai_response=agg["details"].get("OpenAI", {}).get("response"),
        anthropic_response=agg["details"].get("Anthropic", {}).get("response"),
        deepseek_response=agg["details"].get("DeepSeek", {}).get("response"),
        deepseek_reasoning=agg["details"].get("DeepSeek", {}).get("reasoning"),
        raw_responses=agg["details"]
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    
    # بناء الرد
    responses = []
    for model, data in agg["details"].items():
        responses.append(MessageResponse(
            model=model.lower(),
            response=data["response"],
            reasoning=data.get("reasoning"),
            tokens=data.get("tokens"),
            latency_ms=data.get("latency_ms"),
            cost=data.get("cost")
        ))
    
    return ChatResponse(
        message_id=msg.id,
        conversation_id=conv.id,
        user_question=req.question,
        responses=responses,
        created_at=msg.created_at
    )
