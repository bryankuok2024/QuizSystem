from django.shortcuts import render
from django.views.generic import TemplateView
from questions.models import MajorSubject, Subject
from users.models import UserSubjectPurchase
from django.db.models import Prefetch, Count, Exists, OuterRef

# Create your views here.

class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Base queryset for subjects with question count
        subjects_queryset = Subject.objects.filter(is_published=True).annotate(
            question_count=Count('questions')
        )

        if user.is_authenticated:
            # Annotate subjects with purchase status for the current user
            purchased_subquery = UserSubjectPurchase.objects.filter(
                user=user, subject=OuterRef('pk')
            )
            subjects_queryset = subjects_queryset.annotate(
                is_purchased=Exists(purchased_subquery)
            )

        # Get all published major subjects and prefetch their annotated subjects
        major_subjects = MajorSubject.objects.prefetch_related(
            Prefetch(
                'subjects',
                queryset=subjects_queryset.order_by('name'),
                to_attr='published_subjects'
            )
        ).filter(is_active=True).order_by('name')

        # Get all published orphan subjects using the same annotated queryset
        orphan_subjects = subjects_queryset.filter(
            major_subject__isnull=True
        ).order_by('name')

        context["major_subjects"] = major_subjects
        context["orphan_subjects"] = orphan_subjects

        return context
