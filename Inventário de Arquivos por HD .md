1. Inventário de Arquivos por HD (.txt por disco)
 O primeiro passo é percorrer cada HD e coletar os metadados de todos os arquivos, salvando um
 inventário por disco em formato texto (p. ex. um 
.txt ou 
.csv por HD). Cada entrada deve conter
 pelo menos: nome completo do arquivo, caminho (relativo ao ponto de montagem do HD), tamanho em
 bytes, data de modificação e opcionalmente um hash de conteúdo (MD5, SHA-1/256, etc.). 
• 
Recursão pelo diretório: Em Python, pode-se usar 
os.walk() ou 
para varrer recursivamente cada pasta do HD. Exemplo simplificado: 
pathlib.Path.rglob()
 import os
 for root, dirs, files in os.walk('D:/'): # supondo D: como raiz do HD
 for fname in files:
 filepath = os.path.join(root, fname)
 info = os.stat(filepath)
 # extrair info.st_size (tamanho), info.st_mtime (timestamp 
modificação)
 # calcular hash se necessário
 # escrever linha no arquivo de inventário
 Essa lógica percorre todas as pastas e arquivos a partir da raiz do drive (como 
D:/ no Windows ou /
 mnt/hd1 no Linux) e coleta as informações desejadas. Em um cenário multiplataforma, 
pathlib
 pode melhorar a legibilidade (por exemplo, 
Path(root) / fname e métodos como
 .stat() , 
.is_file() etc.). 
• 
Escrita em arquivo de inventário: Conforme cada arquivo é encontrado, escreva uma linha no
 relatório de texto do respectivo HD. Idealmente, use um delimitador claro (vírgula, ponto-e
vírgula ou tabulação) para separar campos como nome, caminho e atributos. Por exemplo,
 pode-se usar o módulo 
csv do Python para garantir o escape correto de caracteres especiais
 no nome ou caminho. Cada HD terá seu próprio arquivo (e.g., 
inventario_HD1.csv , 
inventario_HD2.csv , etc.), facilitando tanto consultas individuais quanto mesclar depois se
 necessário.
 1
• 
1
 Hash opcional de conteúdo: O cálculo do hash (como MD5 ou SHA256) de cada arquivo permite
 identificar duplicatas exatas posteriormente. Entretanto, isso é custoso (leitura completa de cada
 arquivo). Uma estratégia é tornar opcional ou diferido – por exemplo, gerar inicialmente o
 inventário só com nome, caminho, tamanho e data, e calcular hashes numa segunda fase
 apenas para arquivos candidatos a duplicatas (com base em nome ou tamanho iguais).
 Abordagens mais eficientes de deduplicação serão detalhadas na seção de desempenho.
 Confirmando práticas conhecidas: Ferramentas de catalogação de mídia, como o projeto open-source
 CatCLI, seguem lógica semelhante ao criar um índice offline de arquivos de discos externos. O CatCLI
 armazena para cada arquivo atributos como caminho, tamanho e hash MD5, permitindo busca posterior
 . Esse inventário pode ser salvo em formatos simples como JSON ou CSV – o CatCLI, por exemplo,
 suporta exportar o catálogo para JSON (facilitando versionamento em git) ou CSV . Isso reforça a
 viabilidade de nossa abordagem de gerar um inventário completo por disco, com dados necessários
 para futuras análises.
