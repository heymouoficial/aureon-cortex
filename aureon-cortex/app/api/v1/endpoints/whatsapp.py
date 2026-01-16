from fastapi import APIRouter, Request, HTTPException, Depends
from loguru import logger
from app.core.config import get_settings
from app.services.agent_pydantic import pydantic_brain, AureonDependencies

router = APIRouter()
settings = get_settings()

@router.get("/webhook")
async def verify_webhook_standard(request: Request):
    """
    Standard Meta Webhook Verification.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            logger.info("WEBHOOK_VERIFIED")
            return int(challenge) if challenge else challenge
        else:
            logger.warning("WEBHOOK_VERIFICATION_FAILED")
            raise HTTPException(status_code=403, detail="Verification failed")
    
    return {"status": "ok", "message": "Aureon WhatsApp Listener"}

@router.post("/webhook")
async def receive_message(request: Request):
    """
    Receive messages from WhatsApp and process via Pydantic Brain.
    """
    try:
        body = await request.json()
        logger.info(f"WHATSAPP_PAYLOAD: {body}")

        # Check if it's a message
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        
        if "messages" in value:
            message = value["messages"][0]
            msg_body = message.get("text", {}).get("body", "")
            sender_id = message.get("from") # The user phone number
            
            logger.info(f"Message from {sender_id}: {msg_body}")

            # Process with Agnostic Brain
            deps = AureonDependencies(
                organization_id=None, 
                context_data={"source": "whatsapp", "user_id": sender_id}
            )
            
            answer = await pydantic_brain.process_query(
                text=msg_body,
                dependencies=deps
            )
            
            logger.info(f"BRAIN_RESPONSE: {answer[:100]}...")
            
            # TODO: Implement WhatsAppSenderService to actually reply.

        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp Webhook: {e}")
        return {"status": "error", "message": str(e)}
            
            # TODO: Implement WhatsAppSenderService to actually reply.

        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp Webhook: {e}")
        # Always return 200 to Meta to avoid retry loops
        return {"status": "error", "message": str(e)}
