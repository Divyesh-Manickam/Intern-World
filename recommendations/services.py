from decimal import Decimal
from opportunities.models import Opportunity


def calculate_opportunity_match(student_profile, opportunity):
    """
    Computes a weighted compatibility score (0-100%) between a StudentProfile and an Opportunity.
    Returns a dictionary containing the total score and detailed evaluation breakdown.
    """
    if not student_profile or not opportunity:
        return {'score': 0, 'breakdown': {}, 'reasons': []}

    score = 0
    reasons = []

    # 1. Skills Matching (Weight: 40 points)
    student_skills = set(
        s.strip().lower()
        for s in (student_profile.skills or '').split(',')
        if s.strip()
    )
    # Also extract skills mentioned in resume if available
    if student_profile.resume_extracted_text:
        resume_lower = student_profile.resume_extracted_text.lower()
    else:
        resume_lower = ""

    req_skills = [
        s.strip().lower()
        for s in (opportunity.required_skills or '').split(',')
        if s.strip()
    ]
    
    matched_skills = []
    missing_skills = []

    if req_skills:
        for s in req_skills:
            if s in student_skills or (resume_lower and s in resume_lower):
                matched_skills.append(s)
            else:
                missing_skills.append(s)

        skill_ratio = len(matched_skills) / len(req_skills)
        skill_points = int(skill_ratio * 40)
        score += skill_points
        reasons.append(f"Skills: {len(matched_skills)} of {len(req_skills)} required skills matched")
    else:
        score += 35
        reasons.append("Skills: No strict skill restrictions specified")

    # 2. Department Matching (Weight: 15 points)
    dept_match = False
    eligible_depts = (opportunity.eligible_department or '').lower()
    if 'all' in eligible_depts or 'any' in eligible_depts or not eligible_depts:
        dept_match = True
        score += 15
        reasons.append("Department: Open to all academic departments")
    elif student_profile.department and student_profile.department.lower() in eligible_depts:
        dept_match = True
        score += 15
        reasons.append(f"Department: Your department ({student_profile.department}) is eligible")
    else:
        reasons.append(f"Department: Targeted at {opportunity.eligible_department}")

    # 3. Degree Matching (Weight: 15 points)
    degree_match = False
    eligible_degrees = (opportunity.eligible_degree or '').lower()
    if 'all' in eligible_degrees or 'any' in eligible_degrees or not eligible_degrees:
        degree_match = True
        score += 15
        reasons.append("Degree: Open to all degree streams")
    elif student_profile.degree and student_profile.degree.lower() in eligible_degrees:
        degree_match = True
        score += 15
        reasons.append(f"Degree: Your degree ({student_profile.degree}) meets criteria")
    else:
        reasons.append(f"Degree: Targeted at {opportunity.eligible_degree}")

    # 4. CGPA Eligibility (Weight: 15 points)
    cgpa_eligible = False
    min_cgpa = opportunity.min_cgpa or Decimal('0.0')
    student_cgpa = student_profile.cgpa or Decimal('0.0')

    if min_cgpa <= Decimal('0.0'):
        cgpa_eligible = True
        score += 15
        reasons.append("CGPA: No minimum cutoff required")
    elif student_cgpa >= min_cgpa:
        cgpa_eligible = True
        score += 15
        reasons.append(f"CGPA: Your CGPA ({student_cgpa}) meets minimum cutoff ({min_cgpa})")
    elif student_cgpa >= (min_cgpa - Decimal('0.5')):
        score += 5
        reasons.append(f"CGPA: Close to cutoff ({min_cgpa})")
    else:
        reasons.append(f"CGPA: Minimum cutoff is {min_cgpa}")

    # 5. Graduation Year Matching (Weight: 5 points)
    grad_match = False
    if not opportunity.graduation_year or opportunity.graduation_year == student_profile.graduation_year:
        grad_match = True
        score += 5
        if opportunity.graduation_year:
            reasons.append(f"Batch Year: Matches graduating batch {opportunity.graduation_year}")
    else:
        reasons.append(f"Batch Year: Intended for {opportunity.graduation_year} batch")

    # 6. Location & Work Mode Matching (Weight: 5 points)
    loc_match = False
    if opportunity.work_mode == Opportunity.WorkMode.REMOTE:
        loc_match = True
        score += 5
        reasons.append("Location: 100% Remote Opportunity")
    elif student_profile.preferred_location:
        pref_locs = [l.strip().lower() for l in student_profile.preferred_location.split(',')]
        opp_loc = (opportunity.location or '').lower()
        if any(pref in opp_loc for pref in pref_locs):
            loc_match = True
            score += 5
            reasons.append(f"Location: Matches your preferred city ({opportunity.location})")
    else:
        score += 2

    # 7. Job Role & Domain Matching (Weight: 5 points)
    role_match = False
    if student_profile.preferred_role:
        pref_roles = [r.strip().lower() for r in student_profile.preferred_role.split(',')]
        opp_title = (opportunity.title or '').lower()
        opp_role = (opportunity.job_role or '').lower()
        if any(pr in opp_title or pr in opp_role for pr in pref_roles):
            role_match = True
            score += 5
            reasons.append("Job Role: Matches your career interest")
    else:
        score += 2

    # Clamp total score between 0 and 100
    final_score = min(max(score, 0), 100)

    breakdown = {
        'score': final_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'matched_skills_count': len(matched_skills),
        'total_skills_count': len(req_skills),
        'dept_match': dept_match,
        'degree_match': degree_match,
        'cgpa_eligible': cgpa_eligible,
        'grad_match': grad_match,
        'loc_match': loc_match,
        'role_match': role_match,
        'reasons': reasons,
    }

    return breakdown


def get_recommendations_for_student(user, limit=10, min_score=20):
    """
    Returns a sorted list of approved and active opportunities scored for the given student user.
    Each item is a tuple: (opportunity, breakdown_dict).
    """
    if not hasattr(user, 'student_profile'):
        return []

    profile = user.student_profile
    approved_opportunities = Opportunity.objects.filter(
        status=Opportunity.Status.APPROVED
    ).select_related('company', 'recruiter')

    scored_list = []
    for opp in approved_opportunities:
        if opp.is_expired:
            continue
        breakdown = calculate_opportunity_match(profile, opp)
        if breakdown['score'] >= min_score:
            scored_list.append((opp, breakdown))

    # Sort descending by score, then by deadline
    scored_list.sort(key=lambda item: item[1]['score'], reverse=True)

    return scored_list[:limit]
