from rest_framework.generics import CreateAPIView

from .serializers import VideoSerializer

class VideoUploadView(CreateAPIView):
    serializer_class = VideoSerializer