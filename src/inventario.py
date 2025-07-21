"""Gera inventários de arquivos de um drive."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from concurrent.futures import ProcessPoolExecutor

from utils import listar_arquivos, calcular_hash


def _configurar_logging() -> None:
    """Configura o logging com rotacao diaria."""
    logs = Path("logs")
    logs.mkdir(exist_ok=True)
    handler = TimedRotatingFileHandler(
        logs / "inventario.log",
        when="midnight",
        backupCount=7,
        encoding="utf-8",
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[handler, logging.StreamHandler()],
    )


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
    logger = logging.getLogger(__name__)
    logger.info("Gerando invent\u00e1rio de %s", caminho_drive)
    saida = Path("saida_inventarios")
    saida.mkdir(exist_ok=True)
    nome = caminho_drive.name or "drive"
    csv_path = saida / f"{nome}_inventario.csv"

    arquivos = list(listar_arquivos(caminho_drive))

    with csv_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        cabecalho = ["caminho", "tamanho", "data_modificacao"]
        if calcular_hashes:
            cabecalho.append("hash_md5")
        writer.writerow(cabecalho)

        if calcular_hashes:
            with ProcessPoolExecutor(max_workers=1) as executor:
                for arquivo, md5 in zip(arquivos, executor.map(calcular_hash, arquivos)):
                    stat = arquivo.stat()
                    linha = [
                        str(arquivo.relative_to(caminho_drive)),
                        stat.st_size,
                        datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        md5,
                    ]
                    writer.writerow(linha)
        else:
            for arquivo in arquivos:
                stat = arquivo.stat()
                linha = [
                    str(arquivo.relative_to(caminho_drive)),
                    stat.st_size,
                    datetime.fromtimestamp(stat.st_mtime).isoformat(),
                ]
                writer.writerow(linha)

    logger.info("Invent\u00e1rio salvo em %s", csv_path)


if __name__ == "__main__":
    _configurar_logging()
    args = _criar_parser().parse_args()
    gerar_inventario(Path(args.drive), args.hash)
