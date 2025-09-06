# Database Conventions - PostgreSQL & pgVector

## Environment Configuration
```bash
PROJECT_NAME=my-awesome-app
STAGE=dev
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
```

## SQLAlchemy Setup
```python
# app/database.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Base Model Pattern
```python
# app/models/base.py
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.sql import func

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
```

## Vector Models
```python
# app/models/document.py
from sqlalchemy import Column, String, Text, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid

class Document(BaseModel):
    __tablename__ = "documents"
    
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI embedding size
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Vector similarity index
    __table_args__ = (
        Index('idx_documents_embedding_hnsw', 'embedding', 
              postgresql_using='hnsw', postgresql_with={'m': 16, 'ef_construction': 64}),
    )

class DocumentChunk(BaseModel):
    __tablename__ = "document_chunks"
    
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Vector(1536))
    document_id = Column(Integer, ForeignKey("documents.id"))
    
    __table_args__ = (
        Index('idx_chunks_embedding_hnsw', 'embedding', postgresql_using='hnsw'),
    )
```

## Vector Search Service
```python
# app/services/vector_search.py
from sqlalchemy import text
from typing import List, Tuple

class VectorSearchService:
    def __init__(self, db):
        self.db = db
    
    def similarity_search(self, query_embedding: List[float], limit: int = 5) -> List[Tuple]:
        """Search for similar documents using cosine similarity"""
        sql = text("""
            SELECT d.*, (1 - (d.embedding <=> :query_vector)) as similarity
            FROM documents d
            WHERE d.is_active = true AND d.embedding IS NOT NULL
            ORDER BY d.embedding <=> :query_vector
            LIMIT :limit
        """)
        
        result = self.db.execute(sql, {
            'query_vector': str(query_embedding),
            'limit': limit
        })
        
        return [(self.db.get(Document, row.id), row.similarity) for row in result]
    
    def hybrid_search(self, query_embedding: List[float], query_text: str, limit: int = 10):
        """Combine vector similarity with full-text search"""
        sql = text("""
            SELECT dc.*, 
                   (1 - (dc.embedding <=> :query_vector)) as vector_similarity,
                   ts_rank(to_tsvector('english', dc.content), plainto_tsquery('english', :query_text)) as text_rank
            FROM document_chunks dc
            WHERE dc.is_active = true AND dc.embedding IS NOT NULL
            ORDER BY 
                (0.7 * (1 - (dc.embedding <=> :query_vector))) + 
                (0.3 * ts_rank(to_tsvector('english', dc.content), plainto_tsquery('english', :query_text))) DESC
            LIMIT :limit
        """)
        
        return self.db.execute(sql, {
            'query_vector': str(query_embedding),
            'query_text': query_text,
            'limit': limit
        }).fetchall()
```

## Repository Pattern
```python
# app/repositories/base.py
from sqlalchemy import and_
from typing import TypeVar, Generic, List, Optional

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db):
        self.model = model
        self.db = db
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(
            and_(self.model.id == id, self.model.is_active == True)
        ).first()
    
    def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        db_obj = self.get_by_id(id)
        if db_obj:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def soft_delete(self, id: int) -> bool:
        db_obj = self.get_by_id(id)
        if db_obj:
            db_obj.is_active = False
            self.db.commit()
            return True
        return False
```

## Migration Setup
```python
# alembic/versions/001_add_vector_extension.py
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

def upgrade():
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create tables with vector columns
    op.create_table('documents',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(255)),
        sa.Column('content', sa.Text),
        sa.Column('embedding', Vector(1536)),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('is_active', sa.Boolean, default=True)
    )
    
    # Create HNSW index for vector similarity
    op.create_index('idx_documents_embedding_hnsw', 'documents', ['embedding'], 
                   postgresql_using='hnsw', postgresql_with={'m': 16, 'ef_construction': 64})

def downgrade():
    op.drop_table('documents')
    op.execute('DROP EXTENSION IF EXISTS vector')
```

## Performance Indexes
```sql
-- Vector similarity indexes
CREATE INDEX CONCURRENTLY idx_documents_embedding_hnsw ON documents USING hnsw (embedding vector_cosine_ops);
CREATE INDEX CONCURRENTLY idx_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops);

-- Full-text search indexes
CREATE INDEX CONCURRENTLY idx_documents_content_gin ON documents USING gin(to_tsvector('english', content));

-- Partial indexes for active records
CREATE INDEX CONCURRENTLY idx_documents_active ON documents(user_id) WHERE is_active = true;
```

## Usage Examples
```python
# Vector search usage
search_service = VectorSearchService(db)

# Similarity search
results = search_service.similarity_search(query_embedding, limit=5)
for doc, similarity in results:
    print(f"Document: {doc.title}, Similarity: {similarity:.3f}")

# Hybrid search
hybrid_results = search_service.hybrid_search(query_embedding, "search query", limit=10)

# Repository usage
doc_repo = DocumentRepository(db)
document = doc_repo.create({
    "title": "Test Document",
    "content": "Document content",
    "embedding": [0.1, 0.2, ...],  # 1536-dimensional vector
    "user_id": 1
})
```

## Best Practices
- **Vector Indexes**: Use HNSW indexes for large datasets (>10k vectors)
- **Embeddings**: Store 1536-dimensional vectors for OpenAI compatibility
- **Hybrid Search**: Combine vector similarity with full-text search
- **Connection Pooling**: Configure pool_size and max_overflow for production
- **Soft Deletes**: Use `is_active` flag instead of hard deletes
- **Migrations**: Always enable pgvector extension before creating vector columns
- **Performance**: Monitor vector search performance and adjust HNSW parameters
- **Backup**: Regular backups including vector data