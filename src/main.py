from chatbot import start_chat
from auditoria import executar_agente_fraude_contextual, executar_agente_conspiracao, executar_auditoria_simples
from dotenv import load_dotenv
import os

load_dotenv()

SENHA = os.getenv("SENHA")

print("Bem vindo ao IA da Dunder Mifflin\n")
print("Escolha uma das três opções a seguir, colocando o número correto\n")
print("1 - Sou Toby Flenderson\n")
print("2 - Sou outro funcionário e quero saber sobre a política de compliance\n")

escolha_usuario = input()

if escolha_usuario == "1":
    print("Bem Vindo, Toby!\n")
    senha = input("Digite sua senha:")
    if senha == SENHA:
        print("Escolha a opção desejada:\n")
        print("1 - Desejo realizar uma auditoria simples\n")
        print("2 - Desejo realizar um auditoria de fraude contextual")
        print("3 - Desejo verificar o chat")

        escolha_toby = input()

        if escolha_toby == "1":
            executar_auditoria_simples()
        
        if escolha_toby == "2":
            executar_agente_fraude_contextual()

        if escolha_toby == "3":
            start_chat()
else if escolha_usuario:


