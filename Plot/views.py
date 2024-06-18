from django.shortcuts import render, redirect
from django.conf import settings
from .forms import ExcelUploadForm,UploadFileForm,GraphForm,TitleColumnForm,GraphCSVForm
import pandas as pd
import matplotlib.pyplot as plt
import io,os,json
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.csrf import csrf_exempt,csrf_protect,ensure_csrf_cookie,requires_csrf_token
from django.views.decorators.http import require_http_methods
import plotly.graph_objs as go
from io import BytesIO
import urllib, base64
from .models import Table1, Table2, UploadedFile
import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import escape
from django.utils.safestring import mark_safe

def index(request):
    return render(request, 'base_dashboard.html')

def plot_anc_data(request):
    error_message = None
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                df = pd.read_excel(file, engine='openpyxl')
                states = df['State']
                total_value = df['total_value']
                plot_uri = generate_plot(states, total_value)
                return render(request, 'plot.html', {'data': plot_uri})
            except Exception as e:
                error_message = str(e)
    else:
        form = ExcelUploadForm()
    
    return render(request, 'upload.html', {'form': form, 'error_message': error_message})

def generate_plot(states, Public):
    plt.figure(figsize=(15, 9))
    plt.bar(states, Public, color='skyblue')
    plt.xlabel('State')
    plt.ylabel('Total number of pregnant women registered for ANC')
    plt.title('Total Number of Pregnant Women Registered for ANC in 2019-2020 by State')
    plt.xticks(rotation=45)
    plt.grid(axis='y')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri


@cache_control(max_age=0,no_cache=True, must_revalidate=True, no_store=True, CSRF_COOKIE_SECURE=True)
@requires_csrf_token
@ensure_csrf_cookie
@csrf_protect
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            uploaded_file_name = uploaded_file.name
            
            # Construct the file path
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', uploaded_file_name)
            
            # Check if the file already exists in the media/uploads folder
            if os.path.exists(file_path):
                # File exists, proceed with the existing file
                existing_file = UploadedFile.objects.filter(file='uploads/' + uploaded_file_name).first()
                if existing_file:
                    # If a file with the same name exists in the database, present an option to select it
                    return render(request, 'select_file.html', {'existing_file': existing_file})
                else:
                    # Handle case where file exists in the filesystem but not in the database (optional)
                    return render(request, 'error1.html', {'message': 'File exists in the filesystem but not in the database.'})
            else:
                # File does not exist, save the new uploaded file
                form.save()
                return redirect('select_title_column')  # Redirect to next step after successful upload
    else:
        form = UploadFileForm()
    
    return render(request, 'upload_new.html', {'form': form})

def handle_existing_file(request, file_id):
    # Retrieve the existing file
    existing_file = get_object_or_404(UploadedFile, pk=file_id)
    # Store the existing file in session
    request.session['active_file_id'] = existing_file.id
    # Logic to handle the existing file selection
    # This can include setting a session variable, redirecting to another view, etc.
    # For simplicity, we'll just redirect to the 'select_title_column' view
    return redirect('select_title_column')

def select_title_column(request):
    # Get the active file from session
    active_file_id = request.session.get('active_file_id')
    if not active_file_id:
        return render(request, 'error1.html', {'message': 'No file selected or uploaded.'})
    
    try:
        latest_file = UploadedFile.objects.get(id=active_file_id)
        file_path = latest_file.file.path
    except UploadedFile.DoesNotExist:
        return render(request, 'error1.html', {'message': 'No files uploaded yet.'})

    try:
        df = pd.read_excel(file_path)
        columns = df.columns.tolist()
    except Exception as e:
        return render(request, 'error1.html', {'message': f'Error reading Excel file: {e}'})

    if request.method == 'POST':
        form = TitleColumnForm(request.POST, columns=columns)
        if form.is_valid():
            title_column = form.cleaned_data['title_column']
            return redirect('select_columns', title_column=title_column)
    else:
        form = TitleColumnForm(columns=columns)

    return render(request, 'select_title_column.html', {'form': form})

