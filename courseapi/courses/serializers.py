from courses.models import Category, Course, Lesson, Tag,Comment,Like,User
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from cloudinary.http_client import HttpClient


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']


class ItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['image'] = instance.image.url

        return data


class CourseSerializer(ItemSerializer):
    class Meta:
        model = Course
        fields = ['id','subject','image','created_date','category_id']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class LessonSerializer(ItemSerializer):
    class Meta:
        model = Lesson
        fields = ['id' ,'subject','image','course_id','created_date','updated_date']


class LessonDetailsSerializer(LessonSerializer):
    tags = TagSerializer(many= True)
    liked = serializers.SerializerMethodField()

    def get_liked(self, lesson):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return lesson.like_set.filter(user=request.user, active=True).exists()

    class Meta:
        model = LessonSerializer.Meta.model
        fields = LessonSerializer.Meta.fields + ['content','tags','liked']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'avatar']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(u.password)
        u.save()

        return u

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            instance.save()

        return instance


    def to_representation(self, instance):
        d = super().to_representation(instance)
        d['avatar'] = instance.avatar.url if instance.avatar else ''
        return d


class CommentSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        return data

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_date', 'updated_date', 'user', 'lesson']
        extra_kwargs = {
            'lesson': {
                'write_only': True
            }
        }
# class CourseSerializer(serializers.ModelSerializer):
#     image = serializers.SerializerMethodField()
#     class Meta:
#         model = Course
#         fields = ['id','subject','image','created_date','category_id']
#
#     def get_image(self, obj):
#         return obj.image.url