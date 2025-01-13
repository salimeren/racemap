import socket
import json
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from . import tcp_client
from django.http import JsonResponse
from repo import Repo


@csrf_exempt
def logout(request):
    if 'username' in request.session:
        del request.session['username']

    request.session["map_id"] = None
    request.session["username"] = None
    request.session.modified = True
    return redirect('home')


def home(request):
    username = request.session.get('username', None)

    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            request.session['username'] = username
            request.session.modified = True

    options = {
        "friction": "Friction cell slows the car down",
        "Booster": "Booster cell increases speed.",
        "Rock": "Stops the car",
        "Slippery": "Changes the angle",
        "turn90": "Rotates the car",
        "straight": "Goes straight",
        "fuel": "Fuel cell to refuel the cars",
        "Ferrari": "A sports car",
        "Merso": "A sports car"
    }

    context = {
        'username_submitted': username is not None,
        'username': username,
        'options': options
    }

    return render(request, 'maps/base.html', context)


def create_map(request):
    username = request.session.get('username', None)

    if not username:
        return redirect('home')

    options = {
        "friction": "Friction cell slows the car down",
        "Booster": "Booster cell increases speed.",
        "Rock": "Stops the car",
        "Slippery": "Changes the angle",
        "turn90": "Rotates the car",
        "straight": "Goes straight",
        "fuel": "Fuel cell to refuel the cars",
        "Ferrari": "A sports car",
        "Merso": "A sports car"
    }

    context = {
        'username_submitted': username is not None,
        'username': username,
        'options': options,
    }

    if request.method == 'POST':
        map_id = request.POST.get('map_id')
        cols = request.POST.get('cols')
        rows = request.POST.get('rows')
        cellsize = request.POST.get('cellsize')
        bgcolor = request.POST.get('bgcolor')

        response = tcp_client.send_to_server(username, 'create_map', map_id, cols, rows, cellsize, bgcolor)
        response_data = json.loads(response)

        if request.POST['action'] == 'attach_map':
            attach_response = tcp_client.send_to_server(username, 'attach', map_id)
            attach_data = json.loads(attach_response)

            if attach_data.get('status') == 'success':
                request.session["map_id"] = map_id
                context['map_id'] = map_id

        context['message'] = response_data.get('message', f'Map {map_id} created successfully.')

    return render(request, 'maps/create_map_form.html', context)


def view_map(request):
    svg_mapping = {
        "ferrari": "maps/images/car_topview.svg",
        "rock": "maps/images/rock.svg",
        "booster": "maps/images/booster.svg",
        "checkpoint": "maps/images/checkpoint.svg",
        "friction": "maps/images/friction.svg",
        "slippery": "maps/images/slippery.svg",
        "turn": "maps/images/turn90.svg",
        "straight": "maps/images/straight.svg",
        "fuel": "maps/images/fuel.svg",
        "merso": "maps/images/merso.svg",
    }

    username = request.session.get('username', None)
    map_id = request.session.get('map_id', None)

    response = tcp_client.send_to_server(username, 'attach', map_id)
    response_data = json.loads(response)

    if response_data.get('status') == 'error':
        return render(request, 'maps/view_map.html', {
            'username_submitted': username is not None,
            "username": username,
            "map_id": map_id,
            "error": response_data.get('message', "Error attaching to map")
        })

    size_response = tcp_client.send_to_server(username, "map_size", map_id)
    size_data = json.loads(size_response)

    if size_data.get('status') == 'success':
        size_info = size_data.get('data', {})
        rows = size_info.get('rows', 0)
        cols = size_info.get('cols', 0)
        bgcolor = size_info.get('bgcolor', '#FFFFFF')

        grid = [[None for j in range(cols)] for i in range(rows)]

        components = response_data.get('components', {})
        for comp_id, comp_info in components.items():
            row = int(comp_info[0])
            col = int(comp_info[1])
            rotation = comp_info[2] * 90
            comp_type = comp_info[3].lower()

            if comp_type in svg_mapping:
                grid[row][col] = (svg_mapping[comp_type], rotation)

        return render(request, 'maps/view_map.html', {
            'username_submitted': username is not None,
            "username": username,
            "map_id": map_id,
            'grid': grid,
            "color": bgcolor,
        })

    return render(request, 'maps/view_map.html', {
        'username_submitted': username is not None,
        "username": username,
        "map_id": map_id,
        "error": "Error getting map size"
    })


