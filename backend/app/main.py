import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./collabdocs.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(engine)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[dict] = mapped_column(JSON, default=lambda: {"type": "doc", "content": [{"type": "paragraph"}]})
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    owner: Mapped[User] = relationship()

class Share(Base):
    __tablename__ = "shares"
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

class DocumentInput(BaseModel):
    title: str = Field(default="Untitled document", min_length=1, max_length=200)

class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: dict[str, Any] | None = None

class ShareInput(BaseModel):
    user_id: int

app = FastAPI(title="CollabDocs API")
origins = [s.strip() for s in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if s.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.scalar(select(User.id).limit(1)):
            db.add_all([User(id=1, name="Alice"), User(id=2, name="Bob")])
            db.commit()

def get_db():
    with SessionLocal() as db:
        yield db

def current_user(x_user_id: int = Header(default=1), db: Session = Depends(get_db)) -> User:
    user = db.get(User, x_user_id)
    if not user:
        raise HTTPException(401, "Unknown demo user")
    return user

def document_access(db: Session, document_id: int, user: User, owner_only: bool = False) -> Document:
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    if doc.owner_id != user.id and (owner_only or not db.get(Share, (doc.id, user.id))):
        raise HTTPException(403, "Access denied")
    return doc

def serialize(doc: Document, user: User) -> dict:
    return {"id": doc.id, "title": doc.title, "content": doc.content, "owner_id": doc.owner_id, "owner_name": doc.owner.name, "updated_at": doc.updated_at.isoformat(), "can_edit": doc.owner_id == user.id}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/users")
def users(db: Session = Depends(get_db)):
    return [{"id": u.id, "name": u.name} for u in db.scalars(select(User).order_by(User.id))]

@app.get("/documents")
def list_documents(user: User = Depends(current_user), db: Session = Depends(get_db)):
    owned = db.scalars(select(Document).where(Document.owner_id == user.id).order_by(Document.updated_at.desc())).all()
    shared = db.scalars(select(Document).join(Share).where(Share.user_id == user.id, Document.owner_id != user.id).order_by(Document.updated_at.desc())).all()
    return {"mine": [serialize(d, user) for d in owned], "shared": [serialize(d, user) for d in shared]}

@app.post("/documents", status_code=201)
def create_document(body: DocumentInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    doc = Document(title=body.title.strip(), owner_id=user.id, content={"type": "doc", "content": [{"type": "paragraph"}]})
    if not doc.title:
        raise HTTPException(422, "Title cannot be blank")
    db.add(doc); db.commit(); db.refresh(doc)
    return serialize(doc, user)

@app.get("/documents/{document_id}")
def get_document(document_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return serialize(document_access(db, document_id, user), user)

@app.patch("/documents/{document_id}")
def update_document(document_id: int, body: DocumentUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    doc = document_access(db, document_id, user, True)
    if body.title is not None:
        doc.title = body.title.strip()
        if not doc.title:
            raise HTTPException(422, "Title cannot be blank")
    if body.content is not None:
        if body.content.get("type") != "doc":
            raise HTTPException(422, "Invalid Tiptap document")
        doc.content = body.content
    doc.updated_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(doc)
    return serialize(doc, user)

@app.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    doc = document_access(db, document_id, user, True)
    db.query(Share).filter(Share.document_id == doc.id).delete()
    db.delete(doc); db.commit()

@app.post("/documents/{document_id}/share")
def share_document(document_id: int, body: ShareInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    doc = document_access(db, document_id, user, True)
    target = db.get(User, body.user_id)
    if not target or target.id == user.id:
        raise HTTPException(422, "Choose another demo user")
    if not db.get(Share, (doc.id, target.id)):
        db.add(Share(document_id=doc.id, user_id=target.id)); db.commit()
    return {"shared_with": target.name}

@app.post("/documents/import", status_code=201)
async def import_document(file: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(get_db)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in (".txt", ".md"):
        raise HTTPException(422, "Only .txt and .md files are supported")
    raw = await file.read(1_000_001)
    if len(raw) > 1_000_000:
        raise HTTPException(413, "File must be 1 MB or smaller")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(422, "File must be UTF-8 encoded")
    nodes = []
    for line in text.splitlines():
        if suffix == ".md" and line.startswith("#"):
            level = min(len(line) - len(line.lstrip("#")), 3)
            nodes.append({"type": "heading", "attrs": {"level": level}, "content": [{"type": "text", "text": line[level:].strip()}]})
        elif line.strip():
            nodes.append({"type": "paragraph", "content": [{"type": "text", "text": line}]})
        else:
            nodes.append({"type": "paragraph"})
    doc = Document(title=Path(file.filename or "Imported").stem[:200], owner_id=user.id, content={"type": "doc", "content": nodes or [{"type": "paragraph"}]})
    db.add(doc); db.commit(); db.refresh(doc)
    return serialize(doc, user)
