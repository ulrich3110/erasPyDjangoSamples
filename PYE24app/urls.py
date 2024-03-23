from django.urls import path

from . import views

app_name = 'PYE24app'
urlpatterns = [
    # https://erasand.pythonanywhere.com/PYE/ZLMindex
    path("ZLMindex/", views.zlm_index, name="ZLMindex"),
    # https://erasand.pythonanywhere.com/PYE/ZLMdraws
    path("ZLMdraws/", views.zlm_draws, name="ZLMdraws"),
    # https://erasand.pythonanywhere.com/PYE/unique_id/ZLMgame
    path("<str:txUniqueId>/ZLMgame/", views.zlm_game, name="ZLMgame"),
    # https://erasand.pythonanywhere.com/PYE/unique_id/ZLMLsummary
    path("<str:txUniqueId>/ZLMsummary/", views.zlm_summary, name="ZLMsummary"),
]
