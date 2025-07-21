import hashlib
from pathlib import Path
import sys

# Permitir importacao do modulo src
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))

from utils import calcular_hash  # noqa: E402


def test_calcular_hash(tmp_path):
    """Valida o hash MD5 calculado."""
    arquivo = tmp_path / "teste.txt"
    conteudo = b"exemplo"
    arquivo.write_bytes(conteudo)

    esperado = hashlib.md5(conteudo).hexdigest()
    obtido = calcular_hash(arquivo)

    assert obtido == esperado
