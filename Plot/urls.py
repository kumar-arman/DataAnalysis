# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload_old/', views.plot_anc_data, name='plot_anc_data'),
    # Add other URL patterns as needed
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload_file'),
    path('select-title-column/', views.select_title_column, name='select_title_column'),
    path('select-columns/<str:title_column>/', views.select_columns, name='select_columns'),
    path('plot/', views.plot_graph, name='plot_graph'),
    path('handle_existing_file/<int:file_id>/', views.handle_existing_file, name='handle_existing_file'),
    
    path('upload_csv/', views.upload_csv_file, name='upload_csv_file'),
    path('select-csv-title-column/', views.select_csv_title_column, name='select_csv_title_column'),
    path('select-csv-columns/<str:title_column>/', views.select_csv_columns, name='select_csv_columns'),
    path('plot_csv/', views.plot_csv_graph, name='plot_csv_graph'),

    path('upload_json/', views.upload_json_file, name='upload_json_file'),
    path('select-json-columns/', views.select_json_columns, name='select_json_columns'),
    path('select-json-title-column/', views.select_json_title_column, name='select_json_title_column'),
    path('select-json-columns/<str:title_column>/', views.select_json_columns, name='select_json_columns'),
    path('plot_json/', views.plot_json_graph, name='plot_json_graph'),
]