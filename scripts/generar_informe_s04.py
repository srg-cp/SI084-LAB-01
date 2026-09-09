"""Genera el informe DOCX del Taller 04 desde la plantilla oficial del curso."""

from copy import deepcopy
from pathlib import Path
import struct
import sys
import zipfile

from lxml import etree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{" + W_NS + "}"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC_NS = "http://schemas.openxmlformats.org/drawingml/2006/picture"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


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


def has_page_break(paragraph):
    return any(
        node.tag == W + "br" and node.get(W + "type") == "page"
        for node in paragraph.iter()
    )


def remove_instruction_page(body):
    """Retira la página 'Cómo se usa esta plantilla' y conserva el salto anterior."""
    heading = find_paragraph(body, "Cómo se usa esta plantilla")
    start = list(body).index(heading)
    end = start
    for index, child in enumerate(list(body)[start + 1 :], start + 1):
        end = index
        if child.tag == W + "p" and has_page_break(child):
            break
    for child in list(body)[start : end + 1]:
        body.remove(child)


def insert_before_section(body, element):
    section = body.find(W + "sectPr")
    body.insert(list(body).index(section), element)


def plain_paragraph(text, *, centered=False, page_break=False):
    paragraph = ET.Element(W + "p")
    if centered:
        properties = ET.SubElement(paragraph, W + "pPr")
        justification = ET.SubElement(properties, W + "jc")
        justification.set(W + "val", "center")
    run = ET.SubElement(paragraph, W + "r")
    if page_break:
        page = ET.SubElement(run, W + "br")
        page.set(W + "type", "page")
    if text:
        node = ET.SubElement(run, W + "t")
        node.text = text
    return paragraph


