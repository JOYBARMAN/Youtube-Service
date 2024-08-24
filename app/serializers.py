from rest_framework import serializers

from .youtube_service import YoutubeServiceApi


class VideoSerializer(serializers.Serializer):
    title = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True)
    tags = serializers.ListField(
        child=serializers.CharField(), allow_empty=True, default=[],write_only=True
    )
    category_id = serializers.IntegerField(default=None, write_only=True)
    video_path = serializers.FileField(write_only=True)

    def create(self, validated_data):
        response = YoutubeServiceApi().upload_video(
            validated_data["video_path"],
            validated_data["title"],
            validated_data["description"],
            validated_data["tags"],
            validated_data["category_id"],
        )

        self._response = response
        return response

    def to_representation(self, instance):
        return self._response
