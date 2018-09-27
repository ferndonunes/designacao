SELECT nome_servidor,  nome_grupo, saldo_servidor_grupo
	FROM servidores, grupos, servidores_grupos
		WHERE id_servidor == id_servidor_servidor_grupo and id_grupo == id_grupo_servidor_grupo
		ORDER BY nome_servidor,  saldo_servidor_grupo