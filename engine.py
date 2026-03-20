# engine.py (Updated)

GRADE_POINTS = {'A': 6, 'B': 5, 'C': 4, 'D': 3, 'E': 2, 'O': 1, 'F': 0}

def get_weight(subject_grades, course_reqs, o_level_data, gender):
    # (The math remains the same as our previous version)
    e1_grade = subject_grades.get(course_reqs['Essential_1'], 'F')
    e2_grade = subject_grades.get(course_reqs['Essential_2'], 'F')
    rel_grade = subject_grades.get(course_reqs['Relevant'], 'F')
    
    a_level_score = (GRADE_POINTS.get(e1_grade, 0) * 3) + \
                    (GRADE_POINTS.get(e2_grade, 0) * 3) + \
                    (GRADE_POINTS.get(rel_grade, 0) * 2)
    
    desirable_score = (1 if subject_grades.get('GP') else 0) + \
                      (1 if subject_grades.get('Sub') else 0)
    
    o_level_score = (o_level_data['D'] * 0.3) + \
                    (o_level_data['C'] * 0.2) + \
                    (o_level_data['P'] * 0.1)
    
    gender_bonus = 1.5 if gender == "Female" else 0
    return round(a_level_score + desirable_score + o_level_score + gender_bonus, 2)

def get_color_status(user_weight, cut_off):
    """Determines eligibility status based on historical cut-offs."""
    
    # If there is no cut-off data (0), we can't give a status
    if cut_off == 0:
        return "No Data", "#6c757d" # Grey color
        
    if user_weight >= cut_off + 1.0:
        return "Safe", "#28a745" # Green
    elif user_weight >= cut_off - 0.5:
        return "Borderline", "#ffc107" # Yellow
    else:
        return "Risky", "#dc3545" # Red
