 Python oferece módulos prontos para todas as tarefas envolvidas no mapeamento de arquivos:
 • 
• 
• 
• 
• 
• 
• 
Percorrer o sistema de arquivos: 
os.walk() fornece a travessia recursiva de diretórios. Em Python ≥3.5, essa função já está
 otimizada internamente com 
2
 os.scandir() para alto desempenho . 
pathlib.Path.rglob("*") é uma alternativa moderna que retorna iterativamente todos os
 caminhos casando um padrão (e.g. 
"**/*" para todos os arquivos). Internamente, também
 usa 
os.scandir e é equivalente em rapidez, podendo ser mais conveniente pela interface
 orientada a objetos.
 os.scandir() diretamente pode ser usado se quisermos iterar manualmente e acessar
 atributos de entradas de diretório via 
DirEntry (que permite checar tipo, stat, etc., com cache
 de informações). Em muitos casos, simplesmente usar 
os.walk já basta, mas conhecer
 scandir ajuda em otimizações específicas. Nota: O uso de 
scandir reduziu drasticamente
 as chamadas de sistema necessárias para listar arquivos, tornando o 
os.walk() ~8x mais
 rápido no Windows e ~2-3x em POSIX em comparação às abordagens mais antigas .
 Manipulação de paths: 
O módulo 
os.path (e funções como 
os.path.join , 
3
 os.path.getsize , etc.) é
 amplamente usado para construir caminhos e obter atributos básicos. 
O módulo 
pathlib fornece a classe 
Path com métodos como
 .iterdir() , 
.is_file() , 
.stat() , 
.resolve() etc., que podem tornar o código mais
 legível. Por exemplo, 
Path(root) / fname para juntar caminhos, ou 
path.stat().st_mtime para data de modificação.
 • 
• 
• 
Em cenários multiplataforma, 
pathlib lida com diferenças de separadores (
 automaticamente.
 Leitura de metadados: 
os.stat() ou 
\ vs /)
 Path.stat() obtêm informações do arquivo sem abri-lo (tamanho,
 timestamps, permissões). Esses dados são importantes para o inventário. Lembrando que 
2
os.walk já chama 
os.stat internamente para distinguir arquivos de diretórios (embora
 com 
scandir essa necessidade seja minimizada). 
• 
O DirEntry de 
os.scandir possui métodos como 
3
 .stat() , 
.is_file() , 
.is_dir()
 que evitam chamadas extras na maioria dos casos, usando dados retornados pelo sistema
 operacional .
 • 
• 
• 
• 
• 
Cálculo de hash: 
O módulo 
hashlib (parte da biblioteca padrão) permite calcular hashes como MD5, SHA-1,
 SHA-256 etc. Você pode abrir o arquivo em modo binário e ler em blocos, alimentando um
 objeto hash. Exemplo: 
import hashlib
 h = hashlib.md5()
 with open(filepath, "rb") as f:
 for chunk in iter(lambda: f.read(8192), b""):
 h.update(chunk)
 file_hash = h.hexdigest()
 Isso lê o arquivo em pedaços de 8KB (ajustável conforme memória/disco) para evitar carregar
 arquivos grandes inteiros em RAM. Ao final, 
file_hash terá o hash em hexadecimal. Dica:
 para evitar recalcular hash de arquivos que já aparecem duplicados durante a varredura,
 mantenha um dicionário de 
{(tamanho, hash): caminho} ou similar; porém, note que para
 saber que são duplicados você já teria calculado o hash uma vez. Estratégias de cache e
 deduplicação serão discutidas adiante.
 Hash mais rápido: Embora MD5/SHA funcionem, para milhões de arquivos pode ser útil usar
 algoritmos de hash não criptográfico de alta velocidade. Por exemplo, a biblioteca 
4
 5
 xxhash
 (instalável via pip) oferece hashes extremamente rápidos (XXH64, XXH3). Em testes, o XXH64
 pode ser cerca de 10× mais rápido que MD5 ou SHA-256 para calcular checksums de
 integridade . O uso de xxhash ou mesmo do recente BLAKE3 (também disponível em
 Python) pode acelerar a geração de hashes de conteúdo, especialmente em arquivos grandes,
 sem comprometer a confiabilidade na detecção de duplicatas (visto que colisões são raríssimas
 para tais algoritmos). 
de 
Feedback de progresso: Para acompanhar o progresso do scan (visto que milhões de arquivos
 podem demorar horas), a biblioteca tqdm é muito útil. Ela permite envolver iteradores com uma
 barra 
progresso. 
Exemplo: 
for 
root, 
dirs, 
files 
in 
tqdm(os.walk(drive_path)): ... . Como o total de arquivos não é conhecido de antemão
 facilmente, pode-se ao menos exibir o número de arquivos processados até o momento. Outra
 opção é primeiro contar arquivos (o que em si é demorado) ou estimar com base em espaço
 usado. Em todo caso, um progress bar ajuda a monitorar a execução de forma mais amigável. 
Concorrência: Módulos como 
concurrent.futures (com 
ThreadPoolExecutor e
 ProcessPoolExecutor ) podem ser empregados para paralelizar partes do processo. Por
 exemplo:
 3
