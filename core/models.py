from django.db import models
import uuid
import random
import string
from django.utils import timezone

class Track(models.Model):
    title = models.CharField(max_length=100)
    sub_title = models.CharField(max_length=245)
    tags = models.CharField(max_length=245)
    icon_class = models.CharField(max_length=245)

    def __str__(self):
        return self.title
    

class Project(models.Model):

    def generate_project_code():
        """Generate unique project code like PRJ-2024-ABC123"""
        year = timezone.now().year
        while True:
            chars = string.ascii_uppercase + string.digits
            random_part = ''.join(random.choices(chars, k=20))
            code = f"PRJ-{year}-{random_part}"
            if not Project.objects.filter(project_code=code).exists():
                return code

    title = models.CharField(max_length=200)
    description = models.TextField()
    technology = models.CharField(max_length=100, blank=True)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    project_code = models.CharField(max_length=40, unique=True, default=generate_project_code, editable=False)

    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    @property
    def student_count(self):
        return self.team_members.count()
    
    def save(self, *args, **kwargs):
        if not self.project_code:
            self.project_code = self.generate_project_code()
        super().save(*args, **kwargs)


class TeamMember(models.Model):
    """Students working on the project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='team_members')
    full_name = models.CharField(max_length=200)
    student_id = models.CharField(max_length=20)
    email = models.EmailField()
    
    class Meta:
        ordering = ['full_name']
    
    def __str__(self):
        return f"{self.full_name} - {self.project.title}"
    
    @property
    def initials(self):
        names = self.full_name.split()
        if len(names) >= 2:
            return f"{names[0][0]}{names[1][0]}".upper()
        return names[0][:2].upper() if names else '??'



class ProjectEvaluation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='evaluations')
    
    # Evaluator info (minimal)
    evaluator_name = models.CharField(max_length=200)
    evaluator_email = models.EmailField(blank=True,null=True)
    evaluator_organization = models.CharField(max_length=200, blank=True,null=True)
    
    # Your specific criteria (1-5 scale)
    problem_innovation = models.IntegerField(default=3, help_text="Problem & Innovation (20%)")
    technical_excellence = models.IntegerField(default=3, help_text="Technical Excellence (25%)")
    functionality_demo = models.IntegerField(default=3, help_text="Functionality & Demonstration (20%)")
    presentation_team = models.IntegerField(default=3, help_text="Presentation & Team Competence (15%)")
    industry_impact = models.IntegerField(default=3, help_text="Industry Impact & Readiness (20%)")
    
    # Optional feedback
    comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project Evaluation'
        verbose_name_plural = 'Project Evaluations'
    
    def __str__(self):
        return f"{self.project.title} - {self.evaluator_name}"
    
    @property
    def total_score(self):
        """Calculate weighted score out of 100"""
        return (
            self.problem_innovation * 4 +  
            self.technical_excellence * 5 +  
            self.functionality_demo * 4 +  
            self.presentation_team * 3 +  
            self.industry_impact * 4 
        )
    
    @property
    def percentage_score(self):
        """Return score as percentage"""
        return (self.total_score / 100) * 100