import asyncio

from base import Base
from database import engine
import models # Ensure models are registered with Base


async def init() -> None:
    """
    Create all database tables based on the SQLAlchemy models.

    Uses the DATABASE_URL from config/settings (env variable override on Vercel/locally).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed Admin User
    from database import AsyncSessionLocal
    import crud
    
    async with AsyncSessionLocal() as session:
        admin_email = "admin@admin.com"
        admin = await crud.get_user_by_email(session, admin_email)
        if not admin:
            print(f"Creating default admin user: {admin_email}")
            await crud.create_user(
                session, 
                nom="Super Admin", 
                email=admin_email, 
                password="adminpassword", 
                role="admin"
            )
        else:
            print(f"Admin user {admin_email} already exists.")

    # Seed Default Queues (Services)
    async with AsyncSessionLocal() as session:
        default_queues = [
            {"nom": "Accueil / Renmseignements", "institution": "Hopital General", "max_capacity": 100},
            {"nom": "Caisse", "institution": "Hopital General", "max_capacity": 50},
            {"nom": "Consultation Générale", "institution": "Hopital General", "max_capacity": 30},
            {"nom": "Pharmacie", "institution": "Hopital General", "max_capacity": 100},
            {"nom": "Urgence", "institution": "Hopital General", "max_capacity": 10}
        ]
        
        for q_data in default_queues:
            # Check if queue exists by name
            from sqlalchemy import select
            from models import Queue
            import crud
            # Simple check
            q_exist = await session.execute(select(Queue).where(Queue.nom == q_data["nom"]))
            if not q_exist.scalars().first():
                print(f"Creating default queue: {q_data['nom']}")
                await crud.create_queue(
                    session,
                    nom=q_data["nom"],
                    institution=q_data["institution"],
                    max_capacity=q_data["max_capacity"]
                )
            else:
                print(f"Queue {q_data['nom']} already exists.")


if __name__ == "__main__":
    asyncio.run(init())



