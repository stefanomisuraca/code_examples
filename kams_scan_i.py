"""Kams Scan Serializer."""
from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from nsapi.models.kams_scan import (
    KamsScan,
    KamsRegionScoreData,
    KamsScoreData
)
from inflection import underscore
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.db import transaction
import logging
import json

logger = logging.getLogger('project_name')

regional_scores_keys = [
    "left_knee", "right_knee",
    "left_hip", "right_hip",
    "left_ankle", "right_ankle",
    "left_scapula", "right_scapula",
    "left_si_joint", "right_si_joint",
    "left_shoulder", "right_shoulder",
    "thoracic",
]


class KamsRegionScoreSerializer(serializers.ModelSerializer):
    """Serializer for Kams Region."""

    class Meta:
        """Meta Class."""

        exclude = ('id', )
        model = KamsRegionScoreData


class KamsScoreSerializer(serializers.ModelSerializer):
    """Serializer for Kams Score."""

    class Meta:
        """Meta Class."""

        exclude = ('id', 'kams_scan')
        model = KamsScoreData


class KamsScanISerializer(serializers.ModelSerializer):
    """Kams Scan Serializer."""

    def to_internal_value(self, data):
        """Read-Write handler for kams serialier."""
        validated_data = {}
        workflows = data.get('Workflows')
        analysis = workflows[0].get('analysis')
        region_scores = analysis.get('region_scores')
        kams_score = workflows[0].get('kams_scores')
        for region_score in region_scores:
            validated_data[underscore(region_score.get("joint_type"))] = {
                "overall_score": region_score.get('overall_score'),
                "joint_type": region_score.get('joint_type'),
                "dominant_issue": region_score.get('dominant_issue'),
                "dominant_plane": region_score.get('dominant_plane'),
                "mobility_frontal": region_score.get("scores").get("MOBILITYFRONTAL"), #noqa
                "mobility_transverse": region_score.get("scores").get("MOBILITYTRANSVERSE"), #noqa
                "mobility_sagittal": region_score.get("scores").get("MOBILITYSAGITTAL"), #noqa
                "stability_frontal": region_score.get("scores").get("STABILITYFRONTAL"), #noqa
                "stability_transverse": region_score.get("scores").get("STABILITYTRANSVERSE"), #noqa
                "stability_sagittal": region_score.get("scores").get("STABILITYSAGITTAL"), #noqa
              }
        validated_data["kams_score"] = {
          "total_score": kams_score.get("TotalScore"),
          "balance_index": kams_score.get("Balance_Index"),
          "flexibility_index": kams_score.get("Flexibility_Index"),
          "core_stability_index": kams_score.get("Core_Stability_Index"),
          "dynamic_posture_index": kams_score.get("Dynamic_Posture_Index"),
          "lower_extremity_power_score": kams_score.get("Lower_Extremity_Power_Score"), #noqa
          "functional_asymmetry_index": kams_score.get("Functional_Asymmetry_Index", 0), #noqa
          "injury_index": kams_score.get("Injury_Index")
        }
        validated_data["user"] = self.context.get("request").user
        validated_data["kams_data"] = data

        return validated_data

    def to_representation(self, obj):
        """Return custom representation for the API."""
        try:
            analysis = obj.kams_data.get("Workflows")[0].get("analysis")
        except TypeError:
            analysis = []
        return {

                'analysis': analysis,
                'kams_scores': KamsScoreSerializer(obj.kams_score).data,
                'kiosk_serial': obj.kiosk_serial,
                'user_id': obj.user.id,
                'qc_lat': obj.qc_lat,
                'qc_lng': obj.qc_lng,
                'app_lat': obj.app_lat,
                'app_lng': obj.app_lng,
                'status': obj.status,
                'scan_id': obj.scan_id,
                'date_taken': obj.date_taken
            }

    def create(self, validated_data):
        """Create an instance based on the validated data."""
        created_data = {
            "user": validated_data["user"],
            "kams_data": validated_data["kams_data"]
        }
        with transaction.atomic():
            new_kams = KamsScan.objects.create(**created_data)
            KamsScoreData.objects.create(
                **validated_data["kams_score"],
                kams_scan=new_kams
            )
            for key in regional_scores_keys:
                KamsRegionScoreData.objects.create(
                    **validated_data[key],
                    kams_scan=new_kams
                )
            return new_kams

    def update(self, instance, validated_data):
        """Update a kams using serializer."""
        KamsScoreData.objects.update_or_create(
            kams_scan=instance,
            defaults=validated_data['kams_score']
        )
        for key in regional_scores_keys:
            KamsRegionScoreData.objects.update_or_create(
                kams_scan=instance,
                joint_type=key,
                defaults=validated_data[key]
            )
        instance.kams_data = validated_data["kams_data"]
        instance.save()
        return instance

    class Meta:
        """Meta Class."""

        exclude = ('kams_data', )
        model = KamsScan
