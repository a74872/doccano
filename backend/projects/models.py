import abc
import uuid
from typing import Any, Dict, Optional

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Manager
from polymorphic.models import PolymorphicModel
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from roles.models import Role


class ProjectType(models.TextChoices):
    DOCUMENT_CLASSIFICATION = "DocumentClassification"
    SEQUENCE_LABELING = "SequenceLabeling"
    SEQ2SEQ = "Seq2seq"
    INTENT_DETECTION_AND_SLOT_FILLING = "IntentDetectionAndSlotFilling"
    SPEECH2TEXT = "Speech2text"
    IMAGE_CLASSIFICATION = "ImageClassification"
    BOUNDING_BOX = "BoundingBox"
    SEGMENTATION = "Segmentation"
    IMAGE_CAPTIONING = "ImageCaptioning"


class Project(PolymorphicModel):
    name = models.CharField(max_length=100)
    description = models.TextField(default="")
    guideline = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    project_type = models.CharField(max_length=30, choices=ProjectType.choices)
    random_order = models.BooleanField(default=False)
    collaborative_annotation = models.BooleanField(default=False)
    single_class_classification = models.BooleanField(default=False)
    allow_member_to_create_label_type = models.BooleanField(default=False)

    def add_admin(self):
        admin_role = Role.objects.get(name=settings.ROLE_PROJECT_ADMIN)
        Member.objects.create(
            project=self,
            user=self.created_by,
            role=admin_role,
        )

    @property
    @abc.abstractmethod
    def is_text_project(self) -> bool:
        return False

    def clone(self) -> "Project":
        """Clone the project.
        See https://docs.djangoproject.com/en/4.2/topics/db/queries/#copying-model-instances

        Returns:
            The cloned project.
        """
        project = Project.objects.get(pk=self.pk)
        project.pk = None
        project.id = None
        project._state.adding = True
        project.save()

        def bulk_clone(queryset: models.QuerySet, field_initializers: Optional[Dict[Any, Any]] = None):
            """Clone the queryset.

            Args:
                queryset: The queryset to clone.
                field_initializers: The field initializers.
            """
            if field_initializers is None:
                field_initializers = {}
            items = []
            for item in queryset:
                item.id = None
                item.pk = None
                for field, value_or_callable in field_initializers.items():
                    if callable(value_or_callable):
                        value_or_callable = value_or_callable()
                    setattr(item, field, value_or_callable)
                item.project = project
                item._state.adding = True
                items.append(item)
            queryset.model.objects.bulk_create(items)

        bulk_clone(self.role_mappings.all())
        bulk_clone(self.tags.all())

        # clone examples
        bulk_clone(self.examples.all(), field_initializers={"uuid": uuid.uuid4})

        # clone label types
        bulk_clone(self.categorytype_set.all())
        bulk_clone(self.spantype_set.all())
        bulk_clone(self.relationtype_set.all())

        return project

    def __str__(self):
        return self.name


class TextClassificationProject(Project):
    @property
    def is_text_project(self) -> bool:
        return True


class SequenceLabelingProject(Project):
    allow_overlapping = models.BooleanField(default=False)
    grapheme_mode = models.BooleanField(default=False)
    use_relation = models.BooleanField(default=False)

    @property
    def is_text_project(self) -> bool:
        return True


class Seq2seqProject(Project):
    @property
    def is_text_project(self) -> bool:
        return True


class IntentDetectionAndSlotFillingProject(Project):
    @property
    def is_text_project(self) -> bool:
        return True


class Speech2textProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class ImageClassificationProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class BoundingBoxProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class SegmentationProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class ImageCaptioningProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class Tag(models.Model):
    text = models.TextField()
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="tags")

    def __str__(self):
        return self.text


class MemberManager(Manager):
    def can_update(self, project: int, member_id: int, new_role: str) -> bool:
        """The project needs at least 1 admin.

        Args:
            project: The project id.
            member_id: The member id.
            new_role: The new role name.

        Returns:
            Whether the mapping can be updated or not.
        """
        queryset = self.filter(project=project, role__name=settings.ROLE_PROJECT_ADMIN)
        if queryset.count() > 1:
            return True
        else:
            admin = queryset.first()
            # we can change the role except for the only admin.
            return admin.id != member_id or new_role == settings.ROLE_PROJECT_ADMIN

    def has_role(self, project_id: int, user: User, role_name: str):
        return self.filter(project=project_id, user=user, role__name=role_name).exists()


