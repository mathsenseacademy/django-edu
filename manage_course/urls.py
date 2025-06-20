from django.urls import path
from manage_course import views
# from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    #batch related urls
    path('create_course/', views.create_course, name='create_course'),
    path('edit_course/', views.edit_course, name='edit_course'),
    path('showcourseid/', views.show_course_by_id, name='show_course_by_id'),
    path('showallcourse/', views.show_all_courses, name='show_all_batch'),
    path('showallactivatecourse/', views.show_all_activate_courses, name='show_all_activate_batch'),
    path('all_courses_show_public/', views.all_courses_show_public, name='all_courses_show_public'),
    path('courses_detail_show_public/', views.courses_detail_show_public, name='courses_detail_show_public'),

     # course_curriculum related urls
    path('add_course_curriculum/', views.add_course_curriculum, name='add_course_curriculum'),
    path('show_all_curriculums/', views.show_all_curriculums, name='show_all_curriculums'),
    path('show_curriculum_by_id/', views.show_curriculum_by_id, name='show_curriculum_by_id'),
    path('edit_curriculum/', views.edit_curriculum, name='edit_curriculum'),
    path('show_active_curriculums/', views.show_active_curriculums, name='show_active_curriculums'),
    path('show_active_curriculums_by_course_id/', views.show_active_curriculums_by_course_id, name='show_active_curriculums_by_course_id'),
    
    # classroom_essentials related urls
    path('add_classroom_essentials/', views.add_classroom_essentials, name='add_classroom_essentials'),
    path('show_all_classroom_essentials/', views.show_all_classroom_essentials, name='show_all_classroom_essentials'),
    path('show_classroom_essentials_by_id/', views.show_classroom_essentials_by_id, name='show_classroom_essentials_by_id'),
    path('edit_classroom_essentials/', views.edit_classroom_essentials, name='edit_classroom_essentials'),
    path('show_active_classroom_essentials/', views.show_active_classroom_essentials, name='show_active_classroom_essentials'),
    path('show_active_classroom_essentials_by_course_id/', views.show_active_classroom_essentials_by_course_id, name='show_active_classroom_essentials_by_course_id'),

    # class lavel related urls
    path('add_class_level/', views.add_class_level, name='add_class_level'),
    path('show_all_class_levels/', views.show_all_class_levels, name='show_all_class_levels'),
    path('show_class_level_by_id/', views.show_class_level_by_id, name='show_class_level_by_id'),
    path('edit_class_level/', views.edit_class_level, name='edit_class_level'),
    path('show_active_class_levels/', views.show_active_class_levels, name='show_active_class_levels'),

    # category level related urls
    path('add_category_level/', views.add_category_level, name='add_category_level'),
    path('show_all_category_levels/', views.show_all_category_levels, name='show_all_category_levels'),
    path('show_category_level_by_id/', views.show_category_level_by_id, name='show_category_level_by_id'),
    path('edit_category_level/', views.edit_category_level, name='edit_category_level'),
    path('show_active_category_levels/', views.show_active_category_levels, name='show_active_category_levels'),


    #course related urls
    # path('createcourses/', views.createcourses, name='create_courses'),
    # path('editcourses/', views.editcourses, name='edit_courses'),
]
