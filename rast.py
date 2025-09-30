import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import folium
from geopy.geocoders import Nominatim
import requests
from datetime import datetime

class PhoneTracker:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="phone_tracker")
    
    def parse_number(self, phone_number, country_code=None):
        """Parsea y valida el número telefónico"""
        try:
            if country_code:
                parsed_number = phonenumbers.parse(phone_number, country_code)
            else:
                parsed_number = phonenumbers.parse(phone_number, None)
            
            if phonenumbers.is_valid_number(parsed_number):
                return parsed_number
            else:
                raise ValueError("Número telefónico inválido")
        except Exception as e:
            raise ValueError(f"Error al parsear el número: {str(e)}")
    
    def get_basic_info(self, parsed_number):
        """Obtiene información básica del número"""
        info = {
            'numero_internacional': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            'numero_nacional': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL),
            'numero_e164': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
            'codigo_pais': f"+{parsed_number.country_code}",
            'es_valido': phonenumbers.is_valid_number(parsed_number),
            'es_posible': phonenumbers.is_possible_number(parsed_number)
        }
        return info
    
    def get_location_info(self, parsed_number):
        """Obtiene información de ubicación del número"""
        try:
            # Ubicación geográfica
            location = geocoder.description_for_number(parsed_number, "es")
            
            # Operador
            carrier_name = carrier.name_for_number(parsed_number, "es")
            
            # Zona horaria
            timezones = timezone.time_zones_for_number(parsed_number)
            
            location_info = {
                'ubicacion': location or "No disponible",
                'operador': carrier_name or "No disponible",
                'zonas_horarias': list(timezones) if timezones else ["No disponible"]
            }
            
            return location_info
        except Exception as e:
            return {'error': f"Error obteniendo ubicación: {str(e)}"}
    
    def get_coordinates(self, location_name):
        """Obtiene coordenadas aproximadas basadas en la ubicación"""
        try:
            if location_name and location_name != "No disponible":
                location = self.geolocator.geocode(location_name)
                if location:
                    return {
                        'latitud': location.latitude,
                        'longitud': location.longitude,
                        'direccion_completa': location.address
                    }
            return None
        except Exception as e:
            print(f"Error obteniendo coordenadas: {str(e)}")
            return None
    
    def generate_map(self, coordinates, location_name, phone_number):
        """Genera un mapa con la ubicación aproximada"""
        if coordinates:
            # Crear mapa centrado en las coordenadas
            m = folium.Map(
                location=[coordinates['latitud'], coordinates['longitud']], 
                zoom_start=10
            )
            
            # Agregar marcador
            folium.Marker(
                [coordinates['latitud'], coordinates['longitud']],
                popup=f"Ubicación aproximada de {phone_number}\n{location_name}",
                tooltip=location_name,
                icon=folium.Icon(color='red', icon='phone', prefix='fa')
            ).add_to(m)
            
            # Agregar círculo de área aproximada
            folium.Circle(
                location=[coordinates['latitud'], coordinates['longitud']],
                radius=50000,  # 50km de radio
                popup="Área aproximada",
                color='blue',
                fill=True,
                opacity=0.3
            ).add_to(m)
            
            return m
        return None
    
    def generate_report(self, phone_number, country_code=None):
        """Genera un informe completo del número telefónico"""
        try:
            print("="*60)
            print("INFORME DE LOCALIZACIÓN TELEFÓNICA")
            print("="*60)
            print(f"Fecha del análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Número analizado: {phone_number}")
            print("-"*60)
            
            # Parsear número
            parsed_number = self.parse_number(phone_number, country_code)
            
            # Información básica
            basic_info = self.get_basic_info(parsed_number)
            print("\n📱 INFORMACIÓN BÁSICA:")
            for key, value in basic_info.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            
            # Información de ubicación
            location_info = self.get_location_info(parsed_number)
            print("\n🌍 INFORMACIÓN DE UBICACIÓN:")
            for key, value in location_info.items():
                if key != 'error':
                    print(f"  {key.replace('_', ' ').title()}: {value}")
            
            # Obtener coordenadas
            coordinates = self.get_coordinates(location_info.get('ubicacion'))
            if coordinates:
                print("\n📍 COORDENADAS APROXIMADAS:")
                print(f"  Latitud: {coordinates['latitud']}")
                print(f"  Longitud: {coordinates['longitud']}")
                print(f"  Dirección: {coordinates['direccion_completa']}")
                
                # Generar mapa
                map_obj = self.generate_map(coordinates, location_info.get('ubicacion'), phone_number)
                if map_obj:
                    map_filename = f"ubicacion_{phone_number.replace('+', '').replace(' ', '')}.html"
                    map_obj.save(map_filename)
                    print(f"\n🗺️  Mapa guardado como: {map_filename}")
            
            print("\n" + "="*60)
            print("⚠️  AVISO LEGAL:")
            print("Esta información es solo para propósitos educativos y legítimos.")
            print("El rastreo de números sin consentimiento puede ser ilegal.")
            print("="*60)
            
            return {
                'basic_info': basic_info,
                'location_info': location_info,
                'coordinates': coordinates,
                'status': 'success'
            }
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {'status': 'error', 'message': str(e)}

def main():
    """Función principal para ejecutar el programa"""
    tracker = PhoneTracker()
    
    print("🔍 LOCALIZADOR DE NÚMEROS TELEFÓNICOS")
    print("-" * 40)
    
    # Solicitar número al usuario
    phone_number = input("Ingresa el número telefónico (con código de país): ")
    country_code = input("Código de país (opcional, ej: MX, US, ES): ").upper() or None
    
    # Generar informe
    result = tracker.generate_report(phone_number, country_code)
    
    if result['status'] == 'success':
        print("\n✅ Análisis completado exitosamente")
    else:
        print(f"\n❌ Error en el análisis: {result['message']}")

# Función para buscar múltiples números
def batch_analysis():
    """Analiza múltiples números desde una lista"""
    tracker = PhoneTracker()
    
    numbers = [
        "+52 55 1234 5678",  # México
        "+1 555 123 4567",   # Estados Unidos
        "+34 912 345 678"    # España
    ]
    
    print("📊 ANÁLISIS EN LOTE")
    print("="*50)
    
    for number in numbers:
        print(f"\nAnalizando: {number}")
        result = tracker.generate_report(number)
        print("-" * 30)

if __name__ == "__main__":
    # Instalar dependencias necesarias
    required_packages = """
    Para usar este código, instala las siguientes librerías:
    
    pip install phonenumbers
    pip install folium
    pip install geopy
    pip install requests
    """
    
    print(required_packages)
    print("\n" + "="*60)
    
    # Ejecutar programa principal
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa terminado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")