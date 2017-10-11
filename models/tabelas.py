REACTS = ['legal', 'ruim']
SITUACAO = ['P', 'A', 'R', 'B'] ## P = Pendente, A = Aprovada, R = Rejeitada, B = Bloqueada


# Comunidades
Comunidades = db.define_table('comunidades',
    Field('nome', 'string', label='Nome:'),
    Field('descricao', 'string', label='Descrição'),
    Field('avatar', 'upload', label='Foto:', default=os.path.join(request.folder, 'static', 'images', 'defaultUpload.jpg'),),
    Field('privada', 'boolean', label='Comunidade Privada?'),
    auth.signature
)
Comunidades.nome.requires = [IS_NOT_EMPTY(error_message="Campo obrigatório"), IS_LENGTH(50)]
Comunidades.descricao.requires = [IS_NOT_EMPTY(error_message="Campo obrigatório"), IS_LENGTH(200)]
Comunidades.nome.requires = IS_NOT_IN_DB(db, db.comunidades.nome, error_message='Essa comunidade já existe, ou o campo está em branco.')

ComMembership = db.define_table('commembership',
    Field('jovem', 'reference auth_user'),
    Field('comunidade', 'reference comunidades'),
    Field('administrador', 'boolean', default = False),
    Field('situacao', 'string', default = 'A'),
)
ComMembership.comunidade.requires = IS_IN_DB(db, 'comunidades.id', '%(nome)s')
ComMembership.situacao.requires = IS_IN_SET(SITUACAO)


# Posts e comentários
Post = db.define_table('post',
    Field('titulo', 'string', label='Título'),
    Field('corpo', 'text', label='Mensagem'), # Campo do texto
    Field('pontos', 'integer', label='Pontos', default=0),
    Field('comunidade', 'reference comunidades'),
    auth.signature # Campos para auditoria de registros
)
Post.titulo.requires = [IS_NOT_EMPTY(error_message="Campo obrigatório"), IS_LENGTH(50)]
Post.corpo.requires = [IS_NOT_EMPTY(error_message="Campo obrigatório"),]
query = db((Comunidades.created_by==auth.user_id)|((ComMembership.comunidade==Comunidades.id)&(ComMembership.jovem==auth.user_id)&(ComMembership.situacao=='A'))).select(groupby=Comunidades.id)
com = {i.comunidades.id:i.comunidades.nome for i in query}
Post.comunidade.requires = IS_IN_SET(com, zero=T('Escolha uma comunidade'), error_message='Escolha uma comunidade.')

Reacts = db.define_table('reacts',
    Field('post', 'reference post'),
    Field('jovem', 'reference auth_user'),
    Field('react', 'string'),
)
Reacts.post.requires = IS_IN_DB(db, db.post)
Reacts.react.requires = IS_IN_SET(REACTS)

Comments = db.define_table('comments',
    Field('post', 'reference post'),
    Field('comentario', 'text', label=T('Comentar')),
    auth.signature# Campos para auditoria de registros
)


## Situação de amizade
Amigos = db.define_table('amigos',
    Field('solicitante', 'reference auth_user'),
    Field('solicitado', 'reference auth_user'),
    Field('situacao', 'string', default = 'P'),
    auth.signature
)
Amigos.situacao.requires = IS_IN_SET(SITUACAO)
