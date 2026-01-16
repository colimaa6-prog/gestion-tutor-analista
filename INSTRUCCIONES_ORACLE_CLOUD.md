# 📋 INSTRUCCIONES PARA CONFIGURAR ORACLE CLOUD

## 🔍 Diagnóstico del Problema

Tu aplicación está mostrando errores porque **los endpoints de la API no existen** en Oracle ORDS. El error 404 indica que la URL no se encuentra.

**Error actual:**
```
GET https://corsproxy.io/?https://g6e58321a672730-rggestiontutor.adb.mx-queretaro-1.oraclecloudapps.com/ords/admin/api/v1/incidents 404 (Not Found)
```

**Causa:** El archivo `setup_ords.sql` anterior solo definía 3 endpoints, pero tu aplicación necesita más de 15 endpoints diferentes.

---

## ✅ SOLUCIÓN: Ejecutar el Script Completo

### Paso 1: Acceder a Oracle Cloud

1. Abre tu navegador y ve a: https://cloud.oracle.com
2. Inicia sesión con tus credenciales
3. Ve a **Autonomous Database**
4. Selecciona tu base de datos: `rggestiontutor`
5. Haz clic en **Database Actions** → **SQL**

### Paso 2: Limpiar Configuración Anterior (IMPORTANTE)

Antes de ejecutar el nuevo script, necesitas limpiar la configuración anterior. Ejecuta estos comandos uno por uno:

```sql
-- 1. Eliminar handlers anteriores
BEGIN
    FOR h IN (SELECT id FROM user_ords_handlers) LOOP
        ORDS.DELETE_HANDLER(p_id => h.id);
    END LOOP;
    COMMIT;
END;
/

-- 2. Eliminar templates anteriores
BEGIN
    FOR t IN (SELECT id FROM user_ords_templates) LOOP
        ORDS.DELETE_TEMPLATE(p_id => t.id);
    END LOOP;
    COMMIT;
END;
/

-- 3. Eliminar módulos anteriores
BEGIN
    FOR m IN (SELECT id FROM user_ords_modules) LOOP
        ORDS.DELETE_MODULE(p_id => m.id);
    END LOOP;
    COMMIT;
END;
/

-- 4. Verificar que todo está limpio
SELECT COUNT(*) as handlers FROM user_ords_handlers;
SELECT COUNT(*) as templates FROM user_ords_templates;
SELECT COUNT(*) as modules FROM user_ords_modules;
```

**Resultado esperado:** Todos los COUNT(*) deben ser 0.

### Paso 3: Ejecutar el Script Completo

1. Abre el archivo `setup_ords_complete.sql` que acabo de crear
2. **Copia TODO el contenido** del archivo
3. Pégalo en la ventana de SQL de Oracle Cloud
4. Haz clic en **Run Script** (el botón verde de play)
5. **Espera** a que termine (puede tomar 1-2 minutos)

### Paso 4: Verificar que los Endpoints se Crearon

Ejecuta esta consulta para verificar:

```sql
SELECT 
    m.name as module,
    t.uri_template as endpoint,
    h.method as http_method
FROM user_ords_modules m
JOIN user_ords_templates t ON m.id = t.module_id
JOIN user_ords_handlers h ON t.id = h.template_id
ORDER BY t.uri_template, h.method;
```

**Deberías ver estos endpoints:**

| Endpoint | Métodos |
|----------|---------|
| `login` | POST |
| `employees` | GET, POST |
| `employees/:id` | DELETE |
| `branches` | GET |
| `incidents` | GET, POST |
| `incidents/:id` | PUT, DELETE |
| `attendance/mark` | POST |
| `attendance/roster` | GET, POST |
| `attendance/roster/:id` | DELETE |
| `dashboard/stats` | GET |

### Paso 5: Obtener la URL Base de tu API

1. En Oracle Cloud, ve a **Database Actions** → **REST**
2. Copia la URL base que aparece arriba
3. Debería verse así:
   ```
   https://g6e58321a672730-rggestiontutor.adb.mx-queretaro-1.oraclecloudapps.com/ords/admin/api/v1/
   ```

### Paso 6: Actualizar el archivo config.js

