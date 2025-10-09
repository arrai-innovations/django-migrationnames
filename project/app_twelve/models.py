from django.db import models
from django.db.models import DO_NOTHING
from django.db.models import fields
from django.db.models.fields import related


class ModelTwentyFive(models.Model):
    phase = related.OneToOneField(
        "app_twelve.ModelTwentySix", on_delete=DO_NOTHING, related_name="phase_data"
    )
    active = fields.BooleanField()

    class Meta:
        db_table = "app_twelve_phasedata"
        managed = False
        default_related_name = "phase_data"


class ModelTwentySix(models.Model):
    project = related.ForeignKey(
        "app_thirteen.ModelThirtyOne", on_delete=models.CASCADE, related_name="phases"
    )
    name = fields.CharField(max_length=1024)
    sort_order = fields.PositiveIntegerField()

    class Meta:
        unique_together = ("project", "name")
        ordering = ("project", "sort_order")


class ModelTwentySeven(models.Model):
    phase = related.ForeignKey(
        "app_twelve.ModelTwentySix",
        on_delete=models.CASCADE,
        related_name="project_categories",
    )
    work_category = related.ForeignKey(
        "app_eighteen.ModelFiftyFour",
        on_delete=models.PROTECT,
        related_name="project_categories",
    )

    class Meta:
        verbose_name_plural = "project categories"
        verbose_name = "project category"
        unique_together = ("phase", "work_category")
        ordering = ("phase", "work_category")


class ModelTwentyEight(models.Model):
    project_category = related.ForeignKey(
        "app_twelve.ModelTwentySeven",
        on_delete=models.CASCADE,
        related_name="project_work_activities",
    )
    work_activity = related.ForeignKey(
        "app_eighteen.ModelFiftyFive",
        on_delete=models.PROTECT,
        related_name="project_work_activities",
    )
    work_type = fields.CharField(
        max_length=1024,
        choices=(
            ("one", "One"),
            ("two", "Two"),
        ),
        verbose_name="type",
    )

    class Meta:
        verbose_name_plural = "work activities"
        verbose_name = "work activity"
        unique_together = ("project_category", "work_activity")
        ordering = ("project_category", "work_activity")


class ModelTwentyNine(models.Model):
    phase = related.ForeignKey("ModelTwentySix", on_delete=models.CASCADE)
    field_eleven = fields.CharField(
        max_length=1024,
        choices=(
            ("one", "One"),
            ("two", "Two"),
        ),
    )
    effective = fields.DateField()

    class Meta:
        default_related_name = "phase_status_history"
        ordering = ("-effective",)
        unique_together = ("phase", "effective")
