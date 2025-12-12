from django.urls import path
from . import views

urlpatterns = [
    # 1. Inicio del Panel (Dashboard Resumen)
    path('', views.inicio_panel, name='panel_home'),
    
    # 2. Agenda Profesional
    path('agenda/', views.agenda_panel, name='panel_agenda'),
    path('api/turnos-dia/', views.api_turnos_dia, name='api_turnos_dia'),
    
    # API Gestión Turnos
    path('api/turno/<int:turno_id>/gestion/', views.api_gestion_turno, name='api_gestion_turno'),
    
    # 3. Cocina y Pedidos
    path('cocina/', views.cocina_panel, name='panel_cocina'),
    
    # API Detalle Pedido
    path('api/pedido/<int:pedido_id>/detalle/', views.api_pedido_detalle, name='api_pedido_detalle'),
    
    # Acción para cambiar estado
    path('pedido/<int:pedido_id>/estado/<str:nuevo_estado>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),

    # 4. Gestor de Bloqueos (Horarios/Vacaciones)
    path('bloqueos/', views.bloqueos_panel, name='panel_bloqueos'),
    path('api/regla/<int:regla_id>/toggle/', views.toggle_regla, name='toggle_regla'),
    
    # CRUD Reglas
    path('bloqueos/nuevo/', views.regla_editar, name='regla_nueva'),
    path('bloqueos/editar/<int:regla_id>/', views.regla_editar, name='regla_editar'),
    path('bloqueos/eliminar/<int:regla_id>/', views.regla_eliminar, name='regla_eliminar'),

    # 5. Logística (Envíos)
    path('envios/', views.envios_panel, name='panel_envios'),

    # 6. CRM (Pacientes) y Consultorio
    path('pacientes/', views.pacientes_panel, name='panel_pacientes'),
    
    # Crear nuevo paciente manual
    path('pacientes/nuevo/', views.crear_paciente, name='panel_paciente_nuevo'),
    
    # Ficha del paciente
    path('paciente/<int:user_id>/', views.detalle_paciente, name='panel_detalle_paciente'),
    
    # NUEVA RUTA: Vincular usuario web existente a una ficha clínica nueva
    path('paciente/vincular/<int:user_id>/', views.crear_ficha_desde_usuario, name='panel_crear_ficha_usuario'),
    
    # Nueva Consulta Médica
    path('paciente/ficha/<int:paciente_id>/nueva-consulta/', views.crear_consulta, name='panel_nueva_consulta'),

    # 7. Acciones Rápidas
    path('accion/exportar-comanda/', views.exportar_comanda_cocina, name='exportar_comanda'),

    # 8. Gestión de Inventario
    path('inventario/', views.inventario_panel, name='panel_inventario'),
    path('inventario/nuevo/', views.producto_editar, name='producto_nuevo'),
    path('inventario/editar/<int:producto_id>/', views.producto_editar, name='producto_editar'),
    path('inventario/eliminar/<int:producto_id>/', views.producto_eliminar, name='producto_eliminar'),
]