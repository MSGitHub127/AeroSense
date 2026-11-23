"""Conversational AI consultation, Markdown dossier export, and multimodal vision analysis router."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.deps import get_db_session, get_llm
from app.llm.provider import LLMProvider
from app.services.consultation_service import ConsultationService

router = APIRouter(prefix="/api", tags=["Consultation & Vision"])


class AirConsultationRequest(BaseModel):
    """User consultation inquiry payload."""

    question: str = Field(
        ...,
        min_length=2,
        max_length=1000,
        description="Air quality, health concern, or routine adaptation inquiry",
    )


class AirConsultationResponse(BaseModel):
    """Conversational guidance response."""

    profile_id: str = Field(..., description="Target profile ID")
    question: str = Field(..., description="Sanitized question asked")
    answer: str = Field(..., description="Grounded expert guidance from AeroSense")


class VisionInspectionResponse(BaseModel):
    """Visual smog assessment response."""

    filename: str = Field(..., description="Uploaded image filename")
    analysis: str = Field(..., description="Visual smog, haze, or filter condition analysis")


@router.post("/advisory/{profile_id}/ask", response_model=AirConsultationResponse, summary="Ask AeroSense conversational air quality assistant")
def ask_air_consultation(
    profile_id: str,
    payload: AirConsultationRequest,
    db: Annotated[Session, Depends(get_db_session)],
    llm: Annotated[LLMProvider, Depends(get_llm)],
) -> AirConsultationResponse:
    """Consult the AI assistant with specific household air questions grounded in your profile.

    Args:
        profile_id: Target profile UUID.
        payload: Inbound question.
        db: Database session.
        llm: LLM provider instance.

    Returns:
        AirConsultationResponse: Actionable guidance.
    """
    clean_question, answer = ConsultationService.answer_consultation_question(
        profile_id=profile_id,
        question=payload.question,
        db=db,
        llm=llm,
    )

    return AirConsultationResponse(
        profile_id=profile_id,
        question=clean_question,
        answer=answer,
    )


@router.get("/advisory/{profile_id}/dossier", summary="Export complete Family Air Action Plan as Markdown")
@router.get("/advisory/{profile_id}/export", summary="Export complete Family Air Action Plan as Markdown (alias)")
def export_dossier(
    profile_id: str,
    db: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Download the customized Family Air Quality Action Plan as a Markdown dossier.

    Args:
        profile_id: Target profile UUID.
        db: Database session.

    Returns:
        Response: Markdown file stream with download headers.
    """
    filename, action_plan_md = ConsultationService.get_export_dossier_markdown(profile_id, db)

    return Response(
        content=action_plan_md,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/vision/inspect", response_model=VisionInspectionResponse, summary="Analyze smog severity or filter condition via image")
async def inspect_smog_image(
    file: Annotated[UploadFile, File(description="Smog landscape or filter image")],
    prompt: Annotated[str | None, Form(description="Optional custom query for visual analysis")] = None,
    llm: Annotated[LLMProvider, Depends(get_llm)] = None,
) -> VisionInspectionResponse:
    """Inspect an image using multimodal vision to evaluate outdoor haze or indoor air purifier filter condition.

    Args:
        file: Uploaded image file (JPEG, PNG, WebP).
        prompt: Optional query.
        llm: LLM provider with multimodal vision capability.

    Returns:
        VisionInspectionResponse: Grounded visual evaluation.

    Raises:
        HTTPException: If file format or size is invalid.
    """
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image type '{file.content_type}'. Must be JPEG, PNG, or WebP.",
        )

    image_bytes = await file.read()
    if len(image_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size exceeds 5MB limit.",
        )

    analysis = ConsultationService.analyze_image_stream(
        image_bytes=image_bytes,
        filename=file.filename or "image.jpg",
        content_type=file.content_type,
        prompt=prompt,
        llm=llm,
    )

    return VisionInspectionResponse(
        filename=file.filename or "image.jpg",
        analysis=analysis,
    )