class Member(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="role_mappings")
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="role_mappings")
    role = models.ForeignKey(to=Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = MemberManager()
    
    def is_annotator(self):
        return self.role.name == settings.ROLE_ANNOTATOR
    
    def is_annotation_approver(self):
        return self.role.name == settings.ROLE_ANNOTATION_APPROVER

    def clean(self):
        members = self.__class__.objects.exclude(id=self.id)
        if members.filter(user=self.user, project=self.project).exists():
            message = "This user is already assigned to a role in this project."
            raise ValidationError(message)

    def is_admin(self):
        return self.role.name == settings.ROLE_PROJECT_ADMIN

    @property
    def username(self):
        return self.user.username

    class Meta:
        unique_together = ("user", "project")

class DataType(models.TextChoices):
    STRING = "string", "String"
    INTEGER = "integer", "Integer"
    FLOAT = "float", "Float"
    BOOLEAN = "boolean", "Boolean"


class Perspective(models.Model):
    project     = models.ForeignKey(Project, on_delete=models.CASCADE,
                                    related_name="perspectives")
    title       = models.CharField(max_length=100, default="Untitled perspective")
    description = models.CharField(max_length=1000, default="No details yet")
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, related_name="created_perspectives")
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.project.name})"

    class Meta:
        # título único POR PROJECTO, ignorando maiúsc/minúsc
        constraints = [
            UniqueConstraint(
                Lower("title"), "project",
                name="uniq_persp_title_per_project_i",
            )
        ]


class LabelPerspective(models.Model):
    """
    Uma 'etiqueta' pertencente a uma Perspective
    """
    class DataType(models.TextChoices):
        STRING = "string", "Texto livre"
        INT    = "int",    "Número inteiro"
        CHOICE = "choice", "Opção de lista"

    perspective = models.ForeignKey(Perspective, on_delete=models.CASCADE,
                                    related_name="labels")
    name        = models.CharField(max_length=100)
    data_type   = models.CharField(max_length=10, choices=DataType.choices)

    # –– campos opcionais para regras de validação ––
    int_min     = models.IntegerField(null=True, blank=True)
    int_max     = models.IntegerField(null=True, blank=True)

    def clean(self):
        """
        Validação de consistência:
        * intervalo só faz sentido para data_type == INT
        * opções só fazem sentido para data_type == CHOICE
        """
        from django.core.exceptions import ValidationError
        if self.data_type != self.DataType.INT and (self.int_min or self.int_max):
            raise ValidationError("Intervalo só permitido para etiquetas inteiras.")

    def __str__(self):
        return f"{self.name} ({self.get_data_type_display()})"


class ChoiceOption(models.Model):
    """
    Até 4 opções vinculadas a uma Label do tipo CHOICE
    """
    label = models.ForeignKey(LabelPerspective, on_delete=models.CASCADE,
                              related_name="options")
    value = models.CharField(max_length=50)

    class Meta:
        unique_together = ("label", "value")
        ordering        = ["pk"]

    def __str__(self):
        return self.value


class PerspectiveResponse(models.Model):
    """
    Resposta de um usuário a uma perspectiva.
    Uma perspectiva só pode ser respondida uma vez por usuário e label.
    """
    perspective = models.ForeignKey(Perspective, on_delete=models.CASCADE,
                                  related_name="responses")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name="perspective_responses")
    label = models.ForeignKey('LabelPerspective', on_delete=models.CASCADE, related_name='responses', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Campos para armazenar as respostas
    string_value = models.TextField(null=True, blank=True)
    int_value = models.IntegerField(null=True, blank=True)
    choice_value = models.ForeignKey(ChoiceOption, on_delete=models.SET_NULL,
                                   null=True, blank=True)

    class Meta:
        unique_together = ("perspective", "user", "label")
        ordering = ["-created_at"]

    def clean(self):
        """
        Validação de consistência:
        * Apenas um tipo de valor pode ser preenchido
        * O tipo do valor deve corresponder ao tipo da label
        """
        from django.core.exceptions import ValidationError
        
        # Conta quantos valores estão preenchidos
        values_count = sum(1 for v in [self.string_value, self.int_value, self.choice_value] if v is not None)
        if values_count != 1:
            raise ValidationError("Apenas um tipo de valor deve ser preenchido.")

        # Verifica se o tipo do valor corresponde ao tipo da label
        label = self.perspective.labels.first()  # Assumindo que cada perspectiva tem apenas uma label
        if label:
            if label.data_type == LabelPerspective.DataType.STRING and not self.string_value:
                raise ValidationError("Valor de texto esperado.")
            elif label.data_type == LabelPerspective.DataType.INT and not self.int_value:
                raise ValidationError("Valor inteiro esperado.")
            elif label.data_type == LabelPerspective.DataType.CHOICE and not self.choice_value:
                raise ValidationError("Opção de escolha esperada.")

    def __str__(self):
        return f"Resposta de {self.user.username} para {self.perspective.title}"