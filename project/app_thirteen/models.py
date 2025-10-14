from django.db import models
from django.db.models import DO_NOTHING
from django.db.models import fields
from django.db.models.fields import related


class ModelThirty(models.Model):
    project = related.OneToOneField(
        "ModelThirtyOne", on_delete=DO_NOTHING, related_name="project_data"
    )
    active = fields.BooleanField(default=True)

    class Meta:
        db_table = "app_thirteen_projectdata"
        managed = False
        default_related_name = "project_data"


class ModelThirtyOne(models.Model):
    name = fields.CharField(max_length=1024)
    full_number = fields.CharField(max_length=1024, unique=True)
    non_billable = fields.BooleanField(default=False)
    # Refer to project/utils/globals.py for the hard code client name, used to determine if is_australian.
    is_australian = fields.BooleanField(default=False)
    senior_project_leads = related.ManyToManyField(
        "app_six.ModelNine",
        related_name="projects_as_senior_project_lead",
        limit_choices_to={
            "is_senior_project_lead": True,
        },
    )
    party_leaders = related.ManyToManyField(
        "app_six.ModelNine",
        blank=True,
        related_name="projects_as_party_leader",
        limit_choices_to={
            "is_party_leader": True,
        },
    )

    class Meta:
        ordering = ("-full_number",)


class ModelThirtyTwo(models.Model):
    project = related.ForeignKey("ModelThirtyOne", on_delete=models.CASCADE)
    field_eleven = fields.CharField(
        max_length=1024,
        choices=(
            ("one", "One"),
            ("two", "Two"),
        ),
    )
    effective = fields.DateField()

    class Meta:
        default_related_name = "project_status_history"
        ordering = ("-effective",)
        unique_together = ("project", "effective")
