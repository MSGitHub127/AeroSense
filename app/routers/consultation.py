"""Conversational AI consultation, Markdown dossier export, and multimodal vision analysis."""
from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.deps import get_db_session, get_llm
from app.llm.provider import LLMProvider
from app.models import FamilyProfileRecord
from app.security import decrypt_pii, detect_prompt_injection, redact_pii

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

    Raises:
        HTTPException: If prompt injection is detected or profile is missing.
    """
    if detect_prompt_injection(payload.question):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security violation: Inbound inquiry contains forbidden prompt injection patterns.",
        )

    clean_question = redact_pii(payload.question)

    record = db.query(FamilyProfileRecord).filter(FamilyProfileRecord.id == profile_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile '{profile_id}' not found.",
        )

    decrypted_str = decrypt_pii(record.encrypted_details)
    details = json.loads(decrypted_str)

    household_context = (
        f"Household: {record.household_name} in {record.location_city}\n"
        f"Dwelling: {record.home_type}, Cooking Fuel: {details.get('cooking_fuel')}, "
        f"Commute: {details.get('commute_mode')}\n"
        f"Estimated Baseline AQI: {record.estimated_baseline_aqi}\n"
        f"Vulnerability Tier: {details.get('vulnerability_tier')}\n"
        f"Vulnerable Members: {', '.join(details.get('vulnerable_members', []))}\n"
    )

    answer = llm.generate_air_consultation(
        question=clean_question,
        household_context=household_context,
    )

    return AirConsultationResponse(
        profile_id=profile_id,
        question=clean_question,
        answer=answer,
    )


@router.get("/advisory/{profile_id}/dossier", summary="Export Family Air Action Plan in Markdown format")
def export_action_plan_dossier(
    profile_id: str,
    db: Annotated[Session, Depends(get_db_session)],
) -> Response:
    """Export complete synthesized Family Air Action Plan as a downloadable Markdown document.

    Args:
        profile_id: Profile UUID.
        db: Database session.

    Returns:
        Response: Plaintext Markdown with download headers.

    Raises:
        HTTPException: If profile is not found.
    """
    record = db.query(FamilyProfileRecord).filter(FamilyProfileRecord.id == profile_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile '{profile_id}' not found.",
        )

    decrypted_str = decrypt_pii(record.encrypted_details)
    details = json.loads(decrypted_str)
    markdown_content = details.get("action_plan_markdown", "# AeroSense Action Plan")

    filename = f"AeroSense_Plan_{record.household_name.replace(' ', '_')}.md"
    return Response(
        content=markdown_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/vision/inspect", response_model=VisionInspectionResponse, summary="Inspect outdoor haze or air filter visually")
async def inspect_smog_image(
    file: Annotated[UploadFile, File(description="Outdoor skyline or air filter photograph")],
    llm: Annotated[LLMProvider, Depends(get_llm)],
    prompt: Annotated[
        str,
        Form(description="Directive for image analysis"),
    ] = "Inspect the atmospheric haze level, estimated visibility, and safety precautions.",
) -> VisionInspectionResponse:
    """Analyze uploaded photo of outdoor winter smog or home filter conditions using Vision AI.

    Args:
        file: Uploaded image file.
        prompt: Directive instructions.
        llm: LLM provider instance.

    Returns:
        VisionInspectionResponse: Grounded visual inspection assessment.

    Raises:
        HTTPException: If file type is unsupported or file size exceeds 5MB.
    """
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type '{file.content_type}'. Must be JPEG, PNG, or WebP.",
        )

    image_bytes = await file.read()
    if len(image_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image size exceeds 5MB limit.",
        )

    analysis = llm.analyze_smog_image(
        image_bytes=image_bytes,
        mime_type=file.content_type or "image/jpeg",
        prompt=prompt,
    )

    return VisionInspectionResponse(
        filename=file.filename or "upload.jpg",
        analysis=analysis,
    )
