Modelagem
1 - temos uma tabela de projeto e vamos descendo de nível até task instructions

1- Preenchimento de /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md, que será um formulário.

Os arquivos indicados em /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md são lidos e atualizados. Se houver consulta ao PM, ela deverá ser feita. 

Esse fluxo cria o arquivo de INTAKE , que é a base para criação do Arquivo PRD. 

2 - PM aprova INTAKE
3 - IA GERA  DE PRD BASEADO NO INTAKE
4 - PM APROVA PRD
5 - IA GERA FASES DO PROJETO, BASEADO NO PRD
6 - HUMANO APROVA FASES DO PROJETO
7 - IA GERA ÉPICOS DO PROJETO BASEADO NAS FASES 
8- HUMANO APROVA OS ÉPICOS 
9 - IA GERA SPRINTS  BASEADOS NOS ÉPICOS
10 - HUMANO APROVA SPRINTS
11 - IA GERA ISSUES BASEADOS NOS SPRINTS
12 - HUMANO APROVA ISSUES 
13 - IA GERA TASKS BASEADA NAS ISSUES 
14 - HUMANO APROVA TASKS 
15 - IA GERA INSTRUÇÕES `TDD`PARA AS TASKS
16 - INÍCIO DO PIPELINE DE EXECUÇÃO:

Daqui para baixo, é possível automatizar. 
17 - /Users/genivalfreirenobrejunior/Documents/code/npbb/npbb/PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md. É PREENCHIDO COM OS DADOS DA PRIMEIRA FASE-ÉPICO-SPRINT-ISSUE-TAREFA -  : F1-01-001-T1
18 - IA EXECUTA A TAREFA
19 - EM OUTRA SESSÃO, IA VAI PARA TAREFA T<N+1>  Até o fim  de F1-01-001 , e antes de F1-01-002, quando a issue tem suas tarefas terminadas. 
20 -  O arquivo de revisar ISSUE é configurado, trazendo as informações sobre os Diffs e commits que precisam ser analisados em questão e tudo mais que for necessário. 
21 - IA revisa a issue e decide se está aprovada, bloqueada ou se precisa de correção, e o tipo de correção, de acordo com o que já   é previsto hoje pela governança. 
22 -  Humano é informado
23 - IA cria as novas issues e um novo ciclo desses é realizado. 
24- Ao terminar de implementar uma Fase, inicia-se o processo de auditoria da Fase. 
25 - Humano é informado sobre os achados na auditoria e autoriza as soluções de hold
26 - IA aplica as soluções de hold, usando procedimentos de criação de issues e solução de tarefas já estabelecidos acima. 
27 - Ao terminar uma fase, a IA inicia a próxima, com os mesmos ciclos 
