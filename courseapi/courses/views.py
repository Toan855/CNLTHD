from rest_framework import viewsets, generics, status, parsers, permissions
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from courses.models import Category, Course, Lesson, User,Comment,Like
from courses import serializers,perms
from . import paginatiors


# không được viewsets.ModelViewSet vì nó sẽ hiện thực hóa tất cả api
# ViewSet chỉ hiện thực hóa layout co bản, generics.ListAPi hiện thực hóa api lấy danh sách (chỉ hiện thực hóa một cái này thôi)
class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.filter(active=True)
    serializer_class = serializers.CategorySerializer


class CourseViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = serializers.CourseSerializer
    pagination_class = paginatiors.CoursePagination

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(subject__icontains=q)

        cate_id = self.request.query_params.get('category_id')
        if cate_id:
            queryset = queryset.filter(category_id=cate_id)

        return queryset

    @action(methods=['get'], detail=True, url_path='lessons')
    def get_lessons(self, request, pk):
        lessons = self.get_object().lesson_set.filter(active=True)

        return Response(serializers.LessonSerializer(lessons, many=True).data, status=status.HTTP_200_OK)


class LessonViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Lesson.objects.prefetch_related('tags').filter(active=True)
    serializer_class = serializers.LessonDetailsSerializer


    def get_permissions(self):
        if self.action in ['get_comments','like'] and self.request.method.__eq__('POST'):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


    @action(methods=['get', 'post'], detail=True, url_path='comments')
    def get_comments(self, request, pk):
        if request.method.__eq__("POST"):
            t = serializers.CommentSerializer(data={
                'content': request.data.get('content'),
                'user': request.user.pk,
                'lesson': pk
            })
            t.is_valid(raise_exception=True)
            c = t.save()

            return Response(serializers.CommentSerializer(c).data, status=status.HTTP_201_CREATED)
        else:
            comments = self.get_object().comment_set.select_related('user').filter(active=True)
            return Response(serializers.CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='like', detail=True)
    def like(self, request, pk):
        li, created = Like.objects.get_or_create(user=request.user, lesson_id=pk)
        if not created:
            li.active = not li.active

        li.save()
        return Response(serializers.LessonDetailsSerializer(self.get_object(), context={'request': self.request}).data)



class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    @action(methods=['get', "patch"], url_path='current-user', detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        if request.method.__eq__("PATCH"):
            u = request.user

            for key in request.data:
                if key in ['first_name', 'last_name']:
                    setattr(u, key, request.data[key])
                elif key.__eq__('password'):
                    u.set_password(request.data[key])

            u.save()
            return Response(serializers.UserSerializer(u).data)
        else:
            return Response(serializers.UserSerializer(request.user).data)


class CommentViewSet(viewsets.ViewSet,generics.DestroyAPIView, generics.UpdateAPIView,ListAPIView):
    queryset = Comment.objects.filter(active=True)
    serializer_class = serializers.CommentSerializer
    permission_classes = [perms.CommentOwner]