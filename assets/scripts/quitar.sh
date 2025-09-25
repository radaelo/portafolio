#!/bin/bash

# Este script renombra archivos en el directorio actual, eliminando guiones (-) de sus nombres.

echo "Buscando archivos con guiones en el nombre en el directorio actual..."

# Encuentra archivos con guiones en el nombre y los procesa
find . -maxdepth 1 -type f -name "*-*.pdf" -print0 | while IFS= read -r -d $'\0' file; do
    # Extrae la ruta del directorio, el nombre base y la extensión
    dir_name=$(dirname "$file")
    base_name=$(basename "$file")
    extension="${base_name##*.}"
    filename_no_ext="${base_name%.*}"

    # Elimina todos los guiones del nombre sin la extensión
    new_filename_no_ext=$(echo "$filename_no_ext" | tr -d '-')

    # Reconstruye el nuevo nombre completo del archivo
    new_name="$dir_name/$new_filename_no_ext.$extension"

    # Verifica si el nuevo nombre es diferente al original
    if [ "$file" != "$new_name" ]; then
        mv "$file" "$new_name"
        echo "Renombrado: '$file' -> '$new_name'"
    else
        echo "Saltado: '$file' (ya no tiene guiones o el cambio no es significativo)"
    fi
done

echo "Proceso completado."
