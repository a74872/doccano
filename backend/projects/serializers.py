from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import (
    BoundingBoxProject,
    ImageCaptioningProject,
    ImageClassificationProject,
    IntentDetectionAndSlotFillingProject,
    Member,
    Project,
    SegmentationProject,
    Seq2seqProject,
    SequenceLabelingProject,
    Speech2textProject,
    Tag,
    TextClassificationProject,
    Perspective,
    LabelPerspective,
    ChoiceOption,
    PerspectiveResponse,
)


class MemberSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    rolename = serializers.SerializerMethodField()

    @classmethod
    def get_username(cls, instance):
        user = instance.user
        return user.username if user else None

    @classmethod
    def get_rolename(cls, instance):
        role = instance.role
        return role.name if role else None

    class Meta:
        model = Member
        fields = ("id", "user", "role", "username", "rolename")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "project",
            "text",
        )
        read_only_fields = ("id", "project")


class ProjectSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    author = serializers.SerializerMethodField()

    @classmethod
    def get_author(cls, instance):
        if instance.created_by:
            return instance.created_by.username
        return ""

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "guideline",
            "project_type",
            "created_at",
            "updated_at",
            "random_order",
            "author",
            "collaborative_annotation",
            "single_class_classification",
            "allow_member_to_create_label_type",
            "is_text_project",
            "tags",
        ]
        read_only_fields = (
            "created_at",
            "updated_at",
            "author",
            "is_text_project",
        )

    def create(self, validated_data):
        tags = TagSerializer(data=validated_data.pop("tags", []), many=True)
        project = self.Meta.model.objects.create(**validated_data)
        tags.is_valid()
        tags.save(project=project)
        return project

    def update(self, instance, validated_data):
        # Don't update tags. Please use TagAPI.
        validated_data.pop("tags", None)
        return super().update(instance, validated_data)


class TextClassificationProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = TextClassificationProject


class SequenceLabelingProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = SequenceLabelingProject
        fields = ProjectSerializer.Meta.fields + ["allow_overlapping", "grapheme_mode", "use_relation"]


class Seq2seqProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = Seq2seqProject


class IntentDetectionAndSlotFillingProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = IntentDetectionAndSlotFillingProject


class Speech2textProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = Speech2textProject


class ImageClassificationProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = ImageClassificationProject


class BoundingBoxProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = BoundingBoxProject


class SegmentationProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = SegmentationProject


class ImageCaptioningProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = ImageCaptioningProject


class ProjectPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Project: ProjectSerializer,
        **{cls.Meta.model: cls for cls in ProjectSerializer.__subclasses__()},
    }

class ChoiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChoiceOption
        fields = ["value"]

class LabelSerializer(serializers.ModelSerializer):
    options = ChoiceOptionSerializer(many=True, required=False)

    class Meta:
        model  = LabelPerspective
        fields = ["id", "name", "data_type", "int_min", "int_max", "options"]

    def create(self, validated_data):
        opts = validated_data.pop("options", [])
        label = super().create(validated_data)
        if label.data_type == LabelPerspective.DataType.CHOICE:
            for option in opts[:4]:                       # garante máximo de 4
                ChoiceOption.objects.create(label=label, **option)
        return label

class PerspectiveSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    created_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model  = Perspective
        fields = ["id", "title", "project", "labels", "created_by", "created_at"]
        read_only_fields = ("project",)

    def create(self, validated_data):
        labels = validated_data.pop("labels")
        perspective = Perspective.objects.create(**validated_data)
        for lbl in labels:
            LabelSerializer().create({**lbl, "perspective": perspective})
        return perspective

    def update(self, instance, validated_data):
        labels_data = validated_data.pop("labels", [])

        instance.title = validated_data.get("title", instance.title)
        instance.save()

        instance.labels.all().delete()

        for lbl in labels_data:
            LabelSerializer().create({**lbl, "perspective": instance})

        return instance


class PerspectiveResponseSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    perspective = serializers.PrimaryKeyRelatedField(queryset=Perspective.objects.all())
    choice_value = serializers.SlugRelatedField(
        slug_field='value',
        queryset=ChoiceOption.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = PerspectiveResponse
        fields = [
            'id',
            'perspective',
            'user',
            'string_value',
            'int_value',
            'choice_value',
            'created_at'
        ]
        read_only_fields = ('id', 'user', 'created_at')

    def to_internal_value(self, data):
        # Permitir múltiplas respostas no mesmo payload
        if isinstance(data.get('answers'), list):
            return data
        return super().to_internal_value(data)

    def validate(self, data):
        # Se answers está presente, validação será feita no create
        if isinstance(data.get('answers'), list):
            return data
        # Validação antiga para compatibilidade
        return super().validate(data)

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        # Se answers está presente, criar múltiplas respostas
        if isinstance(validated_data.get('answers'), list):
            perspective = validated_data['perspective']
            # Garantir que perspective é um objeto
            from projects.models import Perspective
            if isinstance(perspective, int):
                perspective = Perspective.objects.get(id=perspective)
            answers = validated_data['answers']
            responses = []
            for ans in answers:
                label_id = ans.get('label_id')
                label = perspective.labels.filter(id=label_id).first()
                if not label:
                    raise serializers.ValidationError(f"Label com id {label_id} não encontrada.")
                # Verifica se já existe resposta para este trio
                response, created = PerspectiveResponse.objects.get_or_create(
                    perspective=perspective,
                    user=user,
                    label=label,
                    defaults={}
                )
                # Atualiza o valor conforme o tipo da label
                if label.data_type == LabelPerspective.DataType.STRING:
                    response.string_value = ans.get('string_value')
                    response.int_value = None
                    response.choice_value = None
                elif label.data_type == LabelPerspective.DataType.INT:
                    response.int_value = ans.get('int_value')
                    response.string_value = None
                    response.choice_value = None
                elif label.data_type == LabelPerspective.DataType.CHOICE:
                    choice_val = ans.get('choice_value')
                    choice = label.options.filter(value=choice_val).first()
                    if not choice:
                        raise serializers.ValidationError(f"Opção '{choice_val}' não encontrada para label {label.name}.")
                    response.choice_value = choice
                    response.string_value = None
                    response.int_value = None
                response.save()
                responses.append(response)
            return responses
        # Caso antigo: criar uma resposta
        validated_data['user'] = user
        return super().create(validated_data)