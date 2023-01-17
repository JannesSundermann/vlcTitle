import ffmpeg

def ffmpegSimple(input, output, quiet=False, overwrite=False):
    stream = ffmpeg.input(input)
    stream = ffmpeg.output(stream, output)
    ffmpeg.run(stream, quiet=quiet, overwrite_output=overwrite)

#funktioniert so:
#ffmpegSimple(input="C:\\Users\\super\\Desktop\\Cat turned into bread.mp4", output="C:\\Users\\super\\Desktop\\Cat turned into bread.mp3", overwrite=True, quiet=True)

def convertSeconds(seconds): 
    min, sec = divmod(seconds, 60) 
    hour, min = divmod(min, 60)
    return "%d:%02d:%02d" % (hour, min, sec)

#funktioniert so:
#print(convertSeconds(450))

def writeIt(filename, output, encoding="utf-8"):
    with open(filename, "w",encoding=encoding) as file:
        file.write(output)
        
#funktioniert so:
#writeIt("text.txt", "poggers") writeIt("text.txt", "poggers", "encdoding typ oder so")