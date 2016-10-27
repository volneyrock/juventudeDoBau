Post = db.define_table('post',
            Field("autor", "reference auth_user"), # foreign key com a tabela de usuários
            Field("corpo", "text", label="Mensagem"), # Campo do texto
            auth.signature) # Campos para auditoria de registros

# Validadores para Post
Post.corpo.requires = [IS_NOT_EMPTY(error_message="Campo obrigatório"),
    IS_LENGTH(140)]
