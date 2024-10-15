import os
import sys
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import speech_recognition as sr
import warnings
import keyboard
import time
import subprocess
from datetime import datetime


warnings.filterwarnings("ignore", category=RuntimeWarning)


if getattr(sys, 'frozen', False):
    FFMPEG_PATH = os.path.join(sys._MEIPASS, 'bin', 'ffmpeg.exe')
else:
    FFMPEG_PATH = os.path.join("bin", "ffmpeg.exe")

def escolher_arquivo():
    root = tk.Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)

    caminho_arquivo = filedialog.askopenfilename(
        title="Selecionar arquivo de áudio",
        filetypes=[("Audio Files", "*.wav;*.mp3;*.flac;*.ogg;*.opus")]
    )

    root.attributes("-topmost", False)
    root.destroy()
    return caminho_arquivo

def converter_para_wav(caminho_arquivo):
    caminho_arquivo_wav = "temp.wav"

    if not os.path.exists(FFMPEG_PATH):
        raise FileNotFoundError("O ffmpeg portátil não foi encontrado. Certifique-se de que o executável está no caminho correto.")

    comando = [FFMPEG_PATH, "-i", caminho_arquivo, caminho_arquivo_wav]

    try:
        with subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as proc:
            proc.wait()
        return caminho_arquivo_wav
    except subprocess.CalledProcessError as e:
        print(f"Erro ao converter arquivo: {e}")
        return None

def transcrever_audio(caminho_arquivo):
    try:
        temp_file = None
        if not caminho_arquivo.endswith('.wav'):
            caminho_arquivo = converter_para_wav(caminho_arquivo)
            temp_file = caminho_arquivo

        if not caminho_arquivo:
            return "Erro na conversão do arquivo."

        recognizer = sr.Recognizer()
        with sr.AudioFile(caminho_arquivo) as source:
            audio_data = recognizer.record(source)
            texto = recognizer.recognize_google(audio_data, language='pt-BR')

        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

        return texto
    except Exception as e:
        return f"Erro na transcrição: {e}"

def salvar_transcricao(texto, nome_arquivo):
    diretorio = "Transcrições"
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)

    nome_arquivo_saida = os.path.join(diretorio, f"{nome_arquivo}.txt")

    with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
        f.write(texto)

    print(f"\nTranscrição salva no arquivo: {nome_arquivo_saida}")

def menu_principal():
    while True:
        print("\n--- Transcrever arquivo de áudio para texto ---")
        print("\nPor favor, digite uma das seguintes opções:")
        print("\n1. Selecionar um arquivo de áudio e transcrever")
        print("2. Sair")

        print("\nDigite: ", end="", flush=True)

        while True:
            if keyboard.is_pressed('1'):
                arquivo_selecionado = escolher_arquivo()
                if arquivo_selecionado:
                    print(f'\nArquivo selecionado: {arquivo_selecionado}')
                    print("\nTranscrevendo...")

                    texto_transcrito = transcrever_audio(arquivo_selecionado)

                    root = tk.Tk()
                    root.withdraw()

                    resposta = messagebox.askyesno("Nome do Arquivo", "Nomear arquivo? Escolhendo 'Não' o nome padrão (horário atual) será utilizado.", parent=root)

                    if not resposta:
                        nome_arquivo = datetime.now().strftime("Transcrição %d-%m-%y às %Hh%Mmin%Ss")
                        salvar_transcricao(texto_transcrito, nome_arquivo)
                    else:
                        nome_arquivo = simpledialog.askstring("Nome do Arquivo", "Digite o nome da transcrição (sem extensão):", parent=root)
                        if nome_arquivo:
                            salvar_transcricao(texto_transcrito, nome_arquivo)
                        else:
                            print("Nome do arquivo não fornecido. A transcrição não será salva.")

                    root.quit()
                    root.destroy()

                break
            elif keyboard.is_pressed('2'):
                print("Saindo...")
                return
            time.sleep(0.1)


menu_principal()
