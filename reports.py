from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from deps import get_db_dep, require_roles
from models import Ticket, Queue
from typing import Dict

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/queue/{queue_id}/stats", dependencies=[Depends(require_roles("admin","agent"))])
async def queue_stats(queue_id: int, db: AsyncSession = Depends(get_db_dep)) -> Dict:
    # total tickets, waiting, called, finished, avg wait time (approx)
    q_total = await db.execute(select(func.count(Ticket.ticket_id)).where(Ticket.queue_id==queue_id))
    total = q_total.scalar_one()
    q_wait = await db.execute(select(func.count(Ticket.ticket_id)).where(Ticket.queue_id==queue_id, Ticket.statut=="attente"))
    waiting = q_wait.scalar_one()
    q_called = await db.execute(select(func.count(Ticket.ticket_id)).where(Ticket.queue_id==queue_id, Ticket.statut=="appele"))
    called = q_called.scalar_one()
    q_done = await db.execute(select(func.count(Ticket.ticket_id)).where(Ticket.queue_id==queue_id, Ticket.statut=="traite"))
    done = q_done.scalar_one()
    q_absent = await db.execute(select(func.count(Ticket.ticket_id)).where(Ticket.queue_id==queue_id, Ticket.statut=="absent"))
    absent = q_absent.scalar_one()
    q_skipped = await db.execute(select(func.count(Ticket.ticket_id)).where(Ticket.queue_id==queue_id, Ticket.statut=="saute"))
    skipped = q_skipped.scalar_one()
    
    # avg wait time: avg(heure_passage - heure_arrivee) for treated tickets
    # Note: ensure database supports extract epoch or use appropriate func
    q_avg = await db.execute(select(func.avg(func.extract('epoch', Ticket.heure_passage) - func.extract('epoch', Ticket.heure_arrivee))).where(Ticket.queue_id==queue_id, Ticket.statut == 'traite', Ticket.heure_passage != None))
    avg_seconds = q_avg.scalar_one()
    avg_wait = float(avg_seconds) if avg_seconds is not None else None
    
    return {
        "queue_id": queue_id, 
        "total": total, 
        "waiting": waiting, 
        "called": called, 
        "done": done, 
        "absent": absent,
        "skipped": skipped,
        "avg_wait_seconds": avg_wait
    }
