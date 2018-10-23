import re

from django import forms
from blog.models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message']

    def clean_message(self):
        message = self.cleaned_data.get('message', None)
        if message:
            if not re.search(r'[ㄱ-힣]', message):
                raise forms.ValidationError('메세지에 한글이 필요합니다.')

        return message
    