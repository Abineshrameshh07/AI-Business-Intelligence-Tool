from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Upload(Base):
    
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)          
    file_type = Column(String, nullable=False)         
    file_path = Column(String, nullable=False)         
    status = Column(String, default="uploaded")        
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AnalysisResult(Base):

    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, nullable=False)
    summary_text = Column(Text, nullable=True)          # AI-written summary
    chart_config_json = Column(Text, nullable=True)     # JSON describing chart(s) to render
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
