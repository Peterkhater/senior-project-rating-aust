# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Avg, Count
from .models import Track, Project, TeamMember, ProjectEvaluation
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
    tracks = Track.objects.all()
    return render(request, 'core/home.html', {'tracks': tracks})

@login_required
def track_project_list(request, track_id):
    track = Track.objects.get(id=track_id) 
    projects = Project.objects.filter(track=track).order_by('title')
    return render(request, 'core/track_project_list.html', {'track': track , 'projects': projects})

@login_required
def project_detail(request, project_code):
    project = get_object_or_404(Project, project_code=project_code)
    evaluations = project.evaluations.all()
    
    # Check if current user already evaluated this project
    has_evaluated = ProjectEvaluation.objects.filter(
        project=project, 
        evaluator=request.user
    ).exists()
    
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
        'has_evaluated': has_evaluated,
    }
    
    return render(request, 'core/project_detail.html', context)

@login_required
def submit_evaluation(request, project_code):
    if request.method == 'POST':
        project = get_object_or_404(Project, project_code=project_code)
        
        # Check if user already evaluated this project
        if ProjectEvaluation.objects.filter(project=project, evaluator=request.user).exists():
            messages.warning(request, 'You have already evaluated this project.')
            return redirect('project_detail', project_code=project.project_code)
        
        # Create evaluation with the user
        evaluation = ProjectEvaluation.objects.create(
            project=project,
            evaluator=request.user,
            evaluator_organization=request.POST.get('evaluator_organization', ''),
            problem_innovation=int(request.POST.get('problem_innovation', 3)),
            technical_excellence=int(request.POST.get('technical_excellence', 3)),
            functionality_demo=int(request.POST.get('functionality_demo', 3)),
            presentation_team=int(request.POST.get('presentation_team', 3)),
            industry_impact=int(request.POST.get('industry_impact', 3)),
            comments=request.POST.get('comments', ''),
        )
        
        user_name = request.user.get_full_name() or request.user.username
        messages.success(request, f'Thank you {user_name}! Your evaluation has been submitted.')
        return redirect('project_detail', project_code=project.project_code)
    
    return redirect('project_detail', project_code=project_code)

@staff_member_required
def project_evaluations_admin(request, project_code):
    """Admin only - view all evaluations for a project"""
    project = get_object_or_404(Project, project_code=project_code)
    evaluations = project.evaluations.all().order_by('-created_at')
    
    context = {
        'project': project,
        'evaluations': evaluations,
        'total_evaluations': evaluations.count(),
    }
    
    return render(request, 'core/project_evaluations_admin.html', context)




@staff_member_required
def track_rankings(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    projects = Project.objects.filter(track=track)
    
    # Calculate scores for each project
    project_scores = []
    for project in projects:
        evaluations = project.evaluations.all()
        
        if evaluations.exists():
            avg_scores = {
                'problem_innovation': evaluations.aggregate(Avg('problem_innovation'))['problem_innovation__avg'] or 0,
                'technical_excellence': evaluations.aggregate(Avg('technical_excellence'))['technical_excellence__avg'] or 0,
                'functionality_demo': evaluations.aggregate(Avg('functionality_demo'))['functionality_demo__avg'] or 0,
                'presentation_team': evaluations.aggregate(Avg('presentation_team'))['presentation_team__avg'] or 0,
                'industry_impact': evaluations.aggregate(Avg('industry_impact'))['industry_impact__avg'] or 0,
            }
            avg_total = (
                avg_scores['problem_innovation'] * 4 +
                avg_scores['technical_excellence'] * 5 +
                avg_scores['functionality_demo'] * 4 +
                avg_scores['presentation_team'] * 3 +
                avg_scores['industry_impact'] * 4
            )
        else:
            avg_scores = None
            avg_total = 0
        
        project_scores.append({
            'project': project,
            'avg_scores': avg_scores,
            'avg_total': avg_total,
            'total_evaluations': evaluations.count(),
        })
    
    # Sort by score (highest first)
    project_scores.sort(key=lambda x: x['avg_total'], reverse=True)
    
    # Add rank
    for idx, item in enumerate(project_scores):
        item['rank'] = idx + 1
    
    context = {
        'track': track,
        'project_scores': project_scores,
        'total_projects': len(project_scores),
    }
    
    return render(request, 'core/track_rankings.html', context)