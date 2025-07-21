# Organizador HD

Ferramenta em Python para gerar inventários de arquivos de discos.

## Requisitos

- Python 3.11+
- Dependências listadas em `requirements.txt`

Instale as dependências com:

```bash
pip install -r requirements.txt
```

## Uso

Execute o script `inventario.py` informando o caminho do drive a ser catalogado.

```bash
python src/inventario.py --drive /caminho/do/drive
```

Para calcular o hash MD5 de cada arquivo, utilize a flag `--hash`:

```bash
python src/inventario.py --drive /caminho/do/drive --hash
```

Os arquivos CSV serão criados em `saida_inventarios/`. Cada execução gera um log
em `logs/`.

### Exemplos por sistema operacional

Windows:

```cmd
python src\inventario.py --drive D:\ --hash
```

macOS/Linux:

```bash
python src/inventario.py --drive /mnt/MEU_HD --hash
```

## Estrutura

```
Organizador_hd/
├── src/
│   ├── inventario.py
│   └── utils.py
├── saida_inventarios/
├── logs/
└── requirements.txt
```
