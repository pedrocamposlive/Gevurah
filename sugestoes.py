sugestoes_base = {
    "Supino Reto": ["Supino Inclinado", "Supino Declinado", "Flexão de Braço"],
    "Agachamento Livre": ["Leg Press", "Agachamento no Smith", "Cadeira Extensora"],
    "Puxada Frente": ["Barra Fixa", "Remada Baixa", "Pulldown"],
    "Desenvolvimento Halteres": ["Desenvolvimento Barra", "Elevação Lateral", "Arnold Press"],
    "Rosca Direta": ["Rosca Martelo", "Rosca Scott", "Rosca Concentrada"],
    "Tríceps Corda": ["Tríceps Testa", "Tríceps Banco", "Tríceps Pulley"]
}

def buscar_sugestoes(nome_exercicio):
    return sugestoes_base.get(nome_exercicio, ["Variante 1", "Variante 2", "Variante 3"])
