REACTS = ['legal', 'ruim']
Post = db.define_table('post',
    Field("autor", "reference auth_user"), # foreign key com a tabela de usuários
    Field("corpo", "text", label="Mensagem"), # Campo do texto
    Field('pontos', 'integer', label='Pontos', default=0),
    auth.signature # Campos para auditoria de registros
)
## Validadores para Post
Post.corpo.requires = [IS_NOT_EMPTY(error_message="Campo obrigatório"),
    IS_LENGTH(140)]

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
## P = Pendente, A = Aprovada, R = Rejeitada, B = Bloqueada
Amigos = db.define_table('amigos',
    Field('solicitante', 'reference auth_user'),
    Field('solicitado', 'reference auth_user'),
    Field('situacao', 'string', default = 'P'),
    auth.signature
)
