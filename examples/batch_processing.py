"""
Procesamiento por lotes de múltiples CFDIs.

El PDF generado siempre se nombra con el UUID del timbre fiscal
(``{uuid}.pdf``), así que no se puede elegir el nombre de salida.
"""

from pathlib import Path

from cfdi_pdf import CFDIPDF


def batch_conversion_basic() -> None:
    """Conversión por lotes básica."""
    pdf = CFDIPDF(template="minimal")

    xml_dir = Path("./facturas")
    output_dir = Path("./pdfs")
    output_dir.mkdir(exist_ok=True)

    xml_files = list(xml_dir.glob("*.xml"))
    print(f"Encontrados {len(xml_files)} archivos XML")

    success = 0
    errors = 0

    for xml_file in xml_files:
        try:
            output_path = pdf.render(xml_path=xml_file, output_dir=output_dir)
            print(f"✓ {xml_file.name} -> {output_path.name}")
            success += 1
        except Exception as exc:
            print(f"✗ {xml_file.name}: {exc}")
            errors += 1

    print(f"\nResumen: {success} exitosos, {errors} errores")


def batch_conversion_with_progress() -> None:
    """Conversión por lotes con barra de progreso."""
    try:
        from tqdm import tqdm
    except ImportError:
        print("Instala tqdm para barra de progreso: pip install tqdm")
        return

    pdf = CFDIPDF()

    xml_dir = Path("./facturas")
    output_dir = Path("./pdfs")
    output_dir.mkdir(exist_ok=True)

    xml_files = list(xml_dir.glob("*.xml"))
    print(f"Procesando {len(xml_files)} archivos...")

    success = 0
    errors = 0

    for xml_file in tqdm(xml_files, desc="Convirtiendo"):
        try:
            pdf.render(xml_path=xml_file, output_dir=output_dir)
            success += 1
        except Exception:
            errors += 1

    print(f"\nCompletado: {success} exitosos, {errors} errores")


def batch_conversion_parallel() -> None:
    """Conversión por lotes en paralelo (multiprocesamiento)."""
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor

    def convert_file(xml_path: Path, output_dir: Path) -> tuple[str, bool, str]:
        """Convertir un archivo individual."""
        try:
            pdf = CFDIPDF()
            output_path = pdf.render(xml_path=xml_path, output_dir=output_dir)
            return (xml_path.name, True, output_path.name)
        except Exception as exc:
            return (xml_path.name, False, str(exc))

    xml_dir = Path("./facturas")
    output_dir = Path("./pdfs")
    output_dir.mkdir(exist_ok=True)

    xml_files = list(xml_dir.glob("*.xml"))
    print(f"Procesando {len(xml_files)} archivos en paralelo...")

    num_workers = multiprocessing.cpu_count()
    print(f"Usando {num_workers} procesos")

    success = 0
    errors = 0

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(convert_file, xml_path, output_dir) for xml_path in xml_files]
        for future in futures:
            filename, is_success, detail = future.result()
            if is_success:
                print(f"✓ {filename} -> {detail}")
                success += 1
            else:
                print(f"✗ {filename}: {detail}")
                errors += 1

    print(f"\nResumen: {success} exitosos, {errors} errores")


def batch_with_error_report() -> None:
    """Conversión por lotes con reporte de errores."""
    pdf = CFDIPDF()

    xml_dir = Path("./facturas")
    output_dir = Path("./pdfs")
    output_dir.mkdir(exist_ok=True)

    xml_files = list(xml_dir.glob("*.xml"))
    results = []

    for xml_file in xml_files:
        try:
            output_path = pdf.render(xml_path=xml_file, output_dir=output_dir)
            results.append(
                {
                    "file": xml_file.name,
                    "status": "success",
                    "output": output_path.name,
                    "error": None,
                }
            )
        except Exception as exc:
            results.append(
                {"file": xml_file.name, "status": "error", "output": None, "error": str(exc)}
            )

    success = [r for r in results if r["status"] == "success"]
    errors = [r for r in results if r["status"] == "error"]

    print(f"\n{'=' * 60}")
    print("REPORTE DE CONVERSIÓN")
    print(f"{'=' * 60}")
    print(f"Total procesados: {len(results)}")
    print(f"Exitosos: {len(success)}")
    print(f"Errores: {len(errors)}")

    if errors:
        print(f"\n{'=' * 60}")
        print("DETALLE DE ERRORES")
        print(f"{'=' * 60}")
        for error in errors:
            print(f"\nArchivo: {error['file']}")
            print(f"Error: {error['error']}")

    report_file = output_dir / "conversion_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("Reporte de Conversión\n")
        f.write(f"{'=' * 60}\n\n")
        f.write(f"Total: {len(results)}\n")
        f.write(f"Exitosos: {len(success)}\n")
        f.write(f"Errores: {len(errors)}\n\n")

        if errors:
            f.write(f"\n{'=' * 60}\n")
            f.write("ERRORES\n")
            f.write(f"{'=' * 60}\n\n")
            for error in errors:
                f.write(f"Archivo: {error['file']}\n")
                f.write(f"Error: {error['error']}\n\n")

    print(f"\nReporte guardado en: {report_file}")


if __name__ == "__main__":
    print("=== Conversión por Lotes Básica ===")
    print("Nota: Requiere archivos XML en ./facturas/")
    # batch_conversion_basic()

    print("\n=== Conversión con Barra de Progreso ===")
    print("Requiere: pip install tqdm")
    # batch_conversion_with_progress()

    print("\n=== Conversión en Paralelo ===")
    # batch_conversion_parallel()

    print("\n=== Conversión con Reporte de Errores ===")
    # batch_with_error_report()