La URL en tu `config.js` ya está correcta, pero verifica que sea exactamente:

```javascript
const API_BASE_URL = 'https://corsproxy.io/?' + encodeURIComponent('https://g6e58321a672730-rggestiontutor.adb.mx-queretaro-1.oraclecloudapps.com/ords/admin/api/v1');
```

**NOTA:** El `/api/v1` al final es importante porque así lo definimos en el script.

---

## 🧪 PRUEBA: Verificar que Funciona

### Opción 1: Desde el Navegador

Abre una nueva pestaña y prueba estos URLs:

1. **Empleados:**
   ```
   https://g6e58321a672730-rggestiontutor.adb.mx-queretaro-1.oraclecloudapps.com/ords/admin/api/v1/employees
   ```
   
2. **Sucursales:**
   ```
   https://g6e58321a672730-rggestiontutor.adb.mx-queretaro-1.oraclecloudapps.com/ords/admin/api/v1/branches
   ```

3. **Incidencias:**
   ```
   https://g6e58321a672730-rggestiontutor.adb.mx-queretaro-1.oraclecloudapps.com/ords/admin/api/v1/incidents
   ```

**Resultado esperado:** Deberías ver un JSON con `{"success": true, "data": [...]}`

### Opción 2: Desde la Aplicación

1. Abre `dashboard.html` en tu navegador
2. Inicia sesión con: `admin` / `admin123`
3. Ve a cada sección:
   - **Dashboard** → Debería mostrar estadísticas
   - **Jefes de Oficina** → Debería cargar la lista de empleados
   - **Incidencias** → Debería cargar la lista de incidencias

---

## ❌ Si Aún Hay Errores

### Error: "404 Not Found"
**Causa:** El endpoint no existe en ORDS.
**Solución:** Verifica que ejecutaste el script completo y que la URL en `config.js` es correcta.

### Error: "CORS policy"
**Causa:** Oracle Cloud bloquea peticiones desde otros dominios.
**Solución:** Ya estás usando `corsproxy.io` en tu config, así que esto no debería pasar.

### Error: "Unexpected token '<'"
**Causa:** El servidor está devolviendo HTML en lugar de JSON.
**Solución:** Esto significa que el endpoint no existe. Verifica la URL completa en la consola del navegador.

### Error: "ORA-XXXXX" en Oracle Cloud
**Causa:** Error de sintaxis SQL.
**Solución:** 
1. Lee el mensaje de error completo
2. Busca la línea que causó el error
3. Si es un problema con tablas existentes, primero elimínalas:
   ```sql
   DROP TABLE attendance_roster CASCADE CONSTRAINTS;
   DROP TABLE attendance CASCADE CONSTRAINTS;
   DROP TABLE reports CASCADE CONSTRAINTS;
   DROP TABLE incidents CASCADE CONSTRAINTS;
   DROP TABLE employees CASCADE CONSTRAINTS;
   DROP TABLE users CASCADE CONSTRAINTS;
   DROP TABLE branches CASCADE CONSTRAINTS;
   ```
4. Luego ejecuta el script completo de nuevo

---

## 📝 Notas Importantes

1. **Usuario de la base de datos:** El script usa `USER` que se refiere al usuario actual (probablemente `ADMIN`)
2. **Base path:** Configuramos `/admin/api/v1/` como base path
3. **CORS:** Estás usando `corsproxy.io` que es una solución temporal. Para producción, deberías configurar CORS en Oracle Cloud
4. **Seguridad:** Las contraseñas están en texto plano (`admin123`). Para producción, deberías usar hashing

---

## 🎯 Checklist Final

- [ ] Limpié la configuración anterior de ORDS
- [ ] Ejecuté el script `setup_ords_complete.sql` completo
- [ ] Verifiqué que se crearon todos los endpoints
- [ ] Probé los endpoints desde el navegador
- [ ] La aplicación carga datos correctamente

---

## 🆘 ¿Necesitas Ayuda?

Si después de seguir estos pasos aún tienes problemas:

1. Toma una captura de pantalla del error en la consola del navegador (F12)
2. Copia el mensaje de error completo
3. Verifica qué URL exacta está intentando acceder
4. Comparte esta información para ayudarte mejor
