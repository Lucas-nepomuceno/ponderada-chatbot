from chatbot.test import start_chat
from auditoria.agente_fraude_contextual import executar_agente_fraude_contextual
from auditoria.agentes_conspiracao import executar_agente_conspiracao
from auditoria.auditor_rules import executar_auditoria_simples
from dotenv import load_dotenv
import os

load_dotenv()

SENHA = os.getenv("SENHA")

while True:

    print("Bem vindo a IA da Dunder Mifflin\n")
    print("Escolha uma das três opções a seguir, colocando o número correto")
    print("1 - Sou Toby Flenderson")
    print("2 - Sou outro funcionário e quero saber sobre a política de compliance")
    print("3 - Sair")

    escolha_usuario = input()
    if escolha_usuario == "1":
        print("Bem Vindo, Toby!\n")
        senha = input("Digite sua senha:")
        if senha == SENHA:
            while True:
                print("\nEscolha a opção desejada:")
                print("1 - Desejo realizar uma auditoria simples")
                print("2 - Desejo realizar um auditoria de fraude contextual")
                print("3 - Desejo ver se Michael está conspirando contra mim")
                print("4 - Desejo verificar o chat")
                print("5 - Sair")

                escolha_toby = input()

                if escolha_toby == "1":
                    df_violacoes_simples = executar_auditoria_simples()
                    if not df_violacoes_simples.empty:
                        print(f"TOTAL DE VIOLAÇÕES ENCONTRADAS: {len(df_violacoes_simples)}")
                        print("\n--- Amostra de Violações ---")
                        print(df_violacoes_simples.head(10).to_markdown(index=False))
                    else:
                        print("Nenhuma violação direta de compliance encontrada no Nível 3.1.")

                if escolha_toby == "2":
                    executar_agente_fraude_contextual()

                if escolha_toby == "3":
                    executar_agente_conspiracao()

                if escolha_toby == "4":
                    start_chat()

                if escolha_toby == "5":
                    break
        else: 
            print("Senha Incorreta. Saia Michael!\n")

    elif escolha_usuario == "2":
        start_chat()
    elif escolha_usuario == "3":
        break
    else:
        print("Opção inválida. Tente Novamente")


