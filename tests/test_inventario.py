import csv
import os
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))

from inventario import gerar_inventario  # noqa: E402


def test_gerar_inventario_campos(tmp_path):
    drive = tmp_path / "HD"
    (drive / "Fotos").mkdir(parents=True)
    arquivo = drive / "Fotos" / "img.jpg"
    arquivo.write_text("x")

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        gerar_inventario(drive, calcular_hashes=False)
    finally:
        os.chdir(cwd)

    csv_path = tmp_path / "saida_inventarios" / f"{drive.name}_inventario.csv"
    assert csv_path.exists()

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row = next(reader)

    expected_fields = [
        "caminho",
        "tamanho",
        "data_modificacao",
        "data_criacao",
        "extensao",
        "drive",
        "dir_pai",
    ]
    assert reader.fieldnames == expected_fields
    assert row["extensao"] == ".jpg"
    assert row["dir_pai"] == "Fotos"
    assert row["drive"] == str(drive)
