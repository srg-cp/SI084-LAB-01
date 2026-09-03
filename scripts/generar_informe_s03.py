"""Completa el borrador DOCX del Taller 03 sin inventar evidencias."""

from copy import deepcopy
from pathlib import Path
import sys
import zipfile

from lxml import etree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{" + W_NS + "}"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def paragraph_text(paragraph):
    return "".join(node.text or "" for node in paragraph.iter(W + "t"))


def set_paragraph_text(paragraph, text):
    properties = paragraph.find(W + "pPr")
    saved_properties = deepcopy(properties) if properties is not None else None
    for child in list(paragraph):
        paragraph.remove(child)
    if saved_properties is not None:
        paragraph.append(saved_properties)
    run = ET.SubElement(paragraph, W + "r")
    node = ET.SubElement(run, W + "t")
    if text.startswith(" ") or text.endswith(" "):
        node.set(XML_SPACE, "preserve")
    node.text = text


def set_cell_text(cell, text):
    properties = cell.find(W + "tcPr")
    saved_properties = deepcopy(properties) if properties is not None else None
    for child in list(cell):
        cell.remove(child)
    if saved_properties is not None:
        cell.append(saved_properties)
    paragraph = ET.SubElement(cell, W + "p")
    run = ET.SubElement(paragraph, W + "r")
    node = ET.SubElement(run, W + "t")
    node.text = text


def find_paragraph(body, exact_text):
    for child in body:
        if child.tag == W + "p" and paragraph_text(child).strip() == exact_text:
            return child
    raise ValueError(f"No se encontró el párrafo: {exact_text}")


def insert_after(body, anchor, paragraphs, paragraph_template):
    position = list(body).index(anchor) + 1
    for text in paragraphs:
        paragraph = deepcopy(paragraph_template)
        set_paragraph_text(paragraph, text)
        body.insert(position, paragraph)
        position += 1


source = Path(sys.argv[1])
destination = Path(sys.argv[2])

with zipfile.ZipFile(source) as archive:
    document_xml = archive.read("word/document.xml")
    package = {name: archive.read(name) for name in archive.namelist()}

root = ET.fromstring(document_xml)
body = root.find(W + "body")

