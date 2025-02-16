from django.urls import path
from docusign import views

urlpatterns = [
    path('docusign/login/', views.docusign_login, name='docusign_login'),
    path('docusign/callback/', views.docusign_callback, name='docusign_callback'),
    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("create_contract/", views.create_envelope, name="create_contract"),
    path("success/", views.success, name="success"),
    path("sign_completed/", views.success, name="success"),

    # other urls...
]