@cache_control(max_age=0, no_cache=True, must_revalidate=True, no_store=True, CSRF_COOKIE_SECURE=True)
@requires_csrf_token
@ensure_csrf_cookie
@csrf_protect
def select_columns(request, title_column):
    # Get the active file from session
    active_file_id = request.session.get('active_file_id')
    if not active_file_id:
        return render(request, 'error1.html', {'message': 'No file selected or uploaded.'})
    
    try:
        latest_file = UploadedFile.objects.get(id=active_file_id)
        file_path = latest_file.file.path
    except UploadedFile.DoesNotExist:
        return render(request, 'error1.html', {'message': 'No files uploaded yet.'})

    try:
        df = pd.read_excel(file_path)
        columns = df.columns.tolist()
        title_values_choices = [(val, val) for val in df[title_column].unique()]
    except Exception as e:
        return render(request, 'error1.html', {'message': f'Error reading Excel file: {e}'})

    if request.method == 'POST':
        form = GraphForm(request.POST, columns=columns, title_values_choices=title_values_choices)
        if form.is_valid():
            x_axis = form.cleaned_data['x_axis']
            y_axis = form.cleaned_data['y_axis']
            graph_type = form.cleaned_data['graph_type']
            title_value = form.cleaned_data['title_values']
            width = form.cleaned_data['width']
            height = form.cleaned_data['height']
            return plot_graph(request, file_path, x_axis, y_axis, graph_type, title_column, title_value, width, height, form)
    else:
        form = GraphForm(columns=columns, title_values_choices=title_values_choices)

    return render(request, 'select_columns.html', {'form': form})

def plot_graph(request, file_path, x_axis, y_axis, graph_type, title_column, title_value, width, height, form=None):
    try:
        df = pd.read_excel(file_path)
        df_filtered = df[df[title_column] == title_value]
    except Exception as e:
        return render(request, 'error1.html', {'message': f'Error reading Excel file: {e}'})

    title = title_value

    # Create traces based on the graph type
    traces = []
    try:
        if graph_type == 'line':
            for col in y_axis:
                traces.append(go.Scatter(x=df_filtered[x_axis], y=df_filtered[col], mode='lines', name=col))
        elif graph_type == 'bar':
            for col in y_axis:
                traces.append(go.Bar(x=df_filtered[x_axis], y=df_filtered[col], name=col))
        elif graph_type == 'pie':
            if len(y_axis) != 1:
                return render(request, 'error1.html', {'message': 'Pie chart requires exactly one y-axis column.'})
            traces.append(go.Pie(labels=df_filtered[x_axis], values=df_filtered[y_axis[0]]))
        else:
            return render(request, 'error1.html', {'message': 'Unsupported graph type.'})
    except Exception as e:
        return render(request, 'error1.html', {'message': f'Error creating graph: {e}'})

    # Layout configuration
    layout = go.Layout(title=title, xaxis=dict(title=x_axis), yaxis=dict(title=', '.join(y_axis)),
                       width=width, height=height)

    fig = go.Figure(data=traces, layout=layout)
    plot_div = fig.to_html(full_html=False)

    if form is None:
        form = GraphForm(columns=df.columns.tolist(), title_values_choices=[(val, val) for val in df[title_column].unique()])

    # Filter the DataFrame to include only the specified columns and rows
    filtered_columns = [x_axis] + y_axis
    df_filtered = df_filtered[filtered_columns]

    table_html = df_filtered.to_html(classes='table table-striped')

    return render(request, 'plot_new.html', {'plot_div': plot_div, 'form': form, 'title_column': title_column, 'table_html': mark_safe(table_html)})

################################# Import CSV File ##################################

def upload_csv_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('select_csv_title_column')
    else:
        form = UploadFileForm()
    return render(request, 'upload_csv_new.html', {'form': form})

