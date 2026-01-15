import requests
import json
from datetime import datetime, timedelta
import os

class CurrencyConverter:
    def __init__(self, app):
        self.app = app
        self.rates = {}
        self.last_update = None
        self.cache_file = "exchange_rates.json"
        self.load_rates()
    
    def load_rates(self):
        """Carga las tasas de cambio del archivo de caché"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    data = json.load(f)
                    self.rates = data.get("rates", {})
                    self.last_update = datetime.fromisoformat(data.get("last_update", "2000-01-01"))
                    
                    # Verificar si las tasas son antiguas (más de 1 día)
                    if datetime.now() - self.last_update > timedelta(days=1):
                        self.fetch_latest_rates()
            else:
                self.fetch_latest_rates()
        except Exception as e:
            print(f"Error cargando tasas: {e}")
            self.fetch_latest_rates()
    
    def fetch_latest_rates(self):
        """Obtiene las tasas de cambio más recientes de una API gratuita"""
        try:
            # API de ExchangeRate-API (gratuita, no requiere clave para el plan básico)
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # SOLO GUARDAR LAS MONEDAS QUE NECESITAMOS
                all_rates = data.get("rates", {})
                self.rates = {
                    "USD": 1.0,
                    "ARS": all_rates.get("ARS", 950.0),
                    "EUR": all_rates.get("EUR", 0.92)
                }
                self.last_update = datetime.now()
                
                # Guardar en caché
                cache_data = {
                    "rates": self.rates,
                    "last_update": self.last_update.isoformat()
                }
                with open(self.cache_file, "w") as f:
                    json.dump(cache_data, f, indent=2)
                
                return True
            else:
                # Si falla la API principal, usar tasas de respaldo
                self.use_backup_rates()
                return False
                
        except Exception as e:
            print(f"Error obteniendo tasas: {e}")
            self.use_backup_rates()
            return False
    
    def use_backup_rates(self):
        """Usa tasas de cambio de respaldo si la API falla"""
        # SOLO LAS 3 MONEDAS QUE NECESITAMOS
        self.rates = {
            "USD": 1.0,
            "ARS": 950.0,  # Dólar oficial aproximado
            "EUR": 0.92
        }
        self.last_update = datetime.now()
    
    def convert(self, amount, from_currency, to_currency):
        """Convierte una cantidad de una moneda a otra"""
        if from_currency == to_currency:
            return amount
        
        if from_currency not in self.rates or to_currency not in self.rates:
            return amount  # No se puede convertir, devolver la cantidad original
        
        # Convertir a USD primero (si no es USD)
        if from_currency != "USD":
            amount_in_usd = amount / self.rates[from_currency]
        else:
            amount_in_usd = amount
        
        # Convertir de USD a la moneda destino
        if to_currency != "USD":
            return amount_in_usd * self.rates[to_currency]
        else:
            return amount_in_usd
    
    def get_all_currencies(self):
        """Devuelve todas las monedas disponibles"""
        # SOLO LAS 3 QUE QUERÉS
        return ["USD", "ARS", "EUR"]
    
    def get_rate(self, from_currency, to_currency):
        """Obtiene la tasa de cambio entre dos monedas"""
        if from_currency == to_currency:
            return 1.0
        
        if from_currency not in self.rates or to_currency not in self.rates:
            return None
        
        return self.rates[to_currency] / self.rates[from_currency]
