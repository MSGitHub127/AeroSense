"""Consultation service coordinating AI-driven QA, vision analysis, and dossier exports."""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.exceptions import ProfileNotFoundError, SecurityValidationError
from app.llm.provider import LLMProvider
from app.models import FamilyProfileRecord
from app.security import decrypt_pii, detect_prompt_injection, redact_pii


class ConsultationService:
    """Enterprise service orchestrating grounded conversational intelligence and multimodal vision."""

    @staticmethod
    def answer_consultation_question(
        profile_id: str,
        question: str,
        db: Session,
        llm: LLMProvider,
    ) -> tuple[str, str]:
        """Validate inquiry, fetch profile grounding context, and generate AI response.

        Args:
            profile_id: UUID of family profile.
            question: Inbound user question.
            db: Database session.
            llm: LLM provider instance.

        Returns:
            tuple[str, str]: (sanitized_question, ai_answer).

        Raises:
            SecurityValidationError: If prompt injection patterns are identified.
            ProfileNotFoundError: If target profile does not exist.
        """
        if detect_prompt_injection(question):
            raise SecurityValidationError("Security violation: Inbound inquiry contains forbidden prompt injection patterns.")

        clean_question = redact_pii(question)

        record = db.query(FamilyProfileRecord).filter(FamilyProfileRecord.id == profile_id).first()
        if not record:
            raise ProfileNotFoundError(f"Profile '{profile_id}' not found.")

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

        return clean_question, answer

    @staticmethod
    def get_export_dossier_markdown(profile_id: str, db: Session) -> tuple[str, str]:
        """Fetch saved Markdown air dossier for download.

        Args:
            profile_id: UUID of family profile.
            db: Database session.

        Returns:
            tuple[str, str]: (filename, markdown_content).

        Raises:
            ProfileNotFoundError: If target profile does not exist.
        """
        record = db.query(FamilyProfileRecord).filter(FamilyProfileRecord.id == profile_id).first()
        if not record:
            raise ProfileNotFoundError(f"Profile '{profile_id}' not found.")

        decrypted_str = decrypt_pii(record.encrypted_details)
        details = json.loads(decrypted_str)
        action_plan_md = details.get("action_plan_markdown", "# Family Air Quality Action Plan\n\nNo details available.")
        filename = f"aerosense_action_plan_{record.household_name.replace(' ', '_').lower()}.md"

        return filename, action_plan_md

    @staticmethod
    def analyze_image_stream(
        image_bytes: bytes,
        filename: str,
        content_type: str,
        prompt: str | None,
        llm: LLMProvider,
    ) -> str:
        """Process image upload and run multimodal smog/filter visual analysis.

        Args:
            image_bytes: Binary image data.
            filename: Original uploaded filename.
            content_type: MIME type of the uploaded file.
            prompt: Optional guiding context prompt.
            llm: LLM provider instance.

        Returns:
            str: Grounded visual inspection analysis.
        """
        user_prompt = prompt or "Analyze this image for urban smog severity, atmospheric visibility, or air filter status."
        return llm.analyze_smog_image(
            image_bytes=image_bytes,
            mime_type=content_type,
            prompt=user_prompt,
        )
