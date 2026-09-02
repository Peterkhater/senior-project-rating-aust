from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Avg, Count
from .models import Track, Project, TeamMember, ProjectEvaluation

# Create your views here.
def home(request):
    tracks = Track.objects.all()
    return render(request, 'core/home.html', {'tracks': tracks})

def track_project_list(request, track_id):
    track = Track.objects.get(id=track_id) 
    projects = Project.objects.filter(track=track).order_by('title')
    return render(request, 'core/track_project_list.html', {'track': track , 'projects': projects})


def project_detail(request, project_code):
    project = get_object_or_404(Project, project_code=project_code)
    evaluations = project.evaluations.all()
    
    # Calculate average scores
    if evaluations.exists():
        avg_scores = {
            'problem_innovation': evaluations.aggregate(Avg('problem_innovation'))['problem_innovation__avg'] or 0,
            'technical_excellence': evaluations.aggregate(Avg('technical_excellence'))['technical_excellence__avg'] or 0,
            'functionality_demo': evaluations.aggregate(Avg('functionality_demo'))['functionality_demo__avg'] or 0,
            'presentation_team': evaluations.aggregate(Avg('presentation_team'))['presentation_team__avg'] or 0,
            'industry_impact': evaluations.aggregate(Avg('industry_impact'))['industry_impact__avg'] or 0,
        }
        # Calculate weighted average
        avg_total = (
            avg_scores['problem_innovation'] * 4 +  # 20%
            avg_scores['technical_excellence'] * 5 +  # 25%
            avg_scores['functionality_demo'] * 4 +  # 20%
            avg_scores['presentation_team'] * 3 +  # 15%
            avg_scores['industry_impact'] * 4  # 20%
        )
    else:
        avg_scores = None
        avg_total = 0
    
    context = {
        'project': project,
        'evaluations': evaluations,
        'avg_scores': avg_scores,
        'avg_total': avg_total,
        'total_evaluations': evaluations.count(),
    }
    
    return render(request, 'core/project_detail.html', context)

def submit_evaluation(request, project_code):
    if request.method == 'POST':
        project = get_object_or_404(Project, project_code=project_code)
        
        evaluation = ProjectEvaluation.objects.create(
            project=project,
            evaluator_name=request.POST.get('evaluator_name'),
            evaluator_email=request.POST.get('evaluator_email'),
            evaluator_organization=request.POST.get('evaluator_organization', ''),
            problem_innovation=int(request.POST.get('problem_innovation', 3)),
            technical_excellence=int(request.POST.get('technical_excellence', 3)),
            functionality_demo=int(request.POST.get('functionality_demo', 3)),
            presentation_team=int(request.POST.get('presentation_team', 3)),
            industry_impact=int(request.POST.get('industry_impact', 3)),
            comments=request.POST.get('comments', ''),
        )
        
        messages.success(request, f'Thank you {evaluation.evaluator_name}! Your evaluation has been submitted.')
        return redirect('project_detail', project_code=project.project_code)
    
    return redirect('project_detail', project_code=project_code)