from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas


def home(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        subject_names = request.POST.getlist('subject_name')
        subject_marks = request.POST.getlist('subject_marks')

        subjects = []
        total = 0

        for name, mark in zip(subject_names, subject_marks):
            if name.strip() != '' and mark.strip() != '':
                mark = int(mark)
                subjects.append({
                    'name': name,
                    'marks': mark
                })
                total += mark

        if len(subjects) > 0:
            avg = total / len(subjects)
        else:
            avg = 0

        max_marks = len(subjects) * 100
        if max_marks > 0:
            percentage = (total / max_marks) * 100
        else:
            percentage = 0

        if avg >= 80:
            grade = "A"
        elif avg >= 60:
            grade = "B"
        elif avg >= 40:
            grade = "C"
        else:
            grade = "F"

        if avg >= 40:
            result = "PASS"
        else:
            result = "FAIL"

        if subjects:
            weak_subject_data = min(subjects, key=lambda x: x['marks'])
            weak_subject = weak_subject_data['name']
            suggestion = f"You should improve {weak_subject}"
        else:
            weak_subject = "None"
            suggestion = "No subjects entered"

        request.session['student_name'] = student_name
        request.session['subjects'] = subjects
        request.session['total'] = total
        request.session['avg'] = avg
        request.session['percentage'] = percentage
        request.session['result'] = result
        request.session['grade'] = grade
        request.session['weak_subject'] = weak_subject
        request.session['suggestion'] = suggestion

        context = {
            'student_name': student_name,
            'subjects': subjects,
            'total': total,
            'avg': avg,
            'percentage': percentage,
            'result': result,
            'grade': grade,
            'weak_subject': weak_subject,
            'suggestion': suggestion,
        }

        return render(request, 'result.html', context)

    return render(request, 'form.html')


def download_pdf(request):
    student_name = request.session.get('student_name', 'Student')
    subjects = request.session.get('subjects', [])
    total = request.session.get('total', 0)
    avg = request.session.get('avg', 0)
    percentage = request.session.get('percentage', 0)
    result = request.session.get('result', 'N/A')
    grade = request.session.get('grade', 'N/A')
    weak_subject = request.session.get('weak_subject', 'N/A')
    suggestion = request.session.get('suggestion', 'N/A')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student_name}_report.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, 800, "Student Performance Report")

    p.setFont("Helvetica", 12)
    p.drawString(50, 760, f"Student Name: {student_name}")

    y = 720
    p.drawString(50, y, "Subjects and Marks:")
    y -= 25

    for subject in subjects:
        p.drawString(70, y, f"{subject['name']} : {subject['marks']}")
        y -= 20

    y -= 10
    p.drawString(50, y, f"Total: {total}")
    y -= 20
    p.drawString(50, y, f"Average: {avg}")
    y -= 20
    p.drawString(50, y, f"Percentage: {percentage}%")
    y -= 20
    p.drawString(50, y, f"Result: {result}")
    y -= 20
    p.drawString(50, y, f"Grade: {grade}")
    y -= 20
    p.drawString(50, y, f"Weak Subject: {weak_subject}")
    y -= 20
    p.drawString(50, y, f"Suggestion: {suggestion}")

    p.showPage()
    p.save()

    return response