• 
• 
• 
• 
6
 Multiprocessamento: útil para operações CPU-bound como cálculo de hash em vários arquivos
 simultaneamente. Você pode colher todos os caminhos de arquivos primeiro e então usar um 
ProcessPoolExecutor.map(func, files) para distribuir o cálculo de hashes entre
 múltiplos processos (aproveitando múltiplos núcleos da CPU). Em um exemplo apresentado,
 usar um pool de 4 processos para calcular hashes de arquivos em paralelo acelerou a remoção
 de duplicatas significativamente . 
Multithreading: como a tarefa de listar diretórios é I/O-bound (leitura do disco), threads podem
 ajudar se você tiver vários discos operando em paralelo. Por exemplo, iniciar uma thread para
 varrer cada HD simultaneamente pode praticamente multiplicar a velocidade global (5 HDs em
 paralelo, cada um com seu próprio head de leitura). Em Python, operações de I/O liberam o GIL,
 então threads podem de fato rodar simultaneamente durante espera de disco. Contudo, para 
um mesmo HD, múltiplas threads tendem a atrapalhar mais do que ajudar, pois causam
 movimentação excessiva do braço do disco (seeking) sem aumentar a taxa de leitura sequencial.
 Assim, a recomendação é usar 1 thread ou processo por HD para paralelismo inter-dispositivos,
 mas não exagerar dentro de um único volume. 
◦ 
Em cenários de NAS ou SSD, a concorrência pode trazer ganhos diferentes (um SSD lida
 melhor com IOPS concorrentes, mas num HDD mecânico é melhor sequencial). Um
 estudo empírico mostrou que ao escanear duas pastas grandes, uma abordagem multi
processos obteve desempenho levemente melhor que multi-threading mesmo sendo I/O
bound, possivelmente devido ao número excessivo de threads que o dev criou sem
 benefício real
 7
 8
 . Ou seja, balancear o número de trabalhadores é crítico – mais
 não significa melhor além de um certo ponto.
 Bibliotecas de alto nível como 
asyncio não trazem grande vantagem aqui, já que estamos
 interagindo com operações de bloqueio do sistema de arquivos e não com sockets assíncronos.
 Portanto, manter-se em threads/processos tradicionais é suficiente.
 Filtragem de arquivos: Módulos como 
fnmatch ou 
glob podem ser usados se quisermos
 limitar por extensão/tipo. No exemplo da pergunta original do StackOverflow, usou-se
 fnmatch.filter(files, pattern) para procurar apenas 
.docx em cada dir . No
 nosso caso de inventário completo, provavelmente vamos indexar todos os tipos; mas se houver
 necessidade de ignorar, por exemplo, arquivos temporários, caches ou determinadas pastas do
 sistema, podemos aplicar filtros (e.g. ignorar diretórios com nomes como 
Information , ou pular extensões 
9
 System Volume 
.tmp , etc.). Essa filtragem pode melhorar performance e
 focar nos arquivos de interesse, conforme necessidade.
 10
 12
 13
 11
 Ferramentas prontas relacionadas: Além de escrever seu próprio script, é instrutivo conhecer
 projetos existentes: - CatCLI (Python): mencionado acima, cataloga mídias offline. Pontos fortes: guarda
 metadados (nome, tamanho, hash) e permite busca mesmo com o drive desconectado . Usa JSON
 (textual) como base de catálogo (facilita versionar no git) e pode exportar CSV para análise. Esse projeto
 demonstra uso de técnicas eficientes de leitura e até oferece um Fuse virtual para “montar” o catálogo
 como se fosse um disco (apenas leitura) . - PyFileIndex (Python): biblioteca que cria um índice de
 sistema de arquivos e permite acompanhar alterações. Ela carrega os dados em um DataFrame pandas
 internamente para consultas . É interessante se houver necessidade de atualizar o inventário
 dinamicamente (monitorar adições/remoções), embora para apenas mapear estáticos de 5 HDs, um
 script simples já resolva. - Everything (Windows, utilitário externo): não é Python, mas vale citar – é um
 indexador ultrarrápido de nomes de arquivos em NTFS. Ele utiliza diretamente a MFT do NTFS,
 indexando instantaneamente milhões de nomes. Pode exportar listas de arquivos encontrados. Não
 coleta hashes ou datas, mas se o gargalo for listar nomes, essa ferramenta mostra que é possível
 indexar 3 TB em poucos minutos. Porém, integra-la a nosso fluxo Python exigiria passos adicionais (e
 nossa ênfase é Python, então é mais para referência de velocidade). - Ferramentas de deduplicação:
 1
 4
existem scripts e programas (em várias linguagens) focados em encontrar duplicatas, como 
fdupes
 (C), 
rdfind , etc., e muitos implementações em Python disponíveis no GitHub ou comunidades
 (algumas referenciadas adiante). Eles normalmente fazem aquilo que discutiremos: group by size, hash,
 etc., então podemos nos inspirar neles para a etapa de deduplicação futura.
