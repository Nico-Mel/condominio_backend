from django.core.management.base import BaseCommand
from django.utils import timezone
from condominio.models import Residencia

class Command(BaseCommand):
    help = 'Genera cuotas de alquiler para el mes actual para todas las residencias activas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--mes',
            type=str,
            help='Mes específico en formato YYYY-MM (ej: 2025-10)',
        )
    
    def handle(self, *args, **options):
        # Obtener mes objetivo
        mes_objetivo = options['mes'] or timezone.now().strftime('%Y-%m')
        
        self.stdout.write(f"🔍 Buscando residencias de alquiler activas para {mes_objetivo}...")
        
        # Buscar residencias de alquiler activas
        residencias = Residencia.objects.filter(
            tipo_contrato='alquiler',
            esta_activa=True
        )
        
        cuotas_generadas = 0
        errores = []
        
        for residencia in residencias:
            try:
                # Verificar si debe generar alquiler para este mes
                if residencia.debe_generar_alquiler(mes_objetivo):
                    detalle = residencia.generar_cuota_alquiler_actual(mes_objetivo)
                    if detalle:
                        cuotas_generadas += 1
                        self.stdout.write(
                            self.style.SUCCESS(f" Generada cuota para {residencia} - ${detalle.monto}")
                        )
                    else:
                        errores.append(f"Error generando cuota para {residencia}")
                else:
                    self.stdout.write(
                        f"⏭  {residencia} ya tiene cuota o contrato no vigente"
                    )
                    
            except Exception as e:
                errores.append(f"ERROR en {residencia}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f" Error en {residencia}: {str(e)}")
                )
        
        # Reporte final
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(
            f" Proceso completado para {mes_objetivo}"
        ))
        self.stdout.write(f" Total residencias procesadas: {residencias.count()}")
        self.stdout.write(f" Cuotas generadas: {cuotas_generadas}")
        self.stdout.write(f" Errores: {len(errores)}")
        
        if errores:
            self.stdout.write(self.style.ERROR("Detalles de errores:"))
            for error in errores:
                self.stdout.write(f"  - {error}")