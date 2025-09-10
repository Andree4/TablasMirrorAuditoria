# Sistema de Auditoría y Encriptación de Base de Datos

## 📋 Autor

Arancibia Aguilar Daniel Andre

Ingeniería en Ciencias de la Computación

## 📋 Descripción General

Este proyecto implementa un sistema avanzado de auditoría y encriptación para bases de datos PostgreSQL. Crea tablas espejo con prefijo `aud_` que almacenan datos encriptados de las tablas originales, manteniendo estas últimas completamente sin modificar.

Utiliza el algoritmo **RSA** para encriptar todos los datos de las columnas, almacenándolos como tipo `BYTEA` en las tablas espejo. Los desencadenadores (triggers) de PostgreSQL copian automáticamente los datos a las tablas `aud_` después de operaciones de inserción o actualización.

Una interfaz web basada en Flask, completamente en español, permite seleccionar tablas para encriptar y visualizar datos, con la opción de desencriptar los datos de las tablas `aud_` usando una clave privada.

## ✨ Características Principales

- 🔐 **Tablas Espejo Encriptadas**: Crea tablas `aud_<nombre_tabla>` con datos encriptados
- 🛡️ **Preservación de Datos Originales**: Las tablas originales permanecen sin modificar
- 🔑 **Encriptación RSA**: Utiliza RSA con padding OAEP y SHA256 para máxima seguridad
- ⚡ **Desencadenadores Automáticos**: Copia automática tras operaciones INSERT/UPDATE
- 🌐 **Interfaz Web en Español**: Gestión completa desde navegador web
- 📊 **Visualización con Desencriptación**: Ver datos encriptados y desencriptados
- 💾 **Copia Inicial de Datos**: Los datos existentes se encriptan automáticamente
- 🏗️ **Diseño Modular**: Código organizado en archivos especializados

## 🛠️ Tecnologías Utilizadas

### Backend

- **Python 3.8+**: Lógica principal de la aplicación
- **PostgreSQL 13+**: Sistema de base de datos
- **Flask**: Interfaz web y servidor HTTP

### Librerías Python

- **`psycopg2-binary`**: Conexión a PostgreSQL
- **`cryptography`**: Implementación de encriptación RSA
- **`flask`**: Framework web

## 📋 Requisitos Previos

- **Python 3.8** o superior
- **PostgreSQL 13** o superior
- Permisos de administrador en PostgreSQL

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/database-encryption-audit.git
cd database-encryption-audit
```

### 2. Instalar dependencias Python

```bash
pip install psycopg2-binary cryptography flask
```

### 3. Configurar PostgreSQL

#### Crear base de datos

```sql
CREATE DATABASE dbpostgrado;
```

#### Crear tablas de ejemplo

```sql
CREATE TABLE extractos_bancarios (
    nombre_completo VARCHAR,
    carnet_identidad VARCHAR,
    numero_codigo VARCHAR,
    monto VARCHAR,
    fecha DATE,
    hora TIME,
    procesando VARCHAR,
    estado VARCHAR
);
```

### 4. Configurar estructura del proyecto

```bash
# Crear directorios necesarios
mkdir keys templates

