from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.conf import settings
from .models import PersonalSoporte, Empresa, Bitacora, Destinatario
import datetime
import json
import requests
from bs4 import BeautifulSoup

def index(request):
    bitacora, created = Bitacora.objects.get_or_create(id=1)
    return render(request, 'dashboard/index.html', {
        'bitacora': bitacora
    })

def index_antiguo(request):
    """
    Renderiza el dashboard antiguo con la vista original.
    """
    bitacora, created = Bitacora.objects.get_or_create(id=1)
    return render(request, 'dashboard/index_antiguo.html', {
        'bitacora': bitacora
    })

def pizarra_embed(request):
    bitacora, created = Bitacora.objects.get_or_create(id=1)
    return render(request, 'dashboard/pizarra_embed.html', {
        'bitacora': bitacora
    })

def dashboard_general_embed(request):
    bitacora, created = Bitacora.objects.get_or_create(id=1)
    return render(request, 'dashboard/dashboard_general_embed.html', {
        'bitacora': bitacora
    })

def planillas_embed(request):
    return render(request, 'dashboard/planillas_embed.html')

def actualizar_bitacora(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bitacora, _ = Bitacora.objects.get_or_create(id=1)
            bitacora.texto = data.get('texto', '')
            bitacora.save()
            return JsonResponse({'status': 'ok', 'actualizado_en': bitacora.actualizado_en.strftime('%d/%m/%Y %H:%M')})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    elif request.method == 'GET':
        bitacora, _ = Bitacora.objects.get_or_create(id=1)
        return JsonResponse({'status': 'ok', 'texto': bitacora.texto, 'actualizado_en': bitacora.actualizado_en.strftime('%d/%m/%Y %H:%M')})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def buscar_wiki(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    url = f"https://intranet.innovex.cl/operaciones/search?q={query}&wiki=on"
    auth = (settings.TRAC_USER, settings.TRAC_PASSWORD)
    
    try:
        response = requests.get(url, auth=auth, timeout=5, verify=False)
        if response.status_code == 401:
            return JsonResponse({'error': 'Error 401: Credenciales de Trac incorrectas en el archivo .env'}, status=401)
        elif response.status_code != 200:
            return JsonResponse({'error': f'Error {response.status_code} al conectar con Trac'}, status=response.status_code)
            
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        dl = soup.find('dl', id='results')
        if dl:
            for dt, dd in zip(dl.find_all('dt'), dl.find_all('dd')):
                a_tag = dt.find('a')
                if a_tag:
                    title = a_tag.text.strip()
                    href = a_tag.get('href', '')
                    if href.startswith('/'):
                        link = f"https://intranet.innovex.cl{href}"
                    else:
                        link = href
                    snippet = dd.text.strip()
                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })
        return JsonResponse({'results': results})
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Error: Tiempo de espera agotado al conectar con Trac (Timeout).'}, status=504)
    except requests.exceptions.ConnectionError:
        return JsonResponse({'error': 'Error: No se pudo establecer conexión con intranet.innovex.cl. Verifica la VPN o red.'}, status=502)
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)

from collections import defaultdict

