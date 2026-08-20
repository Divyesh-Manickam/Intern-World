import os
from django.core.exceptions import ValidationError
from django.conf import settings
import pypdf
import io


def validate_pdf_resume(file_obj):
    """
    Validates uploaded resume file:
    - Extension must be .pdf
    - Max size 5MB
    - MIME validation / readable PDF check
    """
    if not file_obj:
        return True

    # 1. Extension check
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError("Only PDF files (.pdf) are allowed for resumes.")

    # 2. File size check (5MB max)
    max_size = getattr(settings, 'MAX_RESUME_SIZE_BYTES', 5 * 1024 * 1024)
    if file_obj.size > max_size:
        raise ValidationError(f"Resume file size cannot exceed {max_size // (1024 * 1024)} MB.")

    # 3. Content / Header check
    try:
        # Check PDF header
        file_obj.seek(0)
        header = file_obj.read(5)
        file_obj.seek(0)
        if not header.startswith(b'%PDF-'):
            raise ValidationError("Invalid PDF format. The uploaded file is not a valid PDF.")
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError("Could not validate the uploaded PDF resume.")

    return True


def extract_text_from_pdf(file_obj):
    """
    Extracts readable text from a PDF resume using pypdf.
    Returns cleaned text string.
    """
    text = ""
    try:
        if hasattr(file_obj, 'read'):
            file_obj.seek(0)
            reader = pypdf.PdfReader(file_obj)
        elif hasattr(file_obj, 'path') and os.path.exists(file_obj.path):
            reader = pypdf.PdfReader(file_obj.path)
        else:
            return ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception:
        return ""
    return text.strip()


def calculate_profile_completion(profile):
    """
    Calculates profile completion percentage (0-100%) based on weighted profile fields.
    """
    if not profile:
        return 0

    points = 0
    total = 100

    # Basic Info & Education (30 pts)
    if profile.college:
        points += 5
    if profile.degree:
        points += 5
    if profile.department:
        points += 5
    if profile.graduation_year:
        points += 5
    if profile.cgpa and profile.cgpa > 0:
        points += 5
    if profile.bio:
        points += 5

    # Skills & Preferences (25 pts)
    if profile.skills:
        points += 15
    if profile.preferred_role or profile.preferred_location:
        points += 10

    # Resume (25 pts)
    if profile.resume:
        points += 25

    # Projects / Experience / Socials (20 pts)
    if profile.projects.exists():
        points += 10
    if profile.certifications.exists() or profile.experiences.exists():
        points += 5
    if profile.github_url or profile.linkedin_url or profile.portfolio_url:
        points += 5

    return min(points, total)
