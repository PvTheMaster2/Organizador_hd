"""Gera inventários de arquivos de um drive."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from datetime import datetime

from tqdm import tqdm

from utils import listar_arquivos, calcular_hash


def _criar_parser() -> argparse.ArgumentParser:
    """Retorna um ArgumentParser configurado."""
    parser = argparse.ArgumentParser(
        description="Mapeia arquivos em um drive e salva em CSV"
    )
    parser.add_argument(
        "--drive",
        required=True,
        help="Caminho do drive a ser inventariado",
    )
    parser.add_argument(
        "--hash",
        action="store_true",
        help="Calcula o hash MD5 de cada arquivo",
    )
    return parser


def gerar_inventario(caminho_drive: Path, calcular_hashes: bool = False) -> None:
    """Percorre o drive e gera o CSV correspondente.

    Parameters
    ----------
    caminho_drive : Path
        Diretorio do drive.
    calcular_hashes : bool, optional
        Se ``True``, calcula o hash dos arquivos.
    """
    saida = Path("saida_inventarios")
    saida.mkdir(exist_ok=True)
    nome = caminho_drive.name or "drive"
    csv_path = saida / f"{nome}_inventario.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        cabecalho = ["caminho", "tamanho", "data_modificacao"]
        if calcular_hashes:
            cabecalho.append("hash_md5")
        writer.writerow(cabecalho)

        for arquivo in tqdm(listar_arquivos(caminho_drive)):
            stat = arquivo.stat()
            linha = [
                str(arquivo.relative_to(caminho_drive)),
                stat.st_size,
                datetime.fromtimestamp(stat.st_mtime).isoformat(),
            ]
            if calcular_hashes:
                linha.append(calcular_hash(arquivo))
            writer.writerow(linha)


if __name__ == "__main__":
    args = _criar_parser().parse_args()
    gerar_inventario(Path(args.drive), args.hash)
