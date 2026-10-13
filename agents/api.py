"""
FastAPI REST API Server for Wells Score Calculator.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from wells import calculate_dvt, calculate_pe, calculate_geneva, list_dvt_criteria, list_pe_criteria, list_geneva_criteria

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Wells Score Calculator API",
    description="Enterprise Distributed Component Platform (Clinical & Biomedical AI)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "wells-score-calculator", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}

# Scoring endpoints are stateless; no identifiers or clinical inputs are persisted.
@app.get("/api/score/criteria")
def score_criteria():
    return {
        "dvt": list_dvt_criteria(),
        "pe": list_pe_criteria(),
        "geneva": list_geneva_criteria(),
    }


@app.post("/api/score/{score_type}")
def score_patient(score_type: str, criteria: Dict[str, Any]):
    calculators = {"dvt": calculate_dvt, "pe": calculate_pe, "geneva": calculate_geneva}
    if score_type not in calculators:
        raise HTTPException(status_code=404, detail="Unknown score type")
    try:
        return calculators[score_type](criteria)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
