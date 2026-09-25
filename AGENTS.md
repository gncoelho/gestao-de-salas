# Criando codigo
Sempre que criar codigo voce nao deve inventar links ou features que nao foram pedidas
Sempre que criar ou alterar o frontend de uma tela, ao terminar a historia lembre de levantar a tela e tirar um screenshot dela.

# Python
Siga PEP 8 e o estilo idiomatico do Django.
Use `snake_case` para funcoes, metodos e variaveis; `PascalCase` para classes; `UPPER_SNAKE_CASE` para constantes.
Prefira `get_user_model()` em vez de importar `User` direto quando o codigo for de autenticacao.
Views, forms e models devem ficar simples: uma responsabilidade por funcao, sem logica extra que nao foi pedida.
Type hints so quando deixam o codigo mais claro; nao anote tudo so por anotar.
Nao use `print` para debug em codigo que vai ser commitado; use o logger do Django se precisar registrar algo.
Imports: stdlib, depois terceiros, depois apps locais. Evite imports circulares e wildcard (`from x import *`).
Nao ignore excecoes vazias (`except Exception: pass`). Capture o erro especifico ou deixe subir.

# Ruff
O lint e o formatador do projeto e o Ruff. Antes de finalizar codigo Python, o arquivo deve passar no Ruff (lint + format).
Nao desabilite regras com `# noqa` sem um motivo real e local (na linha).
Prefira o que o Ruff corrige automaticamente: aspas consistentes, imports ordenados, espacos, linhas em branco.
Evite codigo morto, imports nao usados, comparacoes `== True`/`== False` e `f-strings` sem interpolacao.
Nao adicione configs, plugins ou ignores globais de Ruff se ninguem pediu.

# Frontend
Vanilla JS. Sem jQuery, React, Vue ou outro framework, a menos que o usuario peca.
Bootstrap 5: use as classes utilitarias e componentes do Bootstrap (`container`, `row`, `col-*`, `btn`, `form-control`, `card`, `mb-*`, `d-flex`, etc.) antes de criar CSS novo.
Use o `base.html` como template base sempre que possivel.
JS no HTML: scripts no final do body (o `base.html` ja carrega o bundle do Bootstrap). Prefira `defer` se o script for em arquivo separado.
JS vanilla: `const`/`let` (nunca `var`), funcoes pequenas, eventos com `addEventListener`, selecione o DOM de forma especifica (`querySelector` / `getElementById`). Nao polua `window`.
Nao use `innerHTML` com dados do usuario; use `textContent` ou crie elementos com `createElement`.
Formularios Django: mantenha `{% csrf_token %}` e as classes Bootstrap nos campos (`form-control`, `form-label`, `form-select`, `btn`).

# CSS
Quando precisar de CSS proprio (algo que o Bootstrap nao cobre), nomeie classes com o padrao css:
- Bloco: `.sala-card`
- Elemento: `.sala-card__title`
- Modificador: `.sala-card--destaque`, `.sala-card__title--muted`
Nao encadeie mais de um elemento (`__`) no nome. Nao misture BEM com nomes genericos (`box1`, `redText`).
Nao use IDs como seletor de estilo. Evite `!important`.
Nao copie utilitarios do Bootstrap em CSS custom (`margin`, `flex`, cores de botao): use as classes do Bootstrap.

# Testing
If you want to run the manage.py runserver, first check that its not yet running. If it is running (use ps), kill it first.
