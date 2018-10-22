from rest_framework import fields
from rest_framework.serializers import ModelSerializer

from blog.models import Post


class PostSerializer(ModelSerializer):  # Django Form/ModelForm과 유사
    class Meta:
        model = Post
        fields = '__all__'