def png_extent(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("La captura no es un PNG válido")
    width, height = struct.unpack(">II", data[16:24])
    cx, cy = width * 9525, height * 9525
    max_width, max_height = 5_943_600, 4_114_800
    scale = min(max_width / cx, max_height / cy, 1)
    return int(cx * scale), int(cy * scale)


def image_paragraph(relationship_id, name, data, drawing_id):
    cx, cy = png_extent(data)
    paragraph = ET.Element(W + "p")
    properties = ET.SubElement(paragraph, W + "pPr")
    justification = ET.SubElement(properties, W + "jc")
    justification.set(W + "val", "center")
    run = ET.SubElement(paragraph, W + "r")
    drawing = ET.SubElement(run, W + "drawing")
    inline = ET.SubElement(drawing, "{" + WP_NS + "}inline")
    inline.set("distT", "0")
    inline.set("distB", "0")
    inline.set("distL", "0")
    inline.set("distR", "0")
    extent = ET.SubElement(inline, "{" + WP_NS + "}extent")
    extent.set("cx", str(cx))
    extent.set("cy", str(cy))
    doc_properties = ET.SubElement(inline, "{" + WP_NS + "}docPr")
    doc_properties.set("id", str(drawing_id))
    doc_properties.set("name", name)
    frame = ET.SubElement(inline, "{" + WP_NS + "}cNvGraphicFramePr")
    locks = ET.SubElement(frame, "{" + A_NS + "}graphicFrameLocks")
    locks.set("noChangeAspect", "1")
    graphic = ET.SubElement(inline, "{" + A_NS + "}graphic")
    graphic_data = ET.SubElement(graphic, "{" + A_NS + "}graphicData")
    graphic_data.set("uri", "http://schemas.openxmlformats.org/drawingml/2006/picture")
    picture = ET.SubElement(graphic_data, "{" + PIC_NS + "}pic")
    non_visual = ET.SubElement(picture, "{" + PIC_NS + "}nvPicPr")
    picture_properties = ET.SubElement(non_visual, "{" + PIC_NS + "}cNvPr")
    picture_properties.set("id", "0")
    picture_properties.set("name", name)
    ET.SubElement(non_visual, "{" + PIC_NS + "}cNvPicPr")
    fill = ET.SubElement(picture, "{" + PIC_NS + "}blipFill")
    blip = ET.SubElement(fill, "{" + A_NS + "}blip")
    blip.set("{" + R_NS + "}embed", relationship_id)
    stretch = ET.SubElement(fill, "{" + A_NS + "}stretch")
    ET.SubElement(stretch, "{" + A_NS + "}fillRect")
    shape = ET.SubElement(picture, "{" + PIC_NS + "}spPr")
    transform = ET.SubElement(shape, "{" + A_NS + "}xfrm")
    offset = ET.SubElement(transform, "{" + A_NS + "}off")
    offset.set("x", "0")
    offset.set("y", "0")
    size = ET.SubElement(transform, "{" + A_NS + "}ext")
    size.set("cx", str(cx))
    size.set("cy", str(cy))
    geometry = ET.SubElement(shape, "{" + A_NS + "}prstGeom")
    geometry.set("prst", "rect")
    ET.SubElement(geometry, "{" + A_NS + "}avLst")
    return paragraph


def append_evidence_images(body, package, project):
    captures = [
        ("01_entorno_docker_operativo.png", "Figura 1. Entorno Docker si084-lab con siete contenedores operativos."),
        ("02_lynis_indice_y_sugerencias.png", "Figura 2. Índice de endurecimiento y sugerencias priorizadas de Lynis."),
        ("03_openscap_reglas_fallidas.png", "Figura 3. Reglas XCCDF fallidas obtenidas con OpenSCAP."),
        ("04_docker_bench_advertencias.png", "Figura 4. Advertencias de Docker Bench en las secciones 4 y 5."),
        ("05_trivy_resumen.png", "Figura 5. Resumen de vulnerabilidades y detecciones de Trivy."),
        ("06_matriz_validacion.png", "Figura 6. Validación del porcentaje de hallazgos sin clasificar."),
    ]
    relationship_name = "word/_rels/document.xml.rels"
    relationships = ET.fromstring(package[relationship_name])
    content_types = ET.fromstring(package["[Content_Types].xml"])
    if not any(node.get("Extension", "").lower() == "png" for node in content_types):
        default = ET.SubElement(content_types, "{" + CT_NS + "}Default")
        default.set("Extension", "png")
        default.set("ContentType", "image/png")

    insert_before_section(body, plain_paragraph("", page_break=True))
    insert_before_section(body, plain_paragraph("Anexo E — Capturas numeradas", centered=True))
    evidence_dir = project / "docs" / "evidencias" / "S04"
    for index, (file_name, caption) in enumerate(captures, 1):
        path = evidence_dir / file_name
        data = path.read_bytes()
        relationship_id = f"rIdS04Image{index:02d}"
        media_name = f"s04_{index:02d}.png"
        relationship = ET.SubElement(relationships, "{" + REL_NS + "}Relationship")
        relationship.set("Id", relationship_id)
        relationship.set(
            "Type",
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
        )
        relationship.set("Target", f"media/{media_name}")
        package[f"word/media/{media_name}"] = data
        insert_before_section(body, plain_paragraph(caption, centered=True))
        insert_before_section(
            body,
            image_paragraph(relationship_id, file_name, data, 900 + index),
        )
        insert_before_section(
            body,
            plain_paragraph(
                "Fuente: evidencia obtenida durante la ejecución del Taller 04.",
                centered=True,
            ),
        )

    package[relationship_name] = ET.tostring(
        relationships, encoding="UTF-8", xml_declaration=True, standalone=True
    )
    package["[Content_Types].xml"] = ET.tostring(
        content_types, encoding="UTF-8", xml_declaration=True, standalone=True
    )


source = Path(sys.argv[1])
destination = Path(sys.argv[2])
student_code = sys.argv[3] if len(sys.argv) > 3 else "2022073503"

with zipfile.ZipFile(source) as archive:
    document_xml = archive.read("word/document.xml")
    package = {name: archive.read(name) for name in archive.namelist()}

root = ET.fromstring(document_xml)
body = root.find(W + "body")
remove_instruction_page(body)

replacements = {
    "INFORME DE LABORATORIO N.º ____": "INFORME DE LABORATORIO N.º 04",
    "Título del taller": "Auditoría de configuración segura con Lynis, OpenSCAP, Docker Bench y Trivy",
    "Semana N.º ____ · Unidad ____ · Grupo N.º ____": "Semana N.º 04 · Unidad I · Grupo N.º COLQUE",
    "Haz clic derecho aquí y elige «Actualizar campos» para generar el índice.": (
        "Actualice este índice en Word antes de exportar el PDF."
    ),
    "Reglas de uso del laboratorio y de alcance que se respetaron durante el trabajo.": (
        "La auditoría se limitó al equipo propio y al entorno Docker local si084-lab. No se analizaron "
        "equipos del campus ni sistemas de terceros. Los originales confidenciales se conservaron fuera "
        "de Git y la versión publicable fue saneada antes de su registro."
    ),
    "Cada paso lleva su título, qué se buscaba, el comando o la acción, y la evidencia de que funcionó. Quien lea el informe debe poder repetir el trabajo sin preguntar nada.": (
        "Se ejecutaron cuatro herramientas con un guion reproducible, se conservaron sus salidas primarias, "
        "se consolidaron 294 registros y se validó cada asociación normativa. Las URL de la etiqueta "
        "taller-04 permiten rastrear los resultados hasta su evidencia."
    ),
    "Paso A": "Paso A — Auditoría del sistema con Lynis",
    "Paso B": "Paso B — Evaluación formal con OpenSCAP",
    "Paso C": "Paso C — Revisión CIS de Docker",
    "Si algo no se logró, explícalo aquí. Un resultado no alcanzado y bien explicado vale más que uno declarado sin evidencia.": (
        "La imagen de Lynis indicada por la guía no estaba publicada y Ubuntu 22.04 no ofrecía "
        "ssg-debderived; se aplicaron alternativas oficiales y reproducibles. OpenSCAP produjo 15 fallos "
        "Medios y ningún fallo Alto, por lo que se documentó la limitación sin alterar la severidad. "
        "Antes de versionar se redactaron 51 elementos sensibles detectados por Trivy."
    ),
    "Mínimo tres. Una conclusión no resume lo que hiciste. Dice lo que aprendiste y se sostiene en la evidencia de la sección 3.": (
        "1. La matriz única convirtió 294 registros técnicos heterogéneos en evidencia trazable contra "
        "ISO/IEC 27001:2022 y COBIT 2019.\n"
        "2. La revisión manual corrigió asociaciones ambiguas y redujo a 0,0 % los hallazgos sin clasificar.\n"
        "3. La ausencia de límites de recursos en la IaC y en ejecución demuestra una deficiencia de diseño "
        "de A.8.6, que exige construir el control antes de medir su eficacia.\n"
        "4. Sanear secretos y datos del anfitrión antes de publicar forma parte de la custodia de evidencia.\n"
        "5. Documentar que OpenSCAP no produjo fallos Altos conserva más valor probatorio que alterar el resultado."
    ),
    "Copia cada pregunta de la guía de la semana y respóndela debajo.": (
        "La guía del Taller 04 no presenta un cuestionario independiente. La pregunta de transferencia se "
        "responde así: una organización que no consolida ni valida los reportes puede priorizar duplicados, "
        "ignorar controles ausentes y exponer información sensible al publicar la evidencia sin saneamiento."
    ),
    "Normas técnicas, marcos profesionales, documentación oficial y bibliografía indexada, en formato APA. No se admiten wikis abiertas ni sitios sin autoría verificable.": (
        "ISO. (2022). ISO/IEC 27001:2022. https://www.iso.org/standard/27001\n"
        "ISO. (2022). ISO/IEC 27002:2022. https://www.iso.org/standard/75652.html\n"
        "ISACA. (2018). COBIT 2019 Framework. https://www.isaca.org/resources/cobit\n"
        "Center for Internet Security. CIS Benchmarks. https://www.cisecurity.org/cis-benchmarks\n"
        "CISOfy. Lynis. https://cisofy.com/lynis/\n"
        "OpenSCAP Project. https://www.open-scap.org/\n"
        "ComplianceAsCode. https://github.com/ComplianceAsCode/content\n"
        "Aqua Security. Trivy Documentation. https://trivy.dev/"
    ),
    "Capturas completas, archivos de configuración y salidas extensas. Cada anexo lleva su letra y su título, y se menciona en el cuerpo del informe.": (
        "Anexo A — Reporte OpenSCAP HTML y XML.\n"
        "Anexo B — Matriz consolidada PT04 con 294 registros.\n"
        "Anexo C — SBOM CycloneDX de Juice Shop.\n"
        "Anexo D — Análisis de diseño frente a eficacia operativa.\n"
        "Anexo E — Capturas numeradas 01 a 06.\n"
        "Anexo F — Hashes y cadena de custodia.\n"
        "Etiqueta: https://github.com/srg-cp/SI084-LAB-01/tree/taller-04\n"
        "Pull Request a develop: https://github.com/srg-cp/SI084-LAB-01/pull/1"
    ),
}

for child in body:
    if child.tag == W + "p":
        current = paragraph_text(child).strip()
        if current in replacements:
            set_paragraph_text(child, replacements[current])

integrantes = find_paragraph(body, "Integrantes")
body.insert(
    list(body).index(integrantes) + 1,
    plain_paragraph(f"SERGIO COLQUE PONCE · Código: {student_code}"),
)

paragraph_template = find_paragraph(
    body,
    "La guía del Taller 04 no presenta un cuestionario independiente. La pregunta de transferencia se "
    "responde así: una organización que no consolida ni valida los reportes puede priorizar duplicados, "
    "ignorar controles ausentes y exponer información sensible al publicar la evidencia sin saneamiento.",
)

section_content = {
    "1.1 Título del evento práctico": [
        "Evaluación automatizada de controles generales de TI mediante herramientas libres de auditoría de "
        "configuración, contrastando evidencia técnica con CIS Benchmarks, ISO/IEC 27001:2022 y COBIT 2019."
    ],
    "1.2 Objetivos": [
        "• Auditar el endurecimiento con Lynis y el cumplimiento formal con OpenSCAP.",
        "• Revisar el plano de contenedores mediante Docker Bench for Security.",
        "• Identificar vulnerabilidades, configuraciones IaC, secretos y componentes mediante Trivy.",
        "• Consolidar y validar una matriz mapeada a ISO/IEC 27001:2022 y COBIT 2019.",
        "• Diferenciar una deficiencia de diseño de una de eficacia operativa.",
    ],
    "1.3 Tiempo de duración": [
        "100 minutos de laboratorio guiado y tiempo adicional de descarga, revisión y documentación."
    ],
    "1.4 Resultados de aprendizaje": [
        "RA1: analiza e interpreta conceptos y terminología de Auditoría de Sistemas.",
        "RA2: evalúa la seguridad de la información en Auditoría de Sistemas.",
    ],
}

for heading, paragraphs in section_content.items():
    insert_after(body, find_paragraph(body, heading), paragraphs, paragraph_template)

step_content = {
    "Paso A — Auditoría del sistema con Lynis": [
        "Al no estar disponible cisofy/lynis:latest, se construyó si084/lynis:official desde el repositorio "
        "oficial CISOfy/lynis-docker. El reporte obtuvo un índice de endurecimiento 53 y 28 sugerencias; se "
        "priorizaron AUTH-9262, FIRE-4590 y ACCT-9628."
    ],
    "Paso B — Evaluación formal con OpenSCAP": [
        "Se evaluó el perfil CIS Level 1 Server con el data stream oficial de Ubuntu 22.04 de "
        "ComplianceAsCode 0.1.77. Hubo 15 reglas fallidas de severidad Media y ninguna Alta."
    ],
    "Paso C — Revisión CIS de Docker": [
        "Docker Bench inspeccionó siete contenedores y generó 105 advertencias. En las secciones 4 y 5 se "
        "observaron ejecución como root, sistemas raíz escribibles y ausencia de límites y healthchecks."
    ],
}

for heading, paragraphs in step_content.items():
    insert_after(body, find_paragraph(body, heading), paragraphs, paragraph_template)

section_three = find_paragraph(body, "3. Resultados")
heading_template = deepcopy(find_paragraph(body, "Paso C — Revisión CIS de Docker"))
position = list(body).index(section_three)

for heading, paragraphs in [
    (
        "Paso D — Vulnerabilidades, IaC, secretos y SBOM con Trivy",
        [
            "Se analizaron cuatro imágenes, la carpeta entorno, los secretos del repositorio y un SBOM "
            "CycloneDX. Se obtuvieron 141 vulnerabilidades —8 críticas y 133 altas— y 5 detecciones de "
            "secretos con sus valores omitidos en la versión publicable."
        ],
    ),
    (
        "Paso E — Consolidación, validación y sellado",
        [
            "PT04_matriz_control.py consolidó 294 registros: Docker Bench 105, Lynis 28, OpenSCAP 15, "
            "Trivy 141 y Trivy Secret 5. La revisión final dejó 0 hallazgos sin clasificar (0,0 %) y los "
            "artefactos se sellaron con SHA-256."
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

insert_after(
    body,
    section_three,
    [
        "La versión verificable se encuentra en https://github.com/srg-cp/SI084-LAB-01/tree/taller-04. "
        "El índice de evidencias está en docs/evidencias/S04/README.md.",
        "El control A.8.6 se clasificó como deficiencia de diseño: la IaC no define límites de memoria, CPU "
        "o PID ni healthchecks, y Docker Bench confirmó la misma ausencia en ejecución.",
    ],
    paragraph_template,
)

tables = [child for child in body if child.tag == W + "tbl"]
resource_rows = tables[0].findall(W + "tr")[1:]
resource_data = [
    ("Docker Desktop y Docker Compose", "Cliente y motor 28.0.4", "Entorno local y acceso a contenedores"),
    ("Lynis, OpenSCAP y Docker Bench", "Lynis oficial; ComplianceAsCode 0.1.77", "Auditoría de configuración y cumplimiento"),
    ("Trivy y Python", "Trivy latest; Python 3.11", "Escaneo, SBOM, consolidación y validación"),
]
for row, values in zip(resource_rows, resource_data):
    for cell, value in zip(row.findall(W + "tc"), values):
        set_cell_text(cell, value)

result_rows = tables[1].findall(W + "tr")[1:]
results = [
    ("Lynis con índice y tres observaciones priorizadas", "Logrado", "Índice 53; captura 02 y lynis-report.dat"),
    ("OpenSCAP con perfil y reglas XCCDF", "Logrado con limitación", "15 fallos Medios; 0 Altos; captura 03"),
    ("Docker Bench, conteo y secciones 4–5", "Logrado", "105 WARN; captura 04 y docker-bench.log"),
    ("Trivy: imágenes, IaC, secretos y SBOM", "Logrado", "141 vulnerabilidades, 5 secretos redactados; captura 05"),
    ("Matriz única ISO/IEC 27001 y COBIT 2019", "Logrado", "294 registros en PT04_matriz_control.csv"),
    ("Menos de 20 % sin clasificar", "Logrado", "0 de 294 (0,0 %); captura 06"),
    ("Diseño frente a eficacia operativa", "Logrado", "A.8.6: deficiencia de diseño"),
    ("Hashes, cadena de custodia y commit", "Logrado localmente", "SHA256SUMS_E04.txt y CADENA_DE_CUSTODIA.md"),
]
for index, (row, values) in enumerate(zip(result_rows, results), start=1):
    cells = row.findall(W + "tc")
    for cell, value in zip(cells, (str(index), *values)):
        set_cell_text(cell, value)

append_evidence_images(body, package, source.resolve().parents[1] / "auditoria-si084")

package["word/document.xml"] = ET.tostring(
    root, encoding="UTF-8", xml_declaration=True, standalone=True
)

destination.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
    for name, content in package.items():
        archive.writestr(name, content)

print(destination)
