from fastapi import APIRouter, Request, HTTPException, Depends
from loguru import logger
from app.core.config import get_settings
from app.services.brain import brain_service

router = APIRouter()
settings = get_settings()

@router.get("/webhook")
async def verify_webhook(mode: str = None, token: str = None, challenge: str = None):
    """
    Meta (WhatsApp) Webhook Verification.
    Should return the challenge if the token matches.
    """
    # Meta sends params as: hub.mode, hub.verify_token, hub.challenge
    # But FastAPI might not automatically alias "hub.mode" to "mode" in query params cleanly without extra config 
    # OR we can just read query_params directly if we want to be safe.
    # Actually, let's explicitely look for 'hub.mode' in query params, 
    # BUT FastAPI allows alias. Let's try direct Request object to be 100% sure with Meta's weird naming.
    pass

@router.get("/webhook")
async def verify_webhook_standard(request: Request):
    """
    Manual parsing due to 'hub.' prefix in query params.
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
    Receive messages from WhatsApp.
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

            # Process with Brain
            # Note: We launch this in background or await? 
            # Meta requires 200 OK within seconds. 
            # Ideally we use BackgroundTasks, but for now let's await to see debugging logs live.
            
            response = await brain_service.process_query(
                text=msg_body,
                context={"source": "whatsapp", "user_id": sender_id}
            )
            
            # Here we would SEND the reply back to WhatsApp API
            # For now, we just log the brain's response.
            logger.info(f"BRAIN_RESPONSE: {response.get('text', 'No text')}")
            
            # TODO: Implement WhatsAppSenderService to actually reply.

        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp Webhook: {e}")
        # Always return 200 to Meta to avoid retry loops
        return {"status": "error", "message": str(e)}
