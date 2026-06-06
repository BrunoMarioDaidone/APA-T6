"""
Bruno Mario Daidone Rossini
Fichero que contiene la función normalizaHoras junto con las
funciones auxiliares de esta.
"""
def normalizaHoras(ficText, ficNorm):
    """
    Función que, con ayuda de otras funciones auxiliares 
    lee un fichero, lo analiza en busca de expresiones horarias
    y escribe otro fichero en el que se expresan según el 
    formato normalizado (08:27).
    """
    import re
# Aquí estan las funciones de normalización respectivas a cada
# formato que da el enunciado

    def normaliza_hhmm(match):
        """Normaliza expresiones tipo HH:MM o H:MM."""
        h = match.group(1)
        m = match.group(2)

        # Hora entre 0 y 23, minuto 0 y 59
        if not (h.isdigit() and m.isdigit()):
            return match.group(0)

        h = int(h)
        m = int(m)

        if 0 <= h <= 23 and 0 <= m <= 59:
            return f"{h:02d}:{m:02d}"
        return match.group(0)

    def normaliza_hhmm_letras(match):
        """Normaliza expresiones tipo 7h, 7h5m, 7h05m, 17h30m."""
        h = match.group(1)
        m = match.group(2)

        if not h.isdigit():
            return match.group(0)

        h = int(h)

        # Los minutos pueden darse o no. Vease 7h que no tiene minutos,
        # pero 7h5m si que los tiene 
        if m is None:
            m = 0
        else:
            if not m.isdigit():
                return match.group(0)
            m = int(m)

        # Validación de que los valoers están en los parámetros permitidos
        if not (0 <= h <= 23 and 0 <= m <= 59):
            return match.group(0)

        return f"{h:02d}:{m:02d}"

    def normaliza_exp_12h(h, minutos, periodo):
        """
        Convierte expresiones de 12h + periodo a formato 24h.
        h: 1–12
        minutos: 0–59
        periodo: mañana, mediodía, tarde, noche, madrugada
        """

        if not (1 <= h <= 12 and 0 <= minutos <= 59):
            return None

        if periodo == "mañana":
            if 4 <= h <= 12:
                return f"{h % 12:02d}:{minutos:02d}"
            return None

        if periodo == "mediodía":
            if h == 12:
                return f"12:{minutos:02d}"
            if 1 <= h <= 3:
                return f"{12 + h:02d}:{minutos:02d}"
            return None

        if periodo == "tarde":
            if 3 <= h <= 8:
                return f"{12 + h:02d}:{minutos:02d}"
            return None

        if periodo == "noche":
            if h == 12:
                return f"00:{minutos:02d}"
            if 1 <= h <= 4:
                return f"{h:02d}:{minutos:02d}"
            if 8 <= h <= 11:
                return f"{(h + 12) % 24:02d}:{minutos:02d}"
            return None

        if periodo == "madrugada":
            if 1 <= h <= 6:
                return f"{h:02d}:{minutos:02d}"
            return None

        return None

    def normaliza_frases_12h(match):
        """Normaliza expresiones tipo '8 y cuarto de la tarde', '5 menos cuarto de la noche', etc."""
        h = int(match.group(1))
        tipo = match.group(2)
        periodo = match.group(3)

        if tipo == "en punto":
            minutos = 0
        elif tipo == "y cuarto":
            minutos = 15
        elif tipo == "y media":
            minutos = 30
        elif tipo == "menos cuarto":
            h -= 1
            minutos = 45
            if h == 0:
                h = 12
        else:
            return match.group(0)

        res = normaliza_exp_12h(h, minutos, periodo)
        return res if res is not None else match.group(0)

# A partir de aquí es todo el trabajo con los datos de cada line
# (lectura, escritura y demás).
    with open(ficText, "r", encoding="utf-8") as f_in, \
         open(ficNorm, "w", encoding="utf-8") as f_out:

        for linea in f_in:

            original = linea

            # Aquí busca expresiones del estilo HH:MM
            linea = re.sub(r"\b(\d{1,2}):(\d{2})\b", normaliza_hhmm, linea)

            # Aquí son del estilo HhMm
            linea = re.sub(r"\b(\d{1,2})h(?:(\d{1,2})m)?\b", normaliza_hhmm_letras, linea)

            # Aquí para expresiones como 12h con frases 
            patron_frases = (
                r"\b(\d{1,2})\s*"
                r"(en punto|y cuarto|y media|menos cuarto)"
                r"\s+de la\s+(mañana|tarde|noche|madrugada|mediodía)\b"
            )
            linea = re.sub(patron_frases, normaliza_frases_12h, linea)

            # Y aquí para expresiones 12h sin minutos, osea "8 de la tarde", por ejemplo
            patron_simple = r"\b(\d{1,2})\s+de la\s+(mañana|tarde|noche|madrugada|mediodía)\b"

            def normaliza_simple(match):
                h = int(match.group(1))
                periodo = match.group(2)
                res = normaliza_exp_12h(h, 0, periodo)
                return res if res is not None else match.group(0)

            linea = re.sub(patron_simple, normaliza_simple, linea)

            f_out.write(linea)
