from django.urls import path
from .views import vehicle_query_view, default_chatbot_view, home_view, get_vehicle_table_view, filter_vehicles_view, compare_vehicles_view, price_recommendations_view, vehicle_specifications_view, multi_step_interaction_view, compare_view, specifications_view, financial_options_view, choose_vehicle_view, restart_server

urlpatterns = [
    # path('query/', vehicle_query_view, name='vehicle_query'),
    path('chatbot/', default_chatbot_view, name='default_chatbot'), 
    path('', home_view, name='home'),
    path('get_vehicle_table/', get_vehicle_table_view, name='get_vehicle_table'),
    path('filter/', filter_vehicles_view, name='filter_vehicles'),
    path('compare_vehicles/', compare_vehicles_view, name='compare_vehicles'),
    path('price_recommendations/', price_recommendations_view, name='price_recommendations'),
    path('vehicle_specifications/<int:vehicle_id>/', vehicle_specifications_view, name='vehicle-specifications'),
    
    
    
    path('multi_step_interaction/', multi_step_interaction_view, name='multi_step_interaction'),
    path('vehicle_query/', vehicle_query_view, name='vehicle_query'), 
    path('compare/', compare_view, name='compare'),
    path('specifications/', specifications_view, name='specifications'),
    path('financial_options/', financial_options_view, name='financial_options'),
    path('choose_vehicle/', choose_vehicle_view, name='choose_vehicle'),
    path('restart_server/', restart_server, name='restart_server'),
]