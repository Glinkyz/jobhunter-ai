from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.db.database import get_db
from services.db.models import Application, User, Profile, Job, ApplicationStatusEnum
from services.crm_service.kanban import CRMKanbanManager
from services.api.schemas import (
    ApplicationCreate,
    ApplicationStatusUpdate,
    ApplicationResponse,
    KanbanBoardResponse
)

router = APIRouter(prefix="/crm", tags=["CRM Candidaturas (ATS Personal)"])


@router.get("/kanban", response_model=KanbanBoardResponse)
def get_kanban_board(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Application)
    if user_id:
        query = query.filter(Application.user_id == user_id)
    applications = query.order_by(Application.updated_at.desc()).all()

    organized = CRMKanbanManager.organize_into_kanban(applications)
    
    # Map to schema responses
    result_columns = {}
    for col_name, apps in organized.items():
        result_columns[col_name] = [ApplicationResponse.model_validate(app) for app in apps]

    return KanbanBoardResponse(
        columns=result_columns,
        total_count=len(applications)
    )


@router.get("/applications", response_model=List[ApplicationResponse])
def list_applications(user_id: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Application)
    if user_id:
        query = query.filter(Application.user_id == user_id)
    if status:
        query = query.filter(Application.status == status.upper())
    return query.order_by(Application.updated_at.desc()).all()


@router.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Oferta de empleo no encontrada")

    init_event = CRMKanbanManager.create_timeline_event(
        event_type="APPLICATION_CREATED",
        note=f"Candidatura añadida a la etapa {payload.status.upper()}",
        to_status=payload.status.upper()
    )

    app = Application(
        user_id=payload.user_id,
        profile_id=payload.profile_id,
        job_id=payload.job_id,
        status=payload.status.upper(),
        stage_notes=payload.stage_notes,
        timeline_events=[init_event],
        custom_cv_path=payload.custom_cv_path,
        cover_letter=payload.cover_letter
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.patch("/applications/{app_id}/status", response_model=ApplicationResponse)
def update_application_status(app_id: str, payload: ApplicationStatusUpdate, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Candidatura no encontrada")

    old_status = app.status
    new_status = payload.status.upper()

    event = CRMKanbanManager.create_timeline_event(
        event_type="STATUS_CHANGED",
        note=payload.note or f"Transición de {old_status} a {new_status}",
        from_status=old_status,
        to_status=new_status
    )

    app.status = new_status
    if payload.note:
        app.stage_notes = payload.note
    if payload.next_action_date:
        app.next_action_date = payload.next_action_date

    timeline = list(app.timeline_events or [])
    timeline.append(event)
    app.timeline_events = timeline

    db.commit()
    db.refresh(app)
    return app


@router.delete("/applications/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(app_id: str, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Candidatura no encontrada en el tablero")

    db.delete(app)
    db.commit()
    return None


@router.get("/stats")
def get_crm_stats(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Application)
    if user_id:
        query = query.filter(Application.user_id == user_id)
    applications = query.all()
    return CRMKanbanManager.calculate_stats(applications)
