from google.cloud import texttospeech
from pydub import AudioSegment
import time
import os
from os import listdir
from os.path import isfile, join
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def text2speech (hello_word, output_name):
    # https://cloud.google.com/text-to-speech
    # Codigo foi copiado desse produto da google

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=hello_word)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    arquivo_edit = output_name + ".mp3"


    # The response's audio_content is binary.
    with open(arquivo_edit, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        #print('Audio content written to file {}'.format(arquivo_edit))

def onechaptertxt2multiplepartmp3 (txt_path):
    # Função que lê o capítulo (arquivo de texto) e transforma em N arquivos de mp3, sendo N o output
    arquiv = txt_path
    arquivo_txt = arquiv + ".txt"
    filee=open(arquivo_txt, "r", encoding='utf-8')
    fl =filee.readlines()

    max_char = 0
    trecho = ""
    subchap_count = 0

    for x in range(0, len(fl)):
        max_char = max_char + len(fl[x])
        if max_char >= 4950:
            print("gravando parte {} com {} caracteres".format(subchap_count, max_char - len(fl[x])))
            text2speech(trecho, arquiv + "_particao" + str(subchap_count))
            time.sleep(0.1)
            subchap_count = subchap_count + 1
            max_char = len(fl[x])
            trecho = ""
        trecho = trecho + fl[x]
    
    text2speech(trecho, arquiv + "_particao" + str(subchap_count))
    print("gravando parte {} com {} caracteres".format(subchap_count, max_char))

    return subchap_count + 1

def mp3agg (main_path, subchapter):
    # Função que aglutina todos os N arquivos de mp3 em um arquivo único
    path = main_path + '_particao' + str(0) + '.mp3'
    sound = AudioSegment.from_mp3(path)
    resultante = sound

    for i in range(1,subchapter):
        print("Juntando Particoes {} de {}".format(i, subchapter-1))
        path = main_path+ '_particao' + str(i) + '.mp3'
        sound = AudioSegment.from_mp3(path)
        resultante = resultante + sound
    
    # writing mp3 files is a one liner
    path2 = main_path + ".mp3"
    resultante.export(path2, format="mp3")

    # aqui cabe o delete
    for i in range(0,subchapter):
        path = main_path+ '_particao' + str(i) + '.mp3'
        os.remove(path)

def splittxtbychapter (fl):
    # Função que lê o arquivo de texto e quebra em capítulos, usando uma lista
    chapter = []

    for i in range(0,len(fl)):
        new_chapter = fl[i].find('------------------NEW CHAPTER----------------')
        if new_chapter > -1:
            chapter.append(" ")

    print("Este livro tem {} capítulos".format(len(chapter)))
    chapter.append(" ")

    chap = 0
    for i in range(0,len(fl)):
        new_chapter = fl[i].find('------------------NEW CHAPTER----------------')
        chapter[chap] = chapter[chap] + fl[i]
        if new_chapter > -1:
            chap = chap + 1

    return chapter, chap

def processonechapter (x):
    # Função que transforma cada capítulo (elemento dentro da lista criada) em um arquivo de .mp3
    
    print("Começando chapter {}".format(x))
    arquivo_edit = pasta + "Chapter" + str(x) + ".txt"
    f= open(arquivo_edit,"w+", encoding='utf-8')
    f.write(chapter[x])
    f.close()

    # Função que lê o capítulo (arquivo de texto) e transforma em N arquivos de mp3, sendo N o output
    sub_chap = onechaptertxt2multiplepartmp3(pasta + "Chapter" + str(x))
    # Função que aglutina todos os N arquivos de mp3 em um arquivo único
    mp3agg(pasta + "Chapter" + str(x), sub_chap)
    print("audio capítulo prontos")
    os.remove(arquivo_edit)

def from_epub_to_text (pasta, arquiv, start_chapter, end_chapter):
    # Função que transforma o livro .epub em um documento de txt usando BeautifulSoup
    # o output é um arquivo de texto que é deletado ao final

    f= open(pasta + arquiv + "_raw.txt","w+", encoding='utf-8')
    opening_book = "coded by paula fisch\n"
    opening_chapter = "\n" +  '------------------NEW CHAPTER----------------' + '\n'
    livro_todo = opening_book

    for i in range(int(start_chapter), int(end_chapter) + 1):
        html = capitulos_endereco[i].get_content()
        soup = BeautifulSoup(html, features="lxml")
        conteudo_do_capitulo = soup.get_text()
        livro_todo = livro_todo + opening_chapter  + conteudo_do_capitulo

    print("total de capitulos {}".format(int(end_chapter) + 1 - int(start_chapter)))

    f.write(livro_todo)
    f.close()

    return pasta + arquiv + "_raw.txt"

pasta = input("qual a pasta do seu arquivo ebook?")
arquiv = input("qual o nome do seu arquivo ebook (sem o .epub)?")

arquivo_epub = pasta + arquiv + ".epub"

book = epub.read_epub(arquivo_epub)
capitulos_endereco = []
i = 0

for image in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    print("{} : {}".format(i, image))
    i = i + 1
    capitulos_endereco.append(image)

start_chapter = input("primeiro capitulo será?")
end_chapter = input("ultimo capitulo será?")

# Função que transforma o livro .epub em um documento de txt usando BeautifulSoup
# o output é um arquivo de texto que é deletado ao final
arquivo_txt = from_epub_to_text (pasta, arquiv, start_chapter, end_chapter)

filee=open(arquivo_txt, "r", encoding='utf-8')
fl =filee.readlines()

# Função que lê o arquivo de texto e quebra em capítulos, usando uma lista
chapter, chap = splittxtbychapter(fl)

filee.close()

# Função que transforma cada capítulo (elemento dentro da lista criada) em um arquivo de .mp3
for x in range(1, chap+1):
    processonechapter(x)

os.remove(pasta + arquiv + "_raw.txt")