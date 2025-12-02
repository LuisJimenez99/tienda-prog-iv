from django.template import Template, Context
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from pynliner import Pynliner
from configuracion.models import EmailConfig, AparienciaConfig, DatosPago

def enviar_email_dinamico(tipo, pedido, request=None, codigo_seguimiento=None):
    """
    Busca la configuración del email en la BDD, renderiza las variables
    y envía el correo usando la plantilla base.
    """
    try:
        # 1. Buscar la configuración en la base de datos
        email_config = EmailConfig.objects.get(tipo=tipo)
        apariencia = AparienciaConfig.objects.first()
        datos_pago = DatosPago.objects.first()
        cliente = pedido.cliente

        # 2. Preparar el contexto (las variables disponibles para usar)
        context_data = {
            'pedido': pedido,
            'cliente': cliente,
            'datos_pago': datos_pago,
            'apariencia_config': apariencia,
            'codigo_seguimiento': codigo_seguimiento
        }
        
        # 3. Renderizar el ASUNTO (por si pusieron variables en el asunto)
        asunto_template = Template(email_config.asunto)
        asunto_renderizado = asunto_template.render(Context(context_data))

        # 4. Renderizar el CONTENIDO (el cuerpo del mensaje de la BDD)
        contenido_template = Template(email_config.contenido)
        contenido_renderizado = contenido_template.render(Context(context_data))

        # 5. Inyectar ese contenido en nuestra plantilla BASE (email_base.html)
        #    Para esto, pasamos 'contenido_dinamico' al template base.
        context_data['contenido_dinamico'] = contenido_renderizado
        
        # Usamos un template intermedio simple que extienda de email_base
        # y muestre {{ contenido_dinamico|safe }}
        html_final = render_to_string('carrito/email/email_generico.html', context_data)

        # 6. Inline CSS (Pynliner)
        p = Pynliner()
        html_inlined = p.from_string(html_final).run()

        # 7. Enviar
        send_mail(
            asunto_renderizado,
            strip_tags(html_final), # Versión texto plano automática
            settings.DEFAULT_FROM_EMAIL,
            [cliente.email],
            html_message=html_inlined
        )
        return True

    except EmailConfig.DoesNotExist:
        print(f"⚠️ ADVERTENCIA: No existe configuración de email para '{tipo}'. No se envió nada.")
        return False
    except Exception as e:
        print(f"❌ ERROR enviando email dinámico: {e}")
        return False

# Pequeña utilidad para limpiar HTML para la versión texto plano
from django.utils.html import strip_tags