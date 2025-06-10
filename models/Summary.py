from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base  

class Summary(Base):
    __tablename__ = 'Summary'

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    summary_text = Column(Text, nullable=False)
    summary_type = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('User.id')) 

    user = relationship("User", back_populates="summaries")

    def __repr__(self):
        return f"<SummaryRecord(id={self.id}, input_text={self.input_text[:30]}...)>"

