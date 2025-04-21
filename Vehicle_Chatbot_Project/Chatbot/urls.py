from django.urls import path
from .views import vehicle_query_view, default_chatbot_view, home_view, get_vehicle_table_view, filter_vehicles_view, compare_vehicles_view

urlpatterns = [
    path('query/', vehicle_query_view, name='vehicle_query'),
    path('chatbot/', default_chatbot_view, name='default_chatbot'), 
    path('', home_view, name='home'),
    path('get_vehicle_table/', get_vehicle_table_view, name='get_vehicle_table'),
    path('filter/', filter_vehicles_view, name='filter_vehicles'),
    path('compare_vehicles/', compare_vehicles_view, name='compare_vehicles'),
]