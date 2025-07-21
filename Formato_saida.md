 A escolha do formato do inventário impacta diretamente a facilidade de processar os dados depois,
 especialmente para identificar arquivos duplicados entre os discos. Boas práticas:
 • 
CSV / TSV estruturado: Um arquivo de valores separados por vírgula (CSV) ou tab (TSV) por HD é
 uma ótima escolha. Cada linha representa um arquivo com colunas fixas, por exemplo:
 "nome_arquivo","caminho_relativo","tamanho_bytes","data_modificacao","hash_md5"
 Foto123.jpg,"/Fotos/Viagem/",1532453,"2020-05-10 14:33:22","abcdef123456..."
 ...
 Esse formato tabular permite facilmente concatenar todos os inventários dos 5 HDs em um só (basta
 juntar os arquivos ou usar um script para tal) e então usar filtros ou fórmulas para achar duplicatas. Por
 exemplo, no Excel/LibreOffice, pode-se ordenar por nome e tamanho para ver coincidências, ou em
 6
Python usar pandas: 
df = pandas.read_csv("all_inventories.csv") e então agrupar por hash
 ou nome.
 • 
• 
• 
• 
• 
• 
• 
Inclua uma coluna identificando o HD de origem, caso decida unir tudo num arquivo. Pode ser
 explícito (uma coluna "HD") ou implicitamente pelo nome do arquivo CSV. Ter essa identificação
 facilita saber onde está cada cópia de um arquivo duplicado.
 O hash de conteúdo é a chave para deduplicação precisa. Portanto, se o desempenho permitir,
 tenha uma coluna de hash (MD5, SHA256 ou outro) calculado para cada arquivo. Assim, a
 comparação de duplicatas vira uma simples comparação de strings hash. Se optou por não
 computar todos os hashes durante o inventário (devido ao tempo), pode fazer um inventário
 inicial sem hash e depois um passo adicional para calcular hashes só dos candidatos (por ex.,
 arquivos com mesmo tamanho).
 JSON: É possível usar JSON para armazenar o inventário, por exemplo, uma lista de objetos
 {hd: "HD1", path: "/Fotos/Foto123.jpg", size: 1532453, mtime: 
"2020-05-10T14:33:22", hash: "abcdef123456"} . O JSON tem a vantagem de ser auto
descritivo (chaves nomeadas) e flexível com tipos, além de ser facilmente consumido por scripts
 em diversas linguagens. No entanto, para milhões de arquivos, um único JSON gigante fica
 pesado e difícil até de abrir em editores comuns. CSV acaba sendo mais enxuto e simples para
 esse volume de dados.
 Uma ideia intermediária: JSONL (JSON Lines), onde cada linha do arquivo é um objeto JSON
 separado. Isso combina a estruturada do JSON com a simplicidade de processamento linha-a
linha do CSV. Ferramentas de Big Data gostam desse formato. Mas a menos que planeje usar
 algo como Elasticsearch ou MongoDB depois, talvez seja overkill. 
SQLite ou outro banco local: Em vez de arquivos texto, poderia-se inserir todos registros em
 um banco de dados SQLite local. A vantagem: permite consultas SQL para achar duplicatas
 (SELECT
 * FROM inventario WHERE hash = 'X' ). E o SQLite lida com milhões de registros
 tranquilamente, com um único arquivo 
.sqlite como resultado. No entanto, isso complica a
 etapa de geração (usar bibliotecas SQL ou 
INSERT continuamente) e dificulta a inspeção
 manual simples. Se o foco é automação e volume, SQLite é interessante; se o foco é
 transparência e facilidade de auditoria, CSV/texto é preferível. Como o pedido foi inventário
 em 
