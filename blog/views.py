from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import resolve_url
from django.template.defaultfilters import truncatewords
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from blog.forms import CommentForm
from blog.models import Comment
from blog.models import Post
from blog.serializers import PostSerializer
from rest_framework.renderers import JSONRenderer


class PostListView(ListView):
    model = Post
    paginate_by = 10

    def get_template_names(self):
        if self.request.is_ajax():
            return ['blog/_post_list.html']
        return ['blog/index.html']


index = PostListView.as_view()

post_new = CreateView.as_view(model=Post, fields='__all__')


class PostDetailView(DetailView):
    model = Post

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            return JsonResponse({
                'title': self.object.title,
                'summary': truncatewords(self.object.content, 100),
            })
        # 템플릿 렌더링
        return super().render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context


post_detail = PostDetailView.as_view()

post_edit = UpdateView.as_view(model=Post, fields='__all__')


class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')


post_delete = PostDeleteView.as_view()


class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        response = super().form_valid(form)

        if self.request.is_ajax():
            return JsonResponse({
                'id': comment.id,
                'message': comment.message,
                'updated_at': comment.updated_at,
                'edit_url': resolve_url('blog:comment_edit', comment.post.pk, comment.pk),
                'delete_url': resolve_url('blog:comment_delete', comment.post.pk, comment.pk),
            })

        return response     # url redirect 응답

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(dict(form.errors, is_success=False))
        return super().form_invalid(form)

    def get_success_url(self):
        return resolve_url(self.object.post)


comment_new = CommentCreateView.as_view()


class CommentUpdateView(UpdateView):
    model = Comment
    fields = ['message']

    def get_success_url(self):
        return resolve_url(self.object.post)


comment_edit = CommentUpdateView.as_view()


class CommentDeleteView(DeleteView):
    model = Comment

    def get_success_url(self):
        return resolve_url(self.object.post)


comment_delete = CommentDeleteView.as_view()


def post_list_json(request):
    qs = Post.objects.all()

    # 직접 직렬화 코딩
    # post_list = []
    # for post in qs:
    #     post_list.append({'id': post.id, 'title': post.title, 'content': post.content})
    #
    # return JsonResponse(post_list, safe=False)

    # django-rest-framework 활용
    serializer = PostSerializer(qs, many=True)
    json_utf8_string = JSONRenderer().render(serializer.data)

    # return HttpResponse(json_utf8_string)     # Content-Type 헤더가 text/html; charset=utf-8 로 디폴트 지정
    return HttpResponse(json_utf8_string, content_type='application/json; charset=utf-8')  # 커스텀 지정
