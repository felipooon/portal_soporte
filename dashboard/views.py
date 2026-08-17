from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import PersonalSoporte, ClienteCentro

def index(request):
    return render(request, 'dashboard/index.html')

def correos_masivos(request):
    if request.method == 'POST':
        semana = request.POST.get('semana')
        fecha_sabado = request.POST.get('fecha_sabado')
        fecha_domingo = request.POST.get('fecha_domingo')
        personal_id = request.POST.get('personal_id')
        
        try:
            personal = PersonalSoporte.objects.get(id=personal_id)
        except PersonalSoporte.DoesNotExist:
            messages.error(request, 'El personal seleccionado no existe.')
            return redirect('correos_masivos')

        correo_prueba = request.POST.get('correo_prueba', '').strip()
        if correo_prueba:
            class DummyCliente:
                correo = correo_prueba
            clientes_activos = [DummyCliente()]
        else:
            clientes_activos = ClienteCentro.objects.filter(activo=True)
            
        subject = f"ASISTENCIA SOPORTE INNOVEX FIN DE SEMANA - SEMANA {semana}"
        
        emails_enviados = 0
        for i, cliente in enumerate(clientes_activos):
            html_content = render_to_string('emails/turno_fin_semana.html', {
                'fecha_sabado': fecha_sabado,
                'fecha_domingo': fecha_domingo,
                'personal': personal,
            })
            text_content = strip_tags(html_content)
            
            # Save the first generated email to an HTML file for testing
            if i == 0:
                with open('test_correo_generado.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            # Use EmailMultiAlternatives for HTML emails
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=personal.correo,
                to=[cliente.correo],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            emails_enviados += 1
            
        messages.success(request, f'Se enviaron {emails_enviados} correos. Puedes previsualizar el HTML generado en el archivo "test_correo_generado.html".')
        return redirect('correos_masivos')

    # GET request: load personal list
    personal_list = PersonalSoporte.objects.all()
    return render(request, 'dashboard/correos_masivos.html', {'personal_list': personal_list})

def certificados(request):
    return render(request, 'dashboard/certificados.html')

def calendario(request):
    return render(request, 'dashboard/calendario.html')