def list_maps(request):
    username = request.session.get('username', None)
    response = tcp_client.send_to_server(username, "list_maps")
    response_data = json.loads(response)

    context = {
        'username_submitted': username is not None,
        'username': username,
        "map_list": response_data.get('maps', [])
    }

    if request.method == 'POST':
        selected_maps = request.POST.getlist('selected_map')

        if selected_maps:
            map_id = selected_maps[0]
            attach_response = tcp_client.send_to_server(username, "attach", map_id)
            attach_data = json.loads(attach_response)

            if attach_data.get('status') == 'success':
                request.session["map_id"] = map_id
                context["success_message"] = attach_data.get('message', f"Map {map_id} attached")
            else:
                context["error_message"] = attach_data.get('message', "Error attaching to map")

    return render(request, 'maps/list_maps.html', context)


def create_component(request):
    username = request.session.get('username', None)
    map_id = request.session.get('map_id', None)

    if not username:
        return redirect('home')

    options = {
        "friction": "Friction cell slows the car down",
        "booster": "Booster cell increases speed.",
        "rock": "Stops the car",
        "slippery": "Changes the angle",
        "turn90": "Rotates the car",
        "straight": "Goes straight",
        "fuel": "Fuel cell to refuel the cars",
        "Ferrari": "A sports car",
        "Merso": "A sports car"
    }

    context = {
        'username_submitted': username is not None,
        'username': username,
        'options': options,
        'map_id': map_id
    }

    if request.method == 'POST':
        selected_option = request.POST.get('option')
        rows = request.POST.get('rows')
        cols = request.POST.get('cols')

        if selected_option and rows and cols:
            response = tcp_client.send_component_to_server(username, map_id, selected_option, rows, cols)
            response_data = json.loads(response)

            if response_data.get('status') == 'error':
                context['error'] = response_data.get('message', "Error creating component")
            else:
                context['response'] = response_data.get('message', "Component created successfully")

    return render(request, 'maps/create_component.html', context)


def delete_component(request):
    username = request.session.get('username', None)
    map_id = request.session.get('map_id', None)

    if not username:
        return redirect('home')

    context = {
        'username_submitted': username is not None,
        'username': username,
        'map_id': map_id,
    }

    if request.method == 'POST':
        component_id = request.POST.get('component_id')

        if component_id:
            response = tcp_client.send_delete_to_server(username, map_id, 'delete', 'component', component_id)
            response_data = json.loads(response)
            context['response'] = response_data.get('message', "Component deleted")

    return render(request, 'maps/delete_component.html', context)


def rotate_component(request):
    username = request.session.get('username', None)
    map_id = request.session.get('map_id', None)

    if not username:
        return redirect('home')

    context = {
        'username_submitted': username is not None,
        'username': username,
        'map_id': map_id,
    }

    if request.method == 'POST':
        component_id = request.POST.get('component_id')

        if component_id:
            response = tcp_client.send_rotate_to_server(username, map_id, 'rotate', component_id)
            response_data = json.loads(response)
            context['response'] = response_data.get('message', "Component rotated")

    return render(request, 'maps/rotate_component.html', context)


def save_repo(request):
    username = request.session.get('username', None)
    map_id = request.session.get('map_id', None)

    if not username:
        return redirect('home')

    context = {
        'username_submitted': username is not None,
        'username': username,
        'map_id': map_id,
    }

    if request.method == 'POST':
        response = tcp_client.send_save_to_server(username, map_id, 'save')
        response_data = json.loads(response)
        context['response'] = response_data.get('message', "Repository saved")

    return render(request, 'maps/save_repo.html', context)