def trac_wiki(request):
    auth = (settings.TRAC_USER, settings.TRAC_PASSWORD)
    index_url = "https://intranet.innovex.cl/operaciones/wiki/TitleIndex"
    indice_agrupado = defaultdict(list)
    error_msg = None

    try:
        response = requests.get(index_url, auth=auth, timeout=5, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            content_div = soup.find('div', id='content')
            if content_div:
                for a_tag in content_div.find_all('a'):
                    href = a_tag.get('href', '')
                    text = a_tag.text.strip()
                    if href.startswith('/operaciones/wiki/') and text and not text.startswith('TitleIndex'):
                        if '/' in text:
                            grupo = text.split('/')[0]
                            display_text = text.split('/', 1)[1]
                        else:
                            grupo = text[0].upper() if text else '#'
                            display_text = text
                            
                        indice_agrupado[grupo].append({
                            'titulo': display_text,
                            'url': f"https://intranet.innovex.cl{href}"
                        })
        elif response.status_code == 401:
            error_msg = "Error 401: Credenciales incorrectas. Verifica el archivo .env."
        else:
            error_msg = f"Error {response.status_code} al cargar el índice."
    except Exception as e:
        error_msg = f"No se pudo cargar el índice de Trac: {str(e)}"

    # Sort groups alphabetically
    sorted_indice = dict(sorted(indice_agrupado.items()))

    return render(request, 'dashboard/trac_wiki.html', {
        'indice_agrupado': sorted_indice,
        'error_msg': error_msg
    })

def correos_masivos(request):
    if request.method == 'POST':
        semana = request.POST.get('semana')
        fecha_sabado = request.POST.get('fecha_sabado')
        fecha_domingo = request.POST.get('fecha_domingo')
        
        try:
            fs = datetime.datetime.strptime(fecha_sabado, '%Y-%m-%d')
            fecha_sabado = fs.strftime('%d/%m')
        except ValueError:
            pass
            
        try:
            fd = datetime.datetime.strptime(fecha_domingo, '%Y-%m-%d')
            fecha_domingo = fd.strftime('%d/%m')
        except ValueError:
            pass

        personal_id = request.POST.get('personal_id')
        
        try:
            personal = PersonalSoporte.objects.get(id=personal_id)
        except PersonalSoporte.DoesNotExist:
            messages.error(request, 'El personal seleccionado no existe.')
            return redirect('correos_masivos')

        correo_prueba = request.POST.get('correo_prueba', '').strip()
        if correo_prueba:
            class DummyDestinatario:
                def __init__(self, correo):
                    self.correo = correo
            
            class DummyManager:
                def __init__(self, correos_str):
                    self.correos = [c.strip() for c in correos_str.replace(';', ',').split(',') if c.strip()]
                def filter(self, **kwargs):
                    return [DummyDestinatario(c) for c in self.correos]

            class DummyEmpresa:
                nombre = "Prueba"
                def __init__(self, correos_str):
                    self.destinatarios = DummyManager(correos_str)
                    
            empresas_activas = [DummyEmpresa(correo_prueba)]
            cc_list = []
        else:
            empresas_activas = Empresa.objects.filter(activa=True)
            cc_list = ['soporte@innovex.cl', 'jefe.area@innovex.cl']
            
        subject = f"ASISTENCIA SOPORTE INNOVEX FIN DE SEMANA - SEMANA {semana}"
        
        emails_enviados = 0
        for i, empresa in enumerate(empresas_activas):
            html_content = render_to_string('emails/turno_fin_semana.html', {
                'fecha_sabado': fecha_sabado,
                'fecha_domingo': fecha_domingo,
                'personal': personal,
                'cargo_calculado': personal.cargo_calculado,
            })
            text_content = strip_tags(html_content)
            
            # Save the first generated email to an HTML file for testing
            if i == 0:
                with open('test_correo_generado.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            nombre_parts = personal.nombre.lower().split()
            if len(nombre_parts) >= 2:
                correo_remitente = f"{nombre_parts[0]}.{nombre_parts[1]}@innovex.cl"
            else:
                correo_remitente = f"{nombre_parts[0]}@innovex.cl"
            
            # Fetch individual emails for this company
            dest_objs = empresa.destinatarios.filter(activo=True)
            destinatarios = [d.correo.strip() for d in dest_objs if d.correo.strip()]
            if not destinatarios:
                continue

            # Use EmailMultiAlternatives for HTML emails
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=correo_remitente,
                to=destinatarios,
                cc=cc_list,
                reply_to=[correo_remitente],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            emails_enviados += 1
            
        messages.success(request, f'Se enviaron correos masivos a {emails_enviados} empresas agrupadas. Puedes previsualizar el HTML generado en el archivo "test_correo_generado.html".')
        return redirect('correos_masivos')

    # GET request: load personal list
    personal_list = PersonalSoporte.objects.all()
    current_week = datetime.date.today().isocalendar()[1]
    return render(request, 'dashboard/correos_masivos.html', {
        'personal_list': personal_list,
        'current_week': current_week
    })

def gestionar_correos(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'toggle_destinatario':
                dest_id = data.get('id')
                activo = data.get('activo')
                dest = Destinatario.objects.get(id=dest_id)
                dest.activo = activo
                dest.save()
                return JsonResponse({'status': 'ok'})
                
            elif action == 'create':
                empresa_nombre = data.get('empresa').strip()
                correo = data.get('correo').strip()
                
                empresa, _ = Empresa.objects.get_or_create(nombre=empresa_nombre)
                Destinatario.objects.create(correo=correo, empresa=empresa, activo=True)
                return JsonResponse({'status': 'ok'})
                
            elif action == 'delete_destinatario':
                dest_id = data.get('id')
                Destinatario.objects.filter(id=dest_id).delete()
                return JsonResponse({'status': 'ok'})
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    destinatarios = Destinatario.objects.select_related('empresa').all().order_by('empresa__nombre', 'correo')
    empresas = Empresa.objects.all().order_by('nombre')
    return render(request, 'dashboard/gestionar_correos.html', {'destinatarios': destinatarios, 'empresas': empresas})

def certificados(request):
    return render(request, 'dashboard/certificados.html')

def calendario(request):
    return render(request, 'dashboard/calendario.html')

import os
import subprocess

def get_dbus_env():
    uid = os.getuid()
    env = os.environ.copy()
    if 'DBUS_SESSION_BUS_ADDRESS' not in env:
        env['DBUS_SESSION_BUS_ADDRESS'] = f'unix:path=/run/user/{uid}/bus'
    if 'DISPLAY' not in env:
        env['DISPLAY'] = ':0'
    if 'XDG_RUNTIME_DIR' not in env:
        env['XDG_RUNTIME_DIR'] = f'/run/user/{uid}'
    # Ensure /usr/local/bin is in PATH for yt-dlp
    if '/usr/local/bin' not in env.get('PATH', ''):
        env['PATH'] = f"/usr/local/bin:{env.get('PATH', '')}"
    return env

def music_control(request):
    action = request.GET.get('action')
    query = request.GET.get('query', '')
    commands = {
        'volup': ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+5%'],
        'voldn': ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '-5%'],
        'mute': ['pactl', 'set-sink-mute', '@DEFAULT_SINK@', 'toggle'],
        'play': ['playerctl', 'play-pause'],
        'next': ['playerctl', 'next'],
        'prev': ['playerctl', 'previous']
    }
    
    env = get_dbus_env()

    if action == 'search' and query:
        try:
            import shlex
            
            # Stop any existing background music first
            subprocess.run(['pkill', '-f', 'mpv --no-video'], env=env)
            subprocess.run(['pkill', '-f', 'yt-dlp'], env=env)
            
            # Bypass the mpv 403 error by using yt-dlp to download and pipe directly to mpv.
            # We use force-media-title so the Dashboard UI (playerctl) shows what is playing.
            safe_query = shlex.quote(f"ytsearch1:{query}")
            safe_title = shlex.quote(query.title())
            
            command = f"/usr/local/bin/yt-dlp --js-runtimes nodejs -q -o - -f bestaudio {safe_query} | mpv --no-video --force-media-title={safe_title} -"
            
            # Guardamos un log para ver si falla por permisos
            with open('mpv_debug.log', 'w') as log_file:
                subprocess.Popen(command, env=env, shell=True, start_new_session=True, stdout=log_file, stderr=subprocess.STDOUT)
            
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    if action in commands:
        try:
            subprocess.run(commands[action], env=env, check=True)
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

def music(request):
    return render(request, 'dashboard/music.html')

def music_status(request):
    env = get_dbus_env()
    
    status_data = {
        'status': 'stopped',
        'title': 'No hay música reproduciéndose',
        'artist': ''
    }
    
    try:
        result = subprocess.run(['playerctl', 'status'], env=env, capture_output=True, text=True)
        if result.returncode == 0:
            status_data['status'] = result.stdout.strip().lower()
            
            title_res = subprocess.run(['playerctl', 'metadata', 'title'], env=env, capture_output=True, text=True)
            if title_res.returncode == 0 and title_res.stdout.strip():
                status_data['title'] = title_res.stdout.strip()
                
            artist_res = subprocess.run(['playerctl', 'metadata', 'artist'], env=env, capture_output=True, text=True)
            if artist_res.returncode == 0 and artist_res.stdout.strip():
                status_data['artist'] = artist_res.stdout.strip()
    except Exception:
        pass
        
    return JsonResponse(status_data)

def poseidon(request):
    return render(request, 'dashboard/poseidon.html')

def api_poseidon_status(request):
    import requests
    sites = {
        'llancacheo': 'http://ce-llancacheo-inyeccion.acuimatic.com:8000/',
        'aulen': 'http://ce-aulen-inyeccion.acuimatic.com:8000/'
    }
    status = {}
    for name, url in sites.items():
        try:
            # Short timeout so it doesn't block long if down
            r = requests.get(url, timeout=3)
            status[name] = r.status_code == 200
        except Exception:
            status[name] = False
    return JsonResponse(status)

def api_poseidon_ping_interno(request):
    import paramiko
    import os
    
    # We define the IPs per the user request
    target_ips = {
        '192.168.1.10': 'PC Inyección',
        '192.168.1.110': 'Ubiquiti Pontón',
        '192.168.1.111': 'Ubiquiti Plataforma',
        '192.168.1.1': 'Router Plataforma',
        'flowpresor_1': 'Flowpresor 1',
        'flowpresor_2': 'Flowpresor 2',
        'oxypresor_1': 'Oxypresor 1',
        'oxypresor_2': 'Oxypresor 2',
    }
    
    # Configurations
    sites = {
        'llancacheo': {
            'host': 'ce-llancacheo-inyeccion.acuimatic.com',
            'user': os.environ.get('LLANCACHEO_SSH_USER', 'root'),
            'pass': os.environ.get('LLANCACHEO_SSH_PASS', '')
        },
        'aulen': {
            'host': 'ce-aulen-inyeccion.acuimatic.com',
            'user': os.environ.get('AULEN_SSH_USER', 'root'),
            'pass': os.environ.get('AULEN_SSH_PASS', '')
        }
    }
    
    results = {}
    
    for site_name, site_config in sites.items():
        site_results = {}
        if not site_config['pass']:
            # If password is not configured, we return error for all
            for ip, name in target_ips.items():
                site_results[name] = {'ip': ip, 'status': 'error', 'msg': 'Falta clave en .env'}
            results[site_name] = site_results
            continue
            
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # We connect with a short timeout to avoid freezing if the main host is down
            ssh.connect(
                hostname=site_config['host'],
                username=site_config['user'],
                password=site_config['pass'],
                timeout=5,
                auth_timeout=5
            )
            
            for ip, name in target_ips.items():
                # Skip placeholders
                if not ip.startswith('192.'):
                    site_results[name] = {'ip': ip, 'status': 'unknown', 'msg': 'Pendiente de definir IP'}
                    continue
                    
                # Execute ping -c 1 -W 2 (1 packet, 2 seconds timeout)
                stdin, stdout, stderr = ssh.exec_command(f"ping -c 1 -W 2 {ip}", timeout=3)
                exit_status = stdout.channel.recv_exit_status()
                
                if exit_status == 0:
                    site_results[name] = {'ip': ip, 'status': 'online', 'msg': 'En línea'}
                else:
                    site_results[name] = {'ip': ip, 'status': 'offline', 'msg': 'Fuera de línea'}
                    
            ssh.close()
        except Exception as e:
            for ip, name in target_ips.items():
                site_results[name] = {'ip': ip, 'status': 'error', 'msg': f'Error SSH: {str(e)[:20]}...'}
                
        results[site_name] = site_results
        
    return JsonResponse(results)
