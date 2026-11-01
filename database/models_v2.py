from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, JSON, func

class Base(DeclarativeBase): pass
class Workflow(Base):
    __tablename__="workflows"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int|None]=mapped_column(Integer,nullable=True)
    user_request: Mapped[str]=mapped_column(Text)
    status: Mapped[str]=mapped_column(String(30),default="pending")
    plan: Mapped[dict|None]=mapped_column(JSON,nullable=True)
    created_at: Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now())
class WorkflowTask(Base):
    __tablename__="workflow_tasks"
    id: Mapped[int]=mapped_column(primary_key=True)
    workflow_id: Mapped[int]=mapped_column(ForeignKey("workflows.id",ondelete="CASCADE"),index=True)
    task_id: Mapped[int]=mapped_column(Integer)
    agent: Mapped[str]=mapped_column(String(80))
    status: Mapped[str]=mapped_column(String(30),default="pending")
    dependencies: Mapped[list]=mapped_column(JSON,default=list)
    result: Mapped[dict|None]=mapped_column(JSON,nullable=True)

class User(Base):
    __tablename__="users"
    user_id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100))
    email: Mapped[str]=mapped_column(String(255),unique=True,index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    created_at: Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now())
