from django.urls import path

from .views import (
    ChangeOwnPasswordView,
    CustomLoginView,
    UserBanView,
    UserCreateView,
    UserDeleteView,
    UserListView,
    UserReactivateView,
    UserResetPasswordView,
    UserUpdateView,
    logout_view,
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),

    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/ban/', UserBanView.as_view(), name='user_ban'),
    path('users/<int:pk>/reactivate/', UserReactivateView.as_view(), name='user_reactivate'),
    path('users/<int:pk>/reset-password/', UserResetPasswordView.as_view(), name='user_reset_password'),

    path('change-password/', ChangeOwnPasswordView.as_view(), name='change_own_password'),
]