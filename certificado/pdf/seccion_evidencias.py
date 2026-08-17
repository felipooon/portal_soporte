from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from .plantilla import (
    MARGEN_X, ANCHO_UTIL, ALTO_PAGINA, COLOR_NEGRO, COLOR_BORDE_TABLA,
    COLOR_TEXTO_TABLA, COLOR_SUBTITULO, dibujar_titulo_seccion
)


def obtener_lista_imagenes(evidencias, carpeta_evidencias=None):
    """Obtiene una lista de rutas (Path) a archivos de imágenes."""
    rutas_imagenes = []
    extensiones_validas = {".jpg", ".jpeg", ".png", ".webp"}

    # 1. Escanear carpeta centralizada personal ~/evidencias_instalacion
    dir_entrada = Path.home() / "evidencias_instalacion"
    if dir_entrada.exists() and dir_entrada.is_dir():
        for p in sorted(dir_entrada.iterdir()):
            if p.is_file() and p.suffix.lower() in extensiones_validas and not p.name.startswith("."):
                rutas_imagenes.append(p)

    # 2. Escanear carpeta de evidencias del certificado como respaldo si la central está vacía
    if not rutas_imagenes and carpeta_evidencias:
        dir_path = Path(carpeta_evidencias)
        if dir_path.exists() and dir_path.is_dir():
            for p in sorted(dir_path.iterdir()):
                if p.is_file() and p.suffix.lower() in extensiones_validas and not p.name.startswith("."):
                    rutas_imagenes.append(p)

    # Procesar lista de evidencias pasadas
    if isinstance(evidencias, (list, tuple)) and not rutas_imagenes:
        for item in evidencias:
            r_str = ""
            if isinstance(item, dict):
                r_str = item.get("ruta") or item.get("archivo") or ""
            elif hasattr(item, "ruta") or hasattr(item, "archivo"):
                r_str = getattr(item, "ruta", None) or getattr(item, "archivo", None) or ""
            elif isinstance(item, (str, Path)):
                r_str = str(item)

            if r_str:
                p = Path(r_str)
                if p.exists() and p.is_file() and p.suffix.lower() in extensiones_validas:
                    rutas_imagenes.append(p)

    return rutas_imagenes


def agregar_evidencias(pdf, evidencias, y, carpeta_evidencias=None):
    imagenes = obtener_lista_imagenes(evidencias, carpeta_evidencias)

    if not imagenes:
        return y

    # Forzar inicio de Registro Fotográfico en nueva página dedicada
    pdf.showPage()
    y = ALTO_PAGINA - 90
    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "10. Registro fotográfico")

    # 2. Configuración de Formato Libre Estándar Uniforme (2 fotos grandes por página)
    ancho_box = ANCHO_UTIL
    alto_caja_exterior = 280.0  # Tamaño por defecto uniforme para cada foto

    idx = 0
    total_imgs = len(imagenes)

    while idx < total_imgs:
        # Renderizar hasta 2 fotos por página
        for i in range(2):
            if idx >= total_imgs:
                break

            # Verificar si la foto cabe en la página actual sin tocar margen inferior
            if y - alto_caja_exterior < 45:
                pdf.showPage()
                y = ALTO_PAGINA - 90
                y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "7. Registro fotográfico (cont.)")

            ruta_img = imagenes[idx]
            idx += 1

            y_box_top = y

            # Dibujar marco contenedor gris claro exterior
            pdf.setFillColor(colors.HexColor("#fcfcfc"))
            pdf.setStrokeColor(COLOR_BORDE_TABLA)
            pdf.setLineWidth(0.6)
            pdf.rect(MARGEN_X, y_box_top - alto_caja_exterior, ancho_box, alto_caja_exterior, fill=True, stroke=True)

            # Pie de foto / Leyenda estándar secuencial (Fotografía N° 1, Fotografía N° 2...)
            alto_leyenda = 24.0
            y_leyenda = y_box_top - alto_caja_exterior + 8.0
            x_leyenda = MARGEN_X + 8.0
            w_leyenda = ancho_box - 16.0

            pdf.setFillColor(colors.white)
            pdf.rect(x_leyenda, y_leyenda, w_leyenda, alto_leyenda, fill=True, stroke=True)

            pdf.setFillColor(COLOR_NEGRO)
            pdf.setFont("Helvetica-Bold", 8.5)
            pdf.drawString(x_leyenda + 8, y_leyenda + 7, f"Fotografía N° {idx}")

            pdf.setFillColor(COLOR_SUBTITULO)
            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(x_leyenda + w_leyenda - 8, y_leyenda + 7, f"Archivo: {ruta_img.name}")

            # Espacio para renderizar la imagen centrada de tamaño por defecto
            max_img_w = ancho_box - 24.0
            max_img_h = alto_caja_exterior - alto_leyenda - 24.0

            if ruta_img.exists() and ruta_img.is_file():
                try:
                    img_reader = ImageReader(str(ruta_img))
                    img_w, img_h = img_reader.getSize()

                    aspect_img = img_h / float(img_w)
                    aspect_max = max_img_h / float(max_img_w)

                    if aspect_img > aspect_max:
                        render_h = max_img_h
                        render_w = render_h / aspect_img
                    else:
                        render_w = max_img_w
                        render_h = render_w * aspect_img

                    img_x = MARGEN_X + ((ancho_box - render_w) / 2.0)
                    img_y = y_leyenda + alto_leyenda + 6.0 + ((max_img_h - render_h) / 2.0)

                    # Borde suave alrededor de la fotografía
                    pdf.setStrokeColor(COLOR_BORDE_TABLA)
                    pdf.setLineWidth(0.5)
                    pdf.rect(img_x - 1, img_y - 1, render_w + 2, render_h + 2, fill=False, stroke=True)

                    pdf.drawImage(str(ruta_img), img_x, img_y, width=render_w, height=render_h)
                except Exception:
                    pdf.setFillColor(COLOR_TEXTO_TABLA)
                    pdf.setFont("Helvetica", 8.5)
                    pdf.drawCentredString(MARGEN_X + (ancho_box / 2.0), y_box_top - (alto_caja_exterior / 2.0), "[Error al cargar fotografía]")
            else:
                pdf.setFillColor(COLOR_TEXTO_TABLA)
                pdf.setFont("Helvetica", 8.5)
                pdf.drawCentredString(MARGEN_X + (ancho_box / 2.0), y_box_top - (alto_caja_exterior / 2.0), "[Fotografía no encontrada]")

            y = y_box_top - alto_caja_exterior - 18.0

    return y
