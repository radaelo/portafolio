#!/bin/bash

# Este script renombra archivos en el directorio actual, reemplazando espacios con guiones.

echo "Buscando archivos con espacios en el nombre en el directorio actual..."

# Encuentra archivos con espacios en el nombre y los procesa
find . -maxdepth 1 -type f -name "* *" -print0 | while IFS= read -r -d $'\0' file; do
    # Reemplaza espacios con guiones en el nombre del archivo
    new_name=$(echo "$file" | tr ' ' '-')

    # Verifica si el nuevo nombre es diferente al original
    if [ "$file" != "$new_name" ]; then
        mv "$file" "$new_name"
        echo "Renombrado: '$file' -> '$new_name'"
    else
        echo "Saltado: '$file' (ya no tiene espacios o el cambio no es significativo)"
    fi
done

echo "Proceso completado."
