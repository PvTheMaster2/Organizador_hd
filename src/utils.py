from pathlib import Path
from typing import Iterator
import hashlib
from tqdm import tqdm


def listar_arquivos(diretorio: Path) -> Iterator[Path]:
    """Itera recursivamente pelos arquivos em ``diretorio``.

    Parameters
    ----------
    diretorio : Path
        Caminho base a ser percorrido.

    Yields
    ------
    Iterator[Path]
        Caminhos de arquivos encontrados.
    """
    for caminho in tqdm(diretorio.rglob("*"), desc="Listando", unit="arq"):
        if caminho.is_file():
            yield caminho


def calcular_hash(arquivo: Path, bloco: int = 8192) -> str:
    """Calcula o hash MD5 de ``arquivo``.

    Parameters
    ----------
    arquivo : Path
        Arquivo para leitura dos bytes.
    bloco : int, optional
        Tamanho do bloco de leitura, por padrao ``8192``.

    Returns
    -------
    str
        Hash em hexadecimal.
    """
    md5 = hashlib.md5()
    with arquivo.open("rb") as f:
        for parte in iter(lambda: f.read(bloco), b""):
            md5.update(parte)
    return md5.hexdigest()
