# Função de paginação das pesquisas
# Retorna:
## resultado[0] = registros
## resultado[1] = total de páginas
## resultado[2] = total de itens
def consultaComPaginacao(consulta, pagina=1, paginacao=5, campos=[], filtros={}):
    paginacao = int(paginacao)
    pagina = int(pagina)
    if pagina <= 0:
        redirect(URL(vars={'pagina':1}))
    total = int(consulta.count())
    paginas = int(total/paginacao)
    if total%paginacao:
        paginas+=1
    if pagina > paginas:
        redirect(URL(vars={'pagina':paginas}))
    limites = (paginacao*(pagina-1), (paginacao*pagina))
    registros = consulta.select(
            limitby=limites,
            *campos,
            **filtros
            )
    return (registros, paginas, total)