replacements = {
    "INFORME DE LABORATORIO N.º 2": "INFORME DE LABORATORIO N.º 03",
    "Título del taller": "Evaluación de riesgos con SimpleRisk y detección técnica con Nuclei",
    "Semana N.º __2__ · Unidad _1__ · Grupo N.º ____": "Semana N.º 03 · Unidad I · Grupo N.º COLQUE",
    "SERGIO COLQUE PONCE": "SERGIO COLQUE PONCE",
    "Haz clic derecho aquí y elige «Actualizar campos» para generar el índice.": "Actualice este índice en Word antes de exportar el PDF.",
    "Reglas de uso del laboratorio y de alcance que se respetaron durante el trabajo.": (
        "El escaneo se limita a los contenedores del entorno local si084-lab. No se analizan sistemas "
        "institucionales, direcciones públicas ni equipos de terceros. Las aplicaciones vulnerables se "
        "publican únicamente en 127.0.0.1 y solo se emplean datos sintéticos."
    ),
    "Cada paso lleva su título, qué se buscaba, el comando o la acción, y la evidencia de que funcionó. Quien lea el informe debe poder repetir el trabajo sin preguntar nada.": (
        "Se empleó como base el entorno Docker construido en el Taller 01. Para la detección técnica se "
        "seleccionó Nuclei, alternativa expresamente admitida por la guía cuando Greenbone/OpenVAS no es "
        "viable por consumo de recursos. Los resultados se sustentan en archivos técnicos y capturas fechadas."
    ),
    "Paso A": "Paso A — Preparar el entorno y el alcance autorizado",
    "Paso B": "Paso B — Desplegar y configurar SimpleRisk",
    "Paso C": "Paso C — Ejecutar el escaneo técnico con Nuclei",
    "Si algo no se logró, explícalo aquí. Un resultado no alcanzado y bien explicado vale más que uno declarado sin evidencia.": (
        "Se completó el escaneo con Nuclei, la configuración de SimpleRisk y el registro de diez riesgos. "
        "Se cargaron y trataron cuatro riesgos en SimpleRisk; el quinto quedó pendiente por límite de tiempo."
    ),
    "Mínimo tres. Una conclusión no resume lo que hiciste. Dice lo que aprendiste y se sostiene en la evidencia de la sección 3.": (
        "1. El CVSS no sustituye la valoración de negocio: WordPress obtuvo severidad técnica crítica, pero "
        "riesgo Bajo (5) por el contexto del activo público.\n"
        "2. La exposición de métricas y configuraciones demuestra que una respuesta HTTP exitosa puede revelar "
        "información suficiente para reconocimiento y ataques posteriores.\n"
        "3. La gestión de secretos y el mínimo privilegio son prioritarios: las credenciales débiles y la cuenta "
        "erp_app con privilegios administrativos elevan el impacto sobre la base ERP restringida.\n"
        "4. SimpleRisk permitió mantener trazabilidad entre activo, evidencia, dueño, valoración y tratamiento; "
        "quedó documentada la limitación de cuatro de cinco riesgos cargados por tiempo disponible."
    ),
    "Copia cada pregunta de la guía de la semana y respóndela debajo.": (
        "La guía del Taller 03 no presenta preguntas de cuestionario."
    ),
    "Normas técnicas, marcos profesionales, documentación oficial y bibliografía indexada, en formato APA. No se admiten wikis abiertas ni sitios sin autoría verificable.": (
        "ISO/IEC 27001:2022. Information security, cybersecurity and privacy protection — Information "
        "security management systems — Requirements. https://www.iso.org/standard/27001\n"
        "ISO/IEC 27002:2022. Information security controls. https://www.iso.org/standard/75652.html\n"
        "ISO/IEC 27005:2022. Guidance on managing information security risks. "
        "https://www.iso.org/standard/80585.html\n"
        "ISO 31000:2018. Risk management — Guidelines. https://www.iso.org/standard/65694.html\n"
        "ProjectDiscovery. Nuclei documentation. https://docs.projectdiscovery.io/tools/nuclei"
    ),
    "Capturas completas, archivos de configuración y salidas extensas. Cada anexo lleva su letra y su título, y se menciona en el cuerpo del informe.": (
        "Anexo A — Reporte técnico de Nuclei en CSV, XML y JSONL.\n"
        "Anexo B — Registro PT03 con diez riesgos.\n"
        "Anexo C — Extracto de la Declaración de Aplicabilidad.\n"
        "Anexo D — Declaración firmada del alcance autorizado.\n"
        "Anexo E — Capturas 01 a 15 de ejecución, configuración y tratamiento.\n"
        "Repositorio: https://github.com/srg-cp/SI084-LAB-01\n"
        "Versión de entrega: https://github.com/srg-cp/SI084-LAB-01/tree/taller-03"
    ),
}

for child in body:
    if child.tag == W + "p":
        current = paragraph_text(child).strip()
        if current in replacements:
            set_paragraph_text(child, replacements[current])

paragraph_template = find_paragraph(body, "La guía del Taller 03 no presenta preguntas de cuestionario.")

section_content = {
    "1.1 Título del evento práctico": [
        "Apreciación y tratamiento del riesgo de seguridad de la información sobre el entorno auditado, "
        "alimentada por evidencia técnica obtenida con Nuclei."
    ],
    "1.2 Objetivos": [
        "• Ejecutar un escaneo autorizado sobre el entorno si084-lab.",
        "• Interpretar severidad técnica, CVE y exposición en función del contexto de negocio.",
        "• Elaborar un registro con al menos diez riesgos y asignarles dueño, probabilidad e impacto.",
        "• Definir tratamiento y controles de ISO/IEC 27001:2022 mediante un extracto de SoA.",
    ],
    "1.3 Tiempo de duración": ["100 minutos: 60 de taller guiado y 40 de avance asistido."],
    "1.4 Resultados de aprendizaje": [
        "RA2: Evalúa la seguridad de la información en Auditoría de Sistemas.",
        "RA3: Aplica normas y estándares de auditoría para sustentar riesgos, controles y tratamiento.",
    ],
}

for heading, paragraphs in section_content.items():
    insert_after(body, find_paragraph(body, heading), paragraphs, paragraph_template)