def select_csv_title_column(request):
    try:
        latest_file = UploadedFile.objects.latest('uploaded_at')
        file_path = latest_file.file.path
    except UploadedFile.DoesNotExist:
        return render(request, 'error1.html', {'message': 'No files uploaded yet.'})

    try:
        df = pd.read_csv(file_path)
        columns = df.columns.tolist()
    except Exception as e:
        return render(request, 'error1.html', {'message': f'Error reading CSV file: {e}'})

    if request.method == 'POST':
        form = TitleColumnForm(request.POST, columns=columns)
        if form.is_valid():
            title_column = form.cleaned_data['title_column']
            return redirect('select_csv_columns', title_column=title_column)
    else:
        form = TitleColumnForm(columns=columns)

    return render(request, 'select_csv_title_column.html', {'form': form})



def select_csv_columns(request, title_column):
    try:
        latest_file = UploadedFile.objects.latest('uploaded_at')
        file_path = latest_file.file.path
    except UploadedFile.DoesNotExist:
        return render(request, 'error1.html', {'message': 'No files uploaded yet.'})

    try:
        df = pd.read_csv(file_path)
        columns = df.columns.tolist()
        title_values_choices = [(val, val) for val in df[title_column].unique()]
    except Exception as e:
        return render(request, 'error1.html', {'message': f'Error reading CSV file: {e}'})

    if request.method == 'POST':
        form = GraphCSVForm(request.POST, columns=columns, title_values_choices=title_values_choices)
        if form.is_valid():
            x_axis = form.cleaned_data['x_axis']
            y_axis = form.cleaned_data['y_axis']
            graph_type = form.cleaned_data['graph_type']
            title_values = form.cleaned_data['title_values']
            width = form.cleaned_data['width']
            height = form.cleaned_data['height']
            return plot_csv_graph(request, file_path, x_axis, y_axis, graph_type, title_column, title_values, width, height,form)
    else:
        form = GraphCSVForm(columns=columns, title_values_choices=title_values_choices)

    return render(request, 'select_csv_columns.html', {'form': form})



def plot_csv_graph(request, file_path, x_axis, y_axis, graph_type, title_column, title_values, width, height, form=None):
    try:
        df = pd.read_excel(file_path) if file_path.endswith('.xlsx') else pd.read_csv(file_path)
        df_filtered = df[df[title_column].isin(title_values)]
    except Exception as e:
        return render(request, 'error1.html', {'message': f'Error reading file: {e}'})

    title = ', '.join(title_values)

    # Create traces based on the graph type
    traces = []
    try:
        if graph_type == 'line':
            for col in y_axis:
                traces.append(go.Scatter(x=df_filtered[x_axis], y=df_filtered[col], mode='lines', name=col))
        elif graph_type == 'bar':
            for col in y_axis:
                traces.append(go.Bar(x=df_filtered[x_axis], y=df_filtered[col], name=col))
        elif graph_type == 'pie':
            if len(y_axis) != 1:
                return render(request, 'error1.html', {'message': 'Pie chart requires exactly one y-axis column.'})
            traces.append(go.Pie(labels=df_filtered[x_axis], values=df_filtered[y_axis[0]]))
        else:
            return render(request, 'error1.html', {'message': 'Unsupported graph type.'})
    except Exception as e:
        return render(request, 'error1.html', {'message': f'Error creating graph: {e}'})

    # Layout configuration
    layout = go.Layout(title=title, xaxis=dict(title=x_axis), yaxis=dict(title=', '.join(y_axis)),
                       width=width, height=height)

    fig = go.Figure(data=traces, layout=layout)
    plot_div = fig.to_html(full_html=False)

    # Create HTML for the table
    table_html = df_filtered[[x_axis] + y_axis].to_html(classes='table', index=False)

    if form is None:
        form = GraphForm(columns=df.columns.tolist(), title_values_choices=[(val, val) for val in df[title_column].unique()])

    return render(request, 'plot_csv_new.html', {'plot_div': plot_div, 'form': form, 'title_column': title_column, 'table_html': mark_safe(table_html)})
##################################### JSON ######################################

def upload_json_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('select_json_title_column')
    else:
        form = UploadFileForm()
    return render(request, 'upload_json_file.html', {'form': form})