.txt , manteremos texto como padrão.
 Formato de data/hora: Ao escrever a data de modificação, escolha um formato claro e
 consistente. ISO 8601 (
 YYYY-MM-DDTHH:MM:SS ) é uma boa opção, ou mesmo timestamp Unix
 (número de segundos desde 1970) para facilitar comparações programáticas. Só não misture
 formatos diferentes. E cuidado com timezone – idealmente normalize para UTC ou indique o
 fuso se for local.
 Delimitador de caminho: No inventário, o caminho relativo poderia ser registrado do jeito
 natural do OS (ex: 
\Fotos\Verão no Windows). Porém, para consistência, é comum usar
 forward slashes
 / em todos, ou alguma normalização, especialmente se consolidar inventários
 de Windows e Linux juntos. Decida e documente no cabeçalho. Ferramentas como CatCLI, por
 exemplo, exibem sempre com 
/ ao navegar no catálogo .
 10
 7
• 
Tamanho e unidade: Salvar tamanho em bytes exatos é melhor, pois é valor objetivo para
 comparações e somas. Não formate em KB/MB no texto – deixe qualquer formatação para
 apresentação posteriormente, se necessário.
 Facilitando deduplicação: Com o inventário estruturado, a deduplicação pode ser feita assim: - Por
 nome e tamanho: primeiro, olhar arquivos com mesmo nome e tamanho. Isso pode encontrar
 possíveis duplicatas, mas também muitos falsos (nomes iguais porém conteúdos diferentes). Ainda
 assim, é um filtro inicial rápido de fazer em texto (por exemplo, usar comandos 
sort e 
uniq no
 Linux para achar linhas duplicadas por nome). - Por hash: O método mais confiável. Com os hashes no
 inventário, basta buscar entradas com o mesmo hash (e geralmente mesmo tamanho) para identificar
 duplicatas exatas. Ferramentas customizadas podem ser escritas para ler o CSV e produzir relatórios de
 duplicatas. - Formato do hash: MD5 é suficientemente único para esse propósito e mais rápido que
 SHA-256. Só tenha o cuidado de tratar arquivos zero-byte (o hash deles será sempre o mesmo valor fixo).
 Também é útil talvez combinar hash + tamanho como chave de unicidade para evitar trombadas
 teóricas.
 • 
Exemplo de dedupe assistido: Um artigo demonstrou eliminar arquivos duplicados calculando
 hash MD5 de todos os arquivos e usando um dictionary para mapear hash->caminho,
 removendo as duplicatas
 14
 15
 . Adaptando isso ao nosso caso, em vez de já remover, podemos
 montar um dicionário hash->{lista de caminhos} para ver quais hashes têm mais de um arquivo
 associado (indicando duplicatas). Se o inventário estiver em CSV, esse dicionário pode ser
 construído facilmente via pandas ou script Python.
 Consideração de performance: Se decidir incluir hash de todos os arquivos no inventário, saiba que
 será a parte mais lenta do processo – ler muitos TB de dados e computar hash. Se o tempo for um
 problema, você pode: - Calcular hashes apenas para arquivos acima de certo tamanho ou de certos
 tipos (por exemplo, fotos/vídeos que são grandes e propensos a duplicatas). - Ou adotar a técnica de
 hash parcial: incluir no inventário um hash dos primeiros N bytes de cada arquivo (ex: 4 KB iniciais). Isso é
 bem rápido e pode ajudar a pré-selecionar duplicatas. Arquivos cujo “hash inicial” difere certamente não
 são duplicatas; aqueles com hash inicial igual podem ser e aí uma hash completa seria calculada
 posteriormente para confirmação. Especialistas sugerem essa abordagem de “sample hash” para
 agilizar – “hashing only the start of each file is a nice way of speeding up finding files that cannot be
 16
 duplicates” . Podemos, por exemplo, armazenar 
hash_prefix_4k no inventário e deixar para
 depois o hash completo apenas quando realmente necessário. (Ver mais na seção de performance.)
 Em suma, o formato de saída recomendado é texto tabular (CSV), com colunas bem definidas e
 incluindo (se viável) um identificador de conteúdo. Isso garantirá que etapas posteriores de
 deduplicação ou reorganização possam ser feitas de forma semi-automatizada e confiável.