step_content = {
    "Paso A — Preparar el entorno y el alcance autorizado": [
        "Se conservó el laboratorio de la Semana 01 y se documentó el alcance en "
        "00_administracion/AUTORIZACION_ESCANEO_S03.md. Los únicos objetivos autorizados son juiceshop, "
        "dvwa y wordpress dentro de la red Docker si084-lab_audit_net.",
    ],
    "Paso B — Desplegar y configurar SimpleRisk": [
        "Se añadieron los servicios si084_srdb y si084_simplerisk al archivo entorno/docker-compose.yml. "
        "La interfaz se publica exclusivamente en http://127.0.0.1:8083. La configuración de escalas "
        "1–5 y el criterio de aceptación ≤ 6 se documentó en PT03_escalas_riesgo.md.",
        "Las capturas 04 a 07 demuestran la operación, fórmula y apetito Medio (6); las capturas 08 a 15 "
        "demuestran el registro y tratamiento aceptado de R-001 a R-004.",
    ],
    "Paso C — Ejecutar el escaneo técnico con Nuclei": [
        "El script scripts/S03_ejecutar_escaneo.cmd levanta el laboratorio, registra los contenedores y "
        "ejecuta Nuclei contra los tres servicios web internos. La salida JSONL se convierte de manera "
        "reproducible a CSV y XML mediante scripts/S03_nuclei_a_reportes.py.",
        "El escaneo produjo tres hallazgos reales: métricas Prometheus expuestas, instalador de WordPress "
        "accesible y listado de archivos de configuración en DVWA. Se conservaron CSV, XML y JSONL."
    ],
}

for heading, paragraphs in step_content.items():
    insert_after(body, find_paragraph(body, heading), paragraphs, paragraph_template)

section_three = find_paragraph(body, "3. Resultados")
heading_template = deepcopy(find_paragraph(body, "Paso C — Ejecutar el escaneo técnico con Nuclei"))
position = list(body).index(section_three)

for heading, paragraphs in [
    (
        "Paso D — Convertir hallazgos técnicos en riesgos de negocio",
        [
            "El programa 30_papeles_trabajo/PT03_tecnico_a_riesgo.py combina cada hallazgo con el dueño, "
            "clasificación, exposición y criticidad del activo. El registro final contiene diez riesgos: tres "
            "derivados de Nuclei y siete sustentados en la línea base de configuración del entorno."
        ],
    ),
    (
        "Paso E — Tratamiento y extracto de la Declaración de Aplicabilidad",
        [
            "PT03_soa_extracto.md contiene cinco controles, incluido A.7.4 como control excluido y justificado, "
            "con referencias a los riesgos del registro. SimpleRisk conserva planes aceptados para R-001 a R-004."
        ],
    ),
]:
    new_heading = deepcopy(heading_template)
    set_paragraph_text(new_heading, heading)
    body.insert(position, new_heading)
    position += 1
    for text in paragraphs:
        paragraph = deepcopy(paragraph_template)
        set_paragraph_text(paragraph, text)
        body.insert(position, paragraph)
        position += 1

tables = [child for child in body if child.tag == W + "tbl"]
resource_rows = tables[0].findall(W + "tr")[1:]
resource_data = [
    ("Docker Desktop y Docker Compose", "Cliente Docker 28.0.4", "Ejecutar el entorno auditable y SimpleRisk"),
    ("Nuclei", "Imagen latest", "Escaneo técnico autorizado como alternativa a Greenbone"),
    ("Python", "3.11", "Conversión de reportes y construcción del registro de riesgos"),
]
for row, values in zip(resource_rows, resource_data):
    for cell, value in zip(row.findall(W + "tc"), values):
        set_cell_text(cell, value)

result_rows = tables[1].findall(W + "tr")[1:]
results = [
    ("Greenbone/OpenVAS operativo o Nuclei como alternativa documentada", "Logrado", "Capturas 02–03 y E03_scan/"),
    ("SimpleRisk configurado con escalas 1–5 y criterio de aceptación", "Logrado", "Capturas 04–07"),
    ("Reporte técnico CSV y XML con objetivos autorizados", "Logrado", "20_evidencia/E03_scan/"),
    ("Registro con al menos 10 riesgos", "Logrado", "40_hallazgos/PT03_registro_riesgos.csv"),
    ("Dos casos contrastantes documentados", "Parcial", "R-003: CVSS alto/riesgo bajo; R-001: CVSS medio/riesgo alto"),
    ("Cinco riesgos cargados y tratados en SimpleRisk", "Parcial (4/5)", "Capturas 08–15: R-001 a R-004"),
    ("Extracto de SoA con cinco controles", "Logrado", "30_papeles_trabajo/PT03_soa_extracto.md"),
    ("Hashes, cadena de custodia y commit", "Pendiente", "20_evidencia/SHA256SUMS_E03.txt"),
]
for index, (row, values) in enumerate(zip(result_rows, results), start=1):
    cells = row.findall(W + "tc")
    for cell, value in zip(cells, (str(index), *values)):
        set_cell_text(cell, value)

package["word/document.xml"] = ET.tostring(
    root, encoding="UTF-8", xml_declaration=True, standalone=True
)

destination.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
    for name, content in package.items():
        archive.writestr(name, content)

print(destination)
