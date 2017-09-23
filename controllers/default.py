# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    redirect(URL("timeline"))
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def timeline():
    #Se não for informado, redirecionar para página 1
    try:
        pagina = int(request.vars.pagina)
    except TypeError:
        redirect(URL('default', 'timeline', vars={'pagina':1}))

    form = SQLFORM(Post, submit_button="Postar") # Formulário postar
    if form.process().accepted:
        response.flash = "Mensagem postada com sucesso :)"

    posts = consultaComPaginacao(
                    consulta=db(Post),
                    pagina=pagina,
                    paginacao=10,
                    filtros={'orderby':~Post.pontos|~Post.created_on},
                )
    if request.extension in ['json', 'xml']:
        return dict(posts=posts.as_list())# Garante formatação para json e xml

    comentarios =  db(Post.id==Comments.post).select(Post.id)
    votos = set([i.post for i in db(Reacts.jovem==auth.user_id).select(Reacts.post)])
    return dict(form=form, posts=posts, comentarios=comentarios, votos=votos)

def novos():
    #Se não for informado, redirecionar para página 1
    try:
        pagina = int(request.vars.pagina)
    except TypeError:
        redirect(URL('default', 'novos', vars={'pagina':1}))

    posts = consultaComPaginacao(
                    consulta=db(Post),
                    pagina=pagina,
                    paginacao=10,
                    filtros={'orderby':~Post.created_on},
                )
    if request.extension in ['json', 'xml']:
        return dict(posts=posts.as_list())# Garante formatação para json e xml

    comentarios =  db(Post.id==Comments.post).select(Post.id)
    votos = set([i.post for i in db(Reacts.jovem==auth.user_id).select(Reacts.post)])
    return dict(posts=posts, comentarios=comentarios, votos=votos)


def post():
    post_id = request.args(0)
    post = db(Post.id == post_id).select().first()
    comments = db(Comments.post == post_id).select()
    form = SQLFORM(Comments, submit_button="Comentar", fields=['comentario']) # Formulário comentar
    form.vars.post = post_id
    form.process()
    if form.accepted:
        response.flash = "Mensagem postada com sucesso :)"
        redirect(URL('default', 'post', args=post_id))
    elif form.errors:
        response.flash = form.errors
    return dict(post=post, comments=comments, form=form)


@auth.requires_login()
def amigos():
    ##Seleciona pedidos de amizade enviados ao usuário logado
    convites = db((Amigos.solicitado==auth.user_id) & (Amigos.situacao=="P")).select()
    ##Seleciona todos os pedidos de amizade pendentes
    pendentes = db(((Amigos.solicitante==auth.user_id) | (Amigos.solicitado==auth.user_id)) & (Amigos.situacao=="P")).select()
    ## Seleciona todos os amigos aprovados.
    amigos = db(((Amigos.solicitante==auth.user_id) | (Amigos.solicitado==auth.user_id)) & (Amigos.situacao=="A")).select()

    return dict(convites=convites, amigos=amigos)


@auth.requires_login()
def perfil():
    user_id = request.vars.user_id
    try:
        pagina = int(request.vars.pagina)
    except TypeError:
        redirect(URL('default', 'perfil', vars={'pagina':1, 'user_id':user_id}))
    user = db(db.auth_user.id==user_id).select()
    query = (Post.created_by==user_id)
    myposts = consultaComPaginacao(
                    consulta=db(query),
                    pagina=pagina,
                    paginacao=10,
                    filtros={'orderby':~Post.pontos|~Post.created_on},
                )
    comentarios =  db(Post.id==Comments.post).select(Post.id)
    votos = set([i.post for i in db(Reacts.jovem==auth.user_id).select(Reacts.post)])

    situacao = db(((Amigos.solicitante==user_id) | (Amigos.solicitado==user_id)) & ((Amigos.solicitante==auth.user_id) | (Amigos.solicitado==auth.user_id))).select()
    amigos = db(((Amigos.solicitante==user_id) | (Amigos.solicitado==user_id)) & (Amigos.situacao=="A")).count()
    if user[0].id == auth.user_id: # Se for eu mesmo
        add_amigo = ''
    elif not situacao: # Se não houver solicitações
        add_amigo = A("Adicionar amigo", _class='btn btn-primary btn-block', _href=URL(r=request, c='default', f='add_amigo', vars={'user_id':user_id}))
    elif situacao[0].situacao == "A": # Se já for amigo
        add_amigo = A("Amigos", _class='btn btn-primary btn-block disabled')
    elif situacao[0].situacao == "P": # Se tiver pedido pendente
        add_amigo = A("Pedido de amizade pendente", _class='btn btn-primary btn-block disabled')

    return dict(user=user, myposts=myposts, add_amigo=add_amigo, comentarios=comentarios, votos=votos, amigos=amigos)


@auth.requires_login()
def add_amigo():
    convidado = request.vars.user_id
    Amigos.insert(solicitante=auth.user_id, solicitado=convidado)
    redirect(URL('perfil', vars={'user_id':convidado}))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


def aceitar_amigo():
    solicitante = request.vars.user_id
    db((Amigos.solicitante == solicitante) & (Amigos.solicitado == auth.user_id)).update(situacao='A')
    session.flash = "Amizade aceita"
    redirect(URL('amigos'))

def curtir():
    post = request.vars.id
    react = request.vars.voto
    pontos = db(Reacts.post == post).count()
    votos = set([i.post for i in db(Reacts.jovem==auth.user_id).select(Reacts.post)])

    form1 = SQLFORM.factory(submit_button="Curtir")
    form2 = SQLFORM.factory(submit_button="Descurtir")
    form1.custom.submit.update(_class='btn-info')
    form2.custom.submit.update(_class='btn-danger')
    if int(post) in votos:
        form = form2
        if form.process().accepted:
            db((Reacts.post==post)&(Reacts.jovem==auth.user_id)).delete()
            pontos = db(Reacts.post == post).count()
            db(Post.id==post).update(pontos=pontos)
            redirect(URL('default', 'curtir', vars={'id':post}))
    else:
        form = form1
        if form.process().accepted:
            Reacts.insert(post=post, jovem=auth.user_id, react=react)
            pontos = db(Reacts.post == post).count()
            db(Post.id==post).update(pontos=pontos)
            redirect(URL('default', 'curtir', vars={'id':post}))

    return dict(pontos=pontos, form=form)


@auth.requires_login()
def deleta_post():
    db((Post.id==request.vars.post)&(Post.created_by==auth.user_id)).delete()
    session.flash = 'Post apagado'
    redirect(URL('default', request.vars.page))

def deleta_comentario():
    db((Comments.id==request.vars.comentario)&(Comments.created_by==auth.user_id)).delete()
    session.flash = 'Comentário apagado'
    redirect(URL('default', 'post', args=request.vars.post_id))



# def pontos():
#     post_id = request.vars.id
#     pontos = db(Reacts.post == post_id).count()
#     return str(pontos)
