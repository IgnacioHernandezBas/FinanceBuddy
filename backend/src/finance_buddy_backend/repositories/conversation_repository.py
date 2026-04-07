from finance_buddy_backend.db.models import Conversation, Message
from sqlalchemy.orm import Session

class ConversationRepository:
    def __init__(self, db: Session)->None:
        self.db = db

    def create_conversation(self,user_identifier:str |None, title:str |None) -> Conversation:
        conversation = Conversation(user_identifier=user_identifier, title=title)
        self.db.add(conversation)# Add the new conversation to the session
        self.db.commit()# Commit the transaction 
        self.db.refresh(conversation)# Refresh the conversation instance to get the generated ID and other default values from the database
        return conversation

    def get_conversation_by_id(self, conversation_id: int) -> Conversation|None:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def create_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        explanation_level: str | None = None,
        answer_status: str | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            explanation_level=explanation_level,
            answer_status=answer_status,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def list_messages_by_conversation(self, conversation_id: int) -> list[Message]:
        return self.db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
  
    def get_message_by_id(self, message_id: int) -> Message | None:
        return self.db.query(Message).filter(Message.id == message_id).first()