# Verificar estructura
database-encryption-audit/
├── keys/                    # Claves RSA (se generan automáticamente)
├── templates/
│   └── index.html          # Interfaz web
├── key_generator.py        # Generación de claves RSA
├── crypto_utils.py         # Funciones de encriptación
├── db_utils.py            # Gestión de base de datos
└── app.py                 # Aplicación Flask principal
```

### 5. Configurar credenciales

En `db_utils.py`, verificar las credenciales de conexión:

```python
# Configuración por defecto:
# Usuario: postgres
# Contraseña: 1122ffgg
# Base de datos: dbpostgrado
```

> **⚠️ Importante**: En producción, utilizar variables de entorno para las credenciales.

## 💻 Uso

### 1. Iniciar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: [http://localhost:5000](http://localhost:5000)

### 2. Interfaz Web

#### 🔐 Encriptar una Tabla

1. Ve a la sección **"Encriptar Tabla"**
2. Selecciona una tabla de la lista desplegable
3. Haz clic en **"Encriptar Tabla"**

**Proceso automático:**

- Crea tabla `aud_<nombre_tabla>`
- Copia y encripta datos existentes
- Configura desencadenadores automáticos

#### 📊 Visualizar Datos

1. Ve a la sección **"Ver Datos de la Tabla"**
2. Selecciona una tabla (original o `aud_`)
3. **Para tablas `aud_`**: Introduce la clave privada (`keys/private_key.pem`)
4. Haz clic en **"Cargar Tabla"**

### 3. Gestión de Claves

#### Generación Automática

Las claves RSA se generan automáticamente al primer uso:

- **Clave pública**: `keys/public_key.pem` (para encriptar)
- **Clave privada**: `keys/private_key.pem` (para desencriptar)

#### Usar Clave Privada

Para desencriptar datos en la interfaz web:

1. Abre el archivo `keys/private_key.pem`
2. Copia todo el contenido (incluyendo `-----BEGIN` y `-----END`)
3. Pégalo en el campo "Clave Privada" de la interfaz

## 📁 Estructura y Módulos

### 🔑 `key_generator.py`

- Genera pares de claves RSA (pública/privada)
- Gestiona el almacenamiento seguro de claves
- Formato PEM estándar

### 🔐 `crypto_utils.py`

- Funciones de encriptación RSA con padding OAEP
- Funciones de desencriptación
- Manejo de errores criptográficos

### 🗄️ `db_utils.py`

- Conexión y gestión de PostgreSQL
- Creación de tablas `aud_` automática
- Configuración de triggers (desencadenadores)
- Copia y encriptación de datos existentes

### 🌐 `app.py`

- Aplicación Flask principal
- Rutas y endpoints de la API
- Lógica de la interfaz web

### 🎨 `templates/index.html`

- Interfaz web completa en español
- Formularios para encriptación y visualización
- Diseño responsive y amigable

## 🔧 Funcionamiento Técnico

### Proceso de Encriptación

1. **Selección de tabla** → Interface web
2. **Creación tabla espejo** → `CREATE TABLE aud_<nombre>`
3. **Encriptación datos existentes** → RSA con clave pública
4. **Inserción datos encriptados** → Tabla `aud_`
5. **Creación trigger** → Automático para futuras operaciones

### Desencadenadores (Triggers)

```sql
-- Se crea automáticamente para cada tabla encriptada
CREATE OR REPLACE FUNCTION copy_to_aud_<tabla>()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO aud_<tabla> VALUES (NEW.*);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Tipos de Datos

- **Tablas originales**: Tipos de datos originales
- **Tablas `aud_`**: Todas las columnas como `BYTEA` (datos binarios encriptados)

## ⚠️ Limitaciones y Consideraciones

### 🔄 Encriptación en Triggers

- Los triggers actuales copian datos **sin encriptar directamente**
- Para encriptación en tiempo real, instalar PL/Python:
  ```sql
  CREATE EXTENSION plpython3u;
  ```

### 🔐 Gestión de Claves

- Las claves se almacenan en archivos locales (`keys/`)
- **No recomendado para producción**
- Usar servicios de gestión de claves en entornos reales

### ⚡ Rendimiento

- La encriptación RSA puede ser **lenta para tablas grandes**
- Considerar algoritmos más rápidos para grandes volúmenes
- Implementar encriptación por lotes si es necesario

### 🛡️ Seguridad

- **Backup de claves**: Fundamental para recuperar datos
- **Acceso controlado**: Restringir acceso a claves privadas
- **Rotación de claves**: Implementar en entornos críticos

## 🧪 Pruebas y Verificación

### 1. Verificar Conexión a Base de Datos

```bash
python -c "from db_utils import get_connection; print('✅ Conexión exitosa' if get_connection() else '❌ Error de conexión')"
```

### 2. Probar Encriptación/Desencriptación

```python
from crypto_utils import encrypt_data, decrypt_data
from key_generator import generate_keys, load_keys

# Generar claves si no existen
generate_keys()
public_key, private_key = load_keys()

# Probar encriptación
data = "Datos de prueba"
encrypted = encrypt_data(data, public_key)
decrypted = decrypt_data(encrypted, private_key)

print(f"Original: {data}")
print(f"Desencriptado: {decrypted}")
print("✅ Encriptación funcionando" if data == decrypted else "❌ Error en encriptación")
```

### 3. Verificar Tablas Creadas

```sql
-- Verificar que las tablas aud_ fueron creadas
SELECT tablename FROM pg_tables WHERE tablename LIKE 'aud_%';

-- Verificar datos encriptados
SELECT * FROM aud_extractos_bancarios LIMIT 5;
```

## 🔧 Solución de Problemas

### Error de Conexión a PostgreSQL

- Verificar que PostgreSQL esté ejecutándose
- Confirmar credenciales en `db_utils.py`
- Verificar que la base de datos `dbpostgrado` existe

### Problemas con Claves RSA

- Eliminar carpeta `keys/` y reiniciar para regenerar claves
- Verificar permisos de escritura en el directorio

### Errores en la Interfaz Web

- Verificar que Flask esté instalado: `pip list | grep -i flask`
- Confirmar que el puerto 5000 esté disponible
- Revisar logs en la consola donde ejecutas `python app.py`

### Tablas `aud_` No Se Crean

- Verificar permisos de usuario en PostgreSQL
- Confirmar que la tabla original existe
- Revisar logs de errores en la aplicación Flask
