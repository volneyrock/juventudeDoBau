@auth.requires_login()
def index():
    jovem = auth.user_id
    com = db((Comunidades.created_by==jovem)|((ComMembership.comunidade==Comunidades.id)&(ComMembership.jovem==jovem)&(ComMembership.situacao=='A'))).select(groupby=Comunidades.id)
    return dict(com=com)

@auth.requires_login()
def membros():
    c_id = request.vars.c_id
    membros = db((ComMembership.comunidade==c_id)&(Comunidades.id==c_id)).select(ComMembership.jovem, Comunidades.created_by, orderby=ComMembership.jovem, distinct=True)
    return dict(membros=membros)

@auth.requires_login()
def c():
    c_id = int(request.vars.c_id)
    #Se não for informado, redirecionar para página 1
    try:
        pagina = int(request.vars.pagina)
    except TypeError:
        redirect(URL('com', 'c', vars={'c_id':c_id, 'pagina':1}))

    jovens = db(c_id == ComMembership.comunidade).count()
    # Posts
    c = db(Comunidades.id == c_id).select()
    if c[0].privada == True:
        member = db((ComMembership.comunidade==c_id)&(ComMembership.jovem==auth.user_id)).count()
        if member != 0:
            post_query = (Post.comunidade == c_id)
        else:
            post_query = 0
    else:
        post_query = (Post.comunidade == c_id)
    try:
        posts = consultaComPaginacao(
                        consulta=db(post_query),
                        pagina=pagina,
                        paginacao=10,
                        filtros={'orderby':~Post.pontos|~Post.created_on},
                    )
    except:
        posts = 0

    # Comentarios
    comentarios =  db(Post.id==Comments.post).select(Post.id)
    votos = set([i.post for i in db(Reacts.jovem==auth.user_id).select(Reacts.post)])
    situacao = db((ComMembership.comunidade == c_id)&(ComMembership.jovem == auth.user_id)).select()
    if c[0].created_by == auth.user_id:
        add_com = A("Configurações", _class='btn btn-primary btn-block', _href=URL(r=request, c='com', f='config', vars={'c_id':c_id}))
    else:
        if not situacao:
            add_com = A("Participar", _class='btn btn-primary btn-block', _href=URL(r=request, c='com', f='participar', vars={'c_id':c_id}))
        elif situacao[0].situacao == 'A':
            add_com = A("Sair", _class='btn btn-danger btn-block', _href=URL(r=request, c='com', f='sair', vars={'c_id':c_id}))

    novo_post = A("Novo Post", _class='btn btn-primary btn-block', _href=URL(r=request, c='default', f='novo_post', vars={'c_id':c_id}))

    return dict(c=c, add_com=add_com, novo_post=novo_post, jovens=jovens, posts=posts, comentarios=comentarios, votos=votos, situacao=situacao)


@auth.requires_login()
def nova_com():
    form = SQLFORM(Comunidades, submit_button="Criar")
    if form.process().accepted:
        response.flash = "Comunidade criada com sucesso :)"
        com = db(Comunidades.nome == form.vars.nome).select(Comunidades.id).first()['id']
        redirect(URL('com', 'c', vars={'c_id':com}))
    elif form.errors:
        response.flash = form.errors

    return dict(form=form)


@auth.requires_login()
def config():
    com = request.vars.c_id
    form = SQLFORM(Comunidades, com, fields=['nome', 'avatar'], upload=URL('default', 'download'), showid=False)
    if form.process().accepted:
        response.flash = "Alterações salvas :)"
        com = db(Comunidades.nome == form.vars.nome).select(Comunidades.id).first()['id']
        redirect(URL('com', 'c', vars={'c_id':com}))
    elif form.errors:
        response.flash = form.errors

    delete_confirmation = 'Tem certeza que deseja excluir essa comunidade?'
    delBtn = A('Apagar comunidade', _href=URL('apaga_com', args=com),
        _message=delete_confirmation,
        _class='btn btn-small btn-danger',
        _id='delBtn'
    )

    return dict(form=form, delBtn=delBtn)


@auth.requires_login()
def apaga_com():
    db((Comunidades.id==request.args(0))&(Comunidades.created_by==auth.user_id)).delete()
    redirect(URL('com', 'index'))


@auth.requires_login()
def participar():
    com = request.vars.c_id
    ComMembership.insert(jovem=auth.user_id, comunidade=com)
    redirect(URL('com', 'c', vars={'c_id':com}))


@auth.requires_login()
def sair():
    com = request.vars.c_id
    db((ComMembership.jovem == auth.user_id)&(ComMembership.comunidade == com)).delete()
    redirect(URL('com', 'c', vars={'c_id':com}))
