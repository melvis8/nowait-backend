from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from models import User, Queue, Ticket, Notification
from security import get_password_hash
from typing import Optional, List
import secrets
from fastapi import HTTPException

# Users
async def create_user(db: AsyncSession, nom: str, email: str, password: str, role: str = "client", phone: Optional[str] = None, age: Optional[int] = None) -> User:
    hashed = get_password_hash(password)
    user = User(nom=nom, email=email, mot_de_passe_hash=hashed, role=role, phone=phone, age=age)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    q = await db.execute(select(User).where(User.email == email))
    return q.scalars().first()

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    q = await db.execute(select(User).where(User.user_id == user_id))
    return q.scalars().first()

async def list_users(db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str]=None) -> List[User]:
    stmt = select(User)
    if search:
        stmt = stmt.where(or_(User.nom.ilike(f'%{search}%'), User.email.ilike(f'%{search}%')))
    stmt = stmt.offset(skip).limit(limit)
    q = await db.execute(stmt)
    return q.scalars().all()

# Queues
async def create_queue(db: AsyncSession, nom: str, institution: Optional[str], max_capacity: Optional[int]) -> Queue:
    code_unique = secrets.token_hex(8)
    queue = Queue(nom=nom, institution=institution, code_unique=code_unique, max_capacity=max_capacity)
    db.add(queue)
    await db.commit()
    await db.refresh(queue)
    return queue

async def get_queue(db: AsyncSession, queue_id: int) -> Optional[Queue]:
    q = await db.execute(select(Queue).where(Queue.queue_id == queue_id))
    return q.scalars().first()

async def list_queues(db: AsyncSession, skip: int = 0, limit: int = 100, search: Optional[str]=None):
    stmt = select(Queue)
    if search:
        stmt = stmt.where(Queue.nom.ilike(f'%{search}%') | Queue.institution.ilike(f'%{search}%'))
    stmt = stmt.offset(skip).limit(limit)
    q = await db.execute(stmt)
    return q.scalars().all()

# Tickets
async def next_ticket_number(db: AsyncSession, queue_id: int) -> int:
    q = await db.execute(select(func.max(Ticket.numero)).where(Ticket.queue_id == queue_id))
    max_num = q.scalar_one_or_none()
    return (max_num or 0) + 1


# Priority Logic
def calculate_priority_score(age: Optional[int], severity: str, urgency: str) -> int:
    score = 0
    
    # Severity weights
    severity_map = {"low": 1, "medium": 3, "high": 5}
    score += severity_map.get(severity.lower(), 1) * 10
    
    # Urgency weights
    urgency_map = {"low": 1, "medium": 3, "high": 5}
    score += urgency_map.get(urgency.lower(), 1) * 10
    
    # Age weights (Prioritize elderly > 60 and children < 5)
    if age:
        if age >= 60:
            score += 20
        elif age <= 5:
            score += 15
            
    return score

async def create_ticket(db: AsyncSession, queue_id: int, user_id: Optional[int], prioritaire: bool=False, severity: str="low", urgency: str="low") -> Ticket:
    numero = await next_ticket_number(db, queue_id)
    
    # Get user age if user_id is present to calculate priority
    age = None
    if user_id:
        user = await get_user(db, user_id)
        if user:
            age = user.age
            
    p_score = calculate_priority_score(age, severity, urgency)
    if prioritaire:
        p_score += 50 # Manual override boosts score significantly
        
    ticket = Ticket(
        queue_id=queue_id, 
        user_id=user_id, 
        numero=numero, 
        statut="attente", 
        prioritaire=prioritaire,
        severity=severity,
        urgency=urgency,
        priority_score=p_score
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket

async def get_ticket(db: AsyncSession, ticket_id: int) -> Optional[Ticket]:
    q = await db.execute(select(Ticket).where(Ticket.ticket_id == ticket_id))
    return q.scalars().first()

async def cancel_ticket(db: AsyncSession, ticket_id: int) -> Ticket:
    ticket = await get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.cancelled = True
    ticket.statut = "annule"
    await db.commit()
    await db.refresh(ticket)
    return ticket

async def call_next(db: AsyncSession, queue_id: int) -> Optional[Ticket]:
    q = await db.execute(
        select(Ticket)
        .where(Ticket.queue_id==queue_id, Ticket.statut=="attente", Ticket.cancelled==False)
        .order_by(desc(Ticket.priority_score), Ticket.heure_arrivee)
    )
    next_ticket = q.scalars().first()
    if not next_ticket:
        return None
    next_ticket.statut = "appele"
    await db.commit()
    await db.refresh(next_ticket)
    return next_ticket

async def ticket_history(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    q = await db.execute(
        select(Ticket)
        .where(Ticket.user_id==user_id)
        .order_by(Ticket.heure_arrivee.desc())
        .offset(skip)
        .limit(limit)
    )
    return q.scalars().all()

async def update_ticket_status(db: AsyncSession, ticket_id: int, status: str) -> Optional[Ticket]:
    ticket = await get_ticket(db, ticket_id)
    if not ticket:
        return None
        
    ticket.statut = status
    if status == "traite":
        ticket.heure_fin = func.now()
        
    await db.commit()
    await db.refresh(ticket)
    return ticket

async def get_queue_stats(db: AsyncSession, queue_id: int):
    # Calculate average wait time (heure_passage - heure_arrivee) for treated tickets
    # This is a bit complex with async SQLAlchemy + sqlite/pg differences, so we do a simple fetch and calc for MVP or use SQL func
    # Let's try to do it in python for simplicity if volume is low, or SQL if high.
    # We will use SQL avg.
    
    # Avg wait time (Time until called)
    stmt = select(func.avg(func.extract('epoch', Ticket.heure_passage) - func.extract('epoch', Ticket.heure_arrivee)))\
        .where(Ticket.queue_id == queue_id, Ticket.statut == 'traite', Ticket.heure_passage != None)
    
    result = await db.execute(stmt)
    avg_seconds = result.scalar() or 0
    
    # Waiting count
    count_stmt = select(func.count(Ticket.ticket_id)).where(Ticket.queue_id == queue_id, Ticket.statut == 'attente')
    count_res = await db.execute(count_stmt)
    waiting_count = count_res.scalar() or 0
    
    return {
        "average_wait_time_minutes": round(avg_seconds / 60, 2),
        "waiting_candidates": waiting_count
    }

async def get_queue_tickets(db: AsyncSession, queue_id: int, status: Optional[str] = None, skip: int = 0, limit: int = 100):
    stmt = select(Ticket).where(Ticket.queue_id == queue_id)
    if status:
        stmt = stmt.where(Ticket.statut == status)
    # Sort by priority score desc, then arrival time
    stmt = stmt.order_by(desc(Ticket.priority_score), Ticket.heure_arrivee).offset(skip).limit(limit)
    q = await db.execute(stmt)
    return q.scalars().all()

# Notifications
async def create_notification(db: AsyncSession, user_id: int, type_: str, message: str) -> Notification:
    n = Notification(user_id=user_id, type=type_, message=message)
    db.add(n)
    await db.commit()
    await db.refresh(n)
    return n
