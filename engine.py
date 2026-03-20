# engine.py

# Official 2026/2027 Grade Point Values
GRADE_POINTS = {
    'A': 6, 'B': 5, 'C': 4, 'D': 3, 'E': 2, 'O': 1, 'F': 0
}

def get_weight(subject_grades, course_reqs, o_level_data, gender):
    """
    Calculates weight for a single course.
    subject_grades: dict { 'Physics': 'A', 'Math': 'B', ... }
    course_reqs: dict from CSV row
    o_level_data: dict { 'D': 5, 'C': 3, 'P': 2 }
    """
    
    # 1. Eligibility Check: Does the user have the required Essential Subjects?
    # For now, we assume the user picks their grades manually.
    # We will expand this logic when the CSV data is more complex.
    
    e1_grade = subject_grades.get(course_reqs['Essential_1'], 'F')
    e2_grade = subject_grades.get(course_reqs['Essential_2'], 'F')
    rel_grade = subject_grades.get(course_reqs['Relevant'], 'F')
    
    # 2. A-Level Score (E1*3 + E2*3 + Rel*2)
    a_level_score = (GRADE_POINTS.get(e1_grade, 0) * 3) + \
                    (GRADE_POINTS.get(e2_grade, 0) * 3) + \
                    (GRADE_POINTS.get(rel_grade, 0) * 2)
    
    # 3. Desirable Score (GP and Sub-Math/ICT are usually 1pt each)
    # Passed status passed in via subject_grades as 'GP': True
    desirable_score = (1 if subject_grades.get('GP') else 0) + \
                      (1 if subject_grades.get('Sub') else 0)
    
    # 4. O-Level Score (D=0.3, C=0.2, P=0.1)
    o_level_score = (o_level_data['D'] * 0.3) + \
                    (o_level_data['C'] * 0.2) + \
                    (o_level_data['P'] * 0.1)
    
    # 5. Gender Bonus
    gender_bonus = 1.5 if gender == "Female" else 0
    
    total = a_level_score + desirable_score + o_level_score + gender_bonus
    return round(total, 2)
