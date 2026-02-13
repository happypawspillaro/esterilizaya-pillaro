# Instalación

## Prerequisitos

1. Por favor, sigue las instrucciones de [instalación](https://docs.docker.com/engine/install/) de Docker
2. Configura Docker para que corra en modo [rootless](https://docs.docker.com/engine/security/rootless/#install)

## Instrucciones

Estas instrucciones están indicadas para usuarios que corran en sistemas basados en Debian como Ubuntu, por favor referirse a tu distribución en caso de hacer cambios. También estás instrucciones están dedicadas a configurar el sistema _sin conexión_ como es el objetivo de las campañas

1. Por favor, copie las variables de entorno para iniciar el sistema `cp .env.example .env`, luego se pueden cambiar a discreción
2. Genera una clave segura, por ejemplo con `openssl rand -base64 32`, luego reemplaza el valor de `SECRET_KEY` con el generado
3. Cree los archivos con la información sensible en la carpeta `credenciales`, por ejemplo en Linux:

   ```bash
       mkdir -p credenciales/database
       openssl rand -base64 32 > credenciales/database/root_password.txt
       openssl rand -base64 32 > credenciales/database/user_password.txt
       openssl rand -base64 32 > credenciales/database/admin_password.txt
       mkdir -p credenciales/superuser
       openssl rand -base64 32 > credenciales/superuser/password.txt
   ```

4. Debido a que a veces el sistema no tendrá internet, es necesario descargar `bootstrap` >= 5 y `bootstrap-autocomplete` localmente para que todo el frontend funcione, es recomendable descargarlo de la página oficial con los siguientes comandos:

   ```bash
      # Descarga Bootstrap
      BOOTSTRAP_VERSION="5.3.7"
      wget -P app/static https://github.com/twbs/bootstrap/releases/download/v$BOOTSTRAP_VERSION/bootstrap-$BOOTSTRAP_VERSION-dist.zip
      mkdir -p app/static/temp_bootstrap
      unzip app/static/bootstrap-$BOOTSTRAP_VERSION-dist.zip -d app/static/temp_bootstrap
      mkdir -p app/static/js && mv app/static/temp_bootstrap/bootstrap-$BOOTSTRAP_VERSION-dist/js/* app/static/js
      mkdir -p app/static/css && mv app/static/temp_bootstrap/bootstrap-$BOOTSTRAP_VERSION-dist/css/* app/static/css
      rm -rf app/static/temp_bootstrap
      rm app/static/bootstrap-$BOOTSTRAP_VERSION-dist.zip
      # Descarga Bootstrap Icons
      BOOTSTRAP_ICONS_VERSION="1.13.1"
      wget -P app/static/css https://cdn.jsdelivr.net/npm/bootstrap-icons@$BOOTSTRAP_ICONS_VERSION/font/bootstrap-icons.min.css
      wget -P app/static/css/fonts https://cdn.jsdelivr.net/npm/bootstrap-icons@$BOOTSTRAP_ICONS_VERSION/font/fonts/bootstrap-icons.woff
      wget -P app/static/css/fonts https://cdn.jsdelivr.net/npm/bootstrap-icons@$BOOTSTRAP_ICONS_VERSION/font/fonts/bootstrap-icons.woff2
      # Descarga boostrap-autocomplete
      wget -P app/static/js/ https://cdn.jsdelivr.net/gh/lekoala/bootstrap5-autocomplete@master/autocomplete.js
      # Descarga jQuery
      JQUERY_VERSION="3.7.1"
      wget https://code.jquery.com/jquery-$JQUERY_VERSION.min.js -O app/static/js/jquery.min.js
      # Descargar Chart.js
      CHART_JS_VERSION="4.5.0"
      wget https://cdnjs.cloudflare.com/ajax/libs/Chart.js/$CHART_JS_VERSION/chart.umd.min.js -O app/static/js/chart.umd.min.js
      wget https://cdnjs.cloudflare.com/ajax/libs/Chart.js/$CHART_JS_VERSION/chart.umd.min.js.map -O app/static/js/chart.umd.min.js.map
      wget https://cdnjs.cloudflare.com/ajax/libs/Chart.js/$CHART_JS_VERSION/chart.umd.js.map -O app/static/js/chart.umd.js.map
      # Descargar Leaflet
      LEAFLET_VERSION="1.9.4"
      wget -P app/static/css https://unpkg.com/leaflet@$LEAFLET_VERSION/dist/leaflet.css
      wget -P app/static/js https://unpkg.com/leaflet@$LEAFLET_VERSION/dist/leaflet.js
      wget -P app/static/js https://unpkg.com/leaflet@$LEAFLET_VERSION/dist/leaflet.js.map
   ```

5. Por favor cambia los permisos de tu carpeta de código, en Alpine Linux, el usuario y grupo `www-data` es diferente al de Debian/Ubuntu, en tal caso, usa la siguiente línea para modificar los permisos:

   ```bash
   mkdir -p app/{ssl,uwsgi}
   sudo chown -R 100:82 app/
   sudo chmod -R a+rwX ./app/{campana,inscripcion,registro,ssl,uwsgi}
   ```

6. Descargue los contenedores y ejecuta las migraciones el siguiente comando:

   ```bash
      docker compose -f docker-compose.yml -f docker-compose.prod.yml build
      # En caso de no tener tu ruta de migración, inicializa y da permisos para escribir
      RUTA_MIGRACION=app/tu_app/migrations
      sudo mkdir -p $RUTA_MIGRACION && sudo touch $RUTA_MIGRACION/__init__.py && sudo chmod 777 $RUTA_MIGRACION
      docker compose -f docker-compose.yml -f docker-compose.migrate.yml up db -d
      docker compose -f docker-compose.yml -f docker-compose.migrate.yml -f docker-compose.dev.yml up web
   ```

7. Crea un nuevo superusuario del sistema, con el siguiente comando:

   ```bash
      docker compose -f docker-compose.yml -f docker-compose.superuser.yml up web
   ```

8. Genera el certificado SSL

   ```bash
   openssl req -x509 -newkey rsa:2048 -sha256 -days 3650 -nodes \
       -keyout app/ssl/happypaws.key -out app/ssl/happypaws.crt \
       -subj '/CN=*.happypawspillaro.org' \
       -addext 'subjectAltName=DNS:*.happypawspillaro.org'
   ```

9. Inicie el sistema con el comando:

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

   Puedes acceder al servidor en [http://localhost:8443](http://localhost:8443), nota
   si quieres iniciarle en modo desarrollo refierete a las instrucciones en el [DEVELOPMENT.md](DEVELOPMENT.md)

10. Colecciona los archivos estáticos de tu directorio con el siguiente comando

```bash
docker compose exec web python /home/esterilizaya/code/manage.py collectstatic
```

### Adicional

1. Para poder usar un dominio reconocible, por favor añadir en tu archivo `/etc/hosts` la siguiente línea:

   ```text
   127.0.0.1 happypawspillaro.org www.happypawspillaro.org
   ```

## Preguntas frecuentes

### Cambiar permisos de los volumenes

En caso de que no tengas permiso a acceder el volumen, usa este comando para cambiar el user ID a `100` y el grupo a`82` en el contenedor web.

```bash
  docker run --rm \
    -v esterilizaya-pillaro_media-volume:/data \
    alpine \
    chown -R 100:82 /data
```

### Error 500

Si tienes un error 500, puedes revisar los logs con `docker compose logs web`, pueden suceder los siguientes escenerios:

#### Falta Secret Key

Si puedes ver este error:

```bash
django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty.
```

Asegurate que añadiste una clave segura a tu variable `SECRET_KEY` en el archivo `.env`, revisa las instrucciones para saber cómo

### Redireccionar el tráfico a puertos privilegiados

Si quieres utilizar los puertos privilegiados de tu sistema para tus otros usuarios, usa `iptables` con los siguientes comando, por favor reemplaza la variable `HOTSPOT_IFACE` con tu adaptador de red actual.

```bash
HOTSPOT_IFACE=enp3s0
sudo iptables -t nat -A PREROUTING -i $HOTSPOT_IFACE -p tcp --dport 443 -j REDIRECT --to-port 8443
sudo iptables -t nat -A PREROUTING -i $HOTSPOT_IFACE -p tcp --dport 80 -j REDIRECT --to-port 8080
```
