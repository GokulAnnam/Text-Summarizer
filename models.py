from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SummaryRecord(Base):  
    __tablename__ = 'summaries'

    id = Column(Integer, primary_key=True)
    input_text = Column(Text, nullable=False)
    summary_text = Column(Text, nullable=False)
    summary_type = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