def select_json_title_column(request):
    try:
        latest_file = UploadedFile.objects.latest('uploaded_at')  # Assuming UploadedFile model exists
        file_path = latest_file.file.path
    except UploadedFile.DoesNotExist:
        return render(request, 'error1.html', {'message': 'No files uploaded yet.'})

    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        df = pd.json_normalize(data)  # Convert JSON to DataFrame
        columns = df.columns.tolist()
    except Exception as e:
        return render(request, 'error1.html', {'message': f'Error reading JSON file: {e}'})

    if request.method == 'POST':
        form = TitleColumnForm(request.POST, columns=columns)
        if form.is_valid():
            title_column = form.cleaned_data['title_column']
            # Assuming title_column is something like 'quiz.sport.q1.answer'
            return redirect('select_json_columns', title_column=title_column)
    else:
        form = TitleColumnForm(columns=columns)

    return render(request, 'select_json_title_column.html', {'form': form})
def select_json_columns(request, title_column):
    try:
        latest_file = UploadedFile.objects.latest('uploaded_at')  # Assuming UploadedFile model exists
        file_path = latest_file.file.path
    except UploadedFile.DoesNotExist:
        return render(request, 'error1.html', {'message': 'No files uploaded yet.'})

    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        df = pd.json_normalize(data)  # Convert JSON to DataFrame
        columns = df.columns.tolist()
        title_values_choices = [(val, val) for val in df[title_column].unique()]
    except Exception as e:
        return render(request, 'error1.html', {'message': f'Error reading JSON file: {e}'})

    if request.method == 'POST':
        form = GraphCSVForm(request.POST, columns=columns, title_values_choices=title_values_choices)
        if form.is_valid():
            x_axis = form.cleaned_data['x_axis']
            y_axis = form.cleaned_data['y_axis']
            graph_type = form.cleaned_data['graph_type']
            title_values = form.cleaned_data['title_values']
            width = form.cleaned_data['width']
            height = form.cleaned_data['height']
            return plot_json_graph(request, file_path, x_axis, y_axis, graph_type, title_column, title_values, width, height,form)
    else:
        form = GraphCSVForm(columns=columns, title_values_choices=title_values_choices)

    return render(request, 'select_json_columns.html', {'form': form})


def plot_json_graph(request, file_path, x_axis, y_axis, graph_type, title_column, title_values, width, height, form=None):
    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            return render(request, 'error1.html', {'message': 'Unsupported file format.'})

        df_filtered = df[df[title_column].isin(title_values)]
    except Exception as e:
        return render(request, 'error1.html', {'message': f'Error reading file: {e}'})

    title = ', '.join(title_values)

    # Create traces based on the graph type
    traces = []
    try:
        if graph_type == 'line':
            for col in y_axis:
                traces.append(go.Scatter(x=df_filtered[x_axis], y=df_filtered[col], mode='lines', name=col))
        elif graph_type == 'bar':
            for col in y_axis:
                traces.append(go.Bar(x=df_filtered[x_axis], y=df_filtered[col], name=col))
        elif graph_type == 'pie':
            if len(y_axis) != 1:
                return render(request, 'error1.html', {'message': 'Pie chart requires exactly one y-axis column.'})
            traces.append(go.Pie(labels=df_filtered[x_axis], values=df_filtered[y_axis[0]]))
        else:
            return render(request, 'error1.html', {'message': 'Unsupported graph type.'})
    except Exception as e:
        return render(request, 'error1.html', {'message': f'Error creating graph: {e}'})

    # Layout configuration
    layout = go.Layout(title=title, xaxis=dict(title=x_axis), yaxis=dict(title=', '.join(y_axis)),
                       width=width, height=height)

    fig = go.Figure(data=traces, layout=layout)
    plot_div = fig.to_html(full_html=False)

    # Create HTML for the table
    table_html = df_filtered[[x_axis] + y_axis].to_html(classes='table', index=False)

    if form is None:
        form = GraphCSVForm(columns=df.columns.tolist(), title_values_choices=[(val, val) for val in df[title_column].unique()])

    return render(request, 'plot_csv_new.html', {'plot_div': plot_div, 'form': form, 'title_column': title_column, 'table_html': mark_safe(table_html)})