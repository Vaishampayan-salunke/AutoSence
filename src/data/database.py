"""
AutoSense Database Connection & Session Management
Supports MySQL (Production / Docker / Cloud) and SQLite (Local Offline / Antigravity Sandbox)
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class DatasetSource(Base):
    __tablename__ = 'dataset_sources'
    source_id = Column(String(50), primary_key=True)
    source_name = Column(String(150), nullable=False)
    total_records = Column(Integer, default=0)
    license_notes = Column(Text)
    ingestion_status = Column(String(50), default='ACTIVE')
    created_at = Column(DateTime, default=datetime.utcnow)
    reviews = relationship('Review', back_populates='source')

class Review(Base):
    __tablename__ = 'reviews'
    review_id = Column(BigInteger, primary_key=True)
    source_id = Column(String(50), ForeignKey('dataset_sources.source_id'), nullable=True)
    source_name = Column(String(100), nullable=False)
    brand = Column(String(100), index=True)
    vehicle_model = Column(String(100), index=True)
    review_text_original = Column(Text, nullable=False)
    review_text_processed = Column(Text)
    language = Column(String(10), default='en')
    review_date = Column(DateTime, index=True)
    overall_rating = Column(Float)
    original_sentiment_label = Column(String(20))
    normalized_sentiment_label = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    source = relationship('DatasetSource', back_populates='reviews')
    aspects = relationship('ReviewAspect', back_populates='review', cascade='all, delete-orphan')

class ReviewAspect(Base):
    __tablename__ = 'review_aspects'
    aspect_id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(BigInteger, ForeignKey('reviews.review_id'), nullable=False, index=True)
    aspect_category = Column(String(50), nullable=False, index=True)
    aspect_term = Column(String(100))
    opinion_term = Column(String(100))
    aspect_sentiment = Column(String(20), nullable=False, index=True)
    
    review = relationship('Review', back_populates='aspects')

class SqoopImportLog(Base):
    __tablename__ = 'sqoop_import_logs'
    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_table = Column(String(100), nullable=False)
    hdfs_target_dir = Column(String(255), nullable=False)
    records_transferred = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    throughput_records_sec = Column(Float, nullable=False)
    num_mappers = Column(Integer, default=1)
    status = Column(String(50), default='SUCCESS')
    import_timestamp = Column(DateTime, default=datetime.utcnow)

def get_db_engine():
    """
    Returns an active database engine.
    Tries MySQL connection string first; falls back gracefully to SQLite local file.
    """
    db_url = os.getenv('DATABASE_URL')
    if db_url and 'mysql' in db_url:
        try:
            engine = create_engine(db_url, pool_pre_ping=True)
            with engine.connect() as conn:
                pass
            return engine
        except Exception:
            pass # fallback to SQLite
            
    project_root = Path(__file__).resolve().parents[2]
    sqlite_path = os.getenv(
        'SQLITE_DATABASE_PATH',
        str(project_root / 'bigdata' / 'mysql' / 'autosense_local.db')
    )
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    return create_engine(f'sqlite:///{sqlite_path}', echo=False)

def get_session():
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
