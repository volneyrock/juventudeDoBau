Post = db.define_table('post',
            Field("autor", "reference auth_user"), # foreign key com a tabela de usuários
            Field("corpo", "text", label="Mensagem"), # Campo do texto
            auth.signature) # Campos para auditoria de registros

## Validadores para Post
Post.corpo.requires = [IS_NOT_EMPTY(error_message="Campo obrigatório"),
    IS_LENGTH(140)]

## Situação de amizade
## P = Pendente, A = Aprovada, R = Rejeitada, B = Bloqueada
Amigos = db.define_table('amigos',
            Field('solicitante', 'reference auth_user'),
            Field('solicitado', 'reference auth_user'),
            Field('situacao', 'string', default = 'P'),
            auth.signature)
