from dearpygui.core import *
from dearpygui.simple import *
import os
import subprocess
import eyed3
script_dir = os.path.dirname(__file__)
MEDIA_PATH = script_dir + r'\media'
def open_folder(sender, data): subprocess.Popen(['explorer',MEDIA_PATH])

def file_picker(sender,data):
    open_file_dialog(callback=apply_selected_file)

def apply_selected_file(sender,data):
    print(data)
    file_path = os.path.join(data[0],data[1])
    set_value('SelectedAudioFile', file_path)

def split_command(sender,data):
    timestamps = get_value('timestamps').split('\n')

    songs = {}
    for i in range(len(timestamps)):
        print(timestamps[i])
        start = timestamps[i].split()[0]
        if i == len(timestamps)-1:
            end = ''
        else:
            end = timestamps[i+1].split()[0]
        name = timestamps[i][len(start)+1:]
        songs[i+1] = {'start':start,'end':end,'name':name}

    #print(songs)
    path = get_value('SelectedAudioFile')
    if path:
        delete_item('split')
        add_progress_bar('progressbar',parent='Window1')
        _,tail = os.path.split(path)
        artist, album = tail.split(' - ')
        ext = path.split('.')
        ext = ext[len(ext)-1]
        album = album[:len(album)-4]

        OUTPUT_PATH = MEDIA_PATH + f'\\{artist}'
        try:
            os.mkdir(OUTPUT_PATH)
        except FileExistsError:
            pass
        OUTPUT_PATH += f'\\{album}\\'
        try:
            os.mkdir(OUTPUT_PATH)
        except FileExistsError:
            pass

        progress_step = float(1)/(len(songs.keys()) * 2)
        for tracknum, d in songs.items():
            set_value('progressbar',get_value('progressbar')+progress_step)
            print(tracknum, d)
            output_file = OUTPUT_PATH + d['name']+'.'+ext

            start = f"-ss {d['start']}"
            end = f"-to {d['end']}" if d['end'] else ''

            command = f'ffmpeg -i "{path}" {start} {end} "{output_file}"'
            print(command)
            subprocess.Popen(command).wait()
            set_value('progressbar',get_value('progressbar')+progress_step)
            af = eyed3.load(output_file)
            af.tag.artist = artist
            af.tag.album = album
            af.tag.title = d['name']
            af.tag.track_num = tracknum
            af.tag.save()

        delete_item('progressbar')
        add_button('split',parent='Window1',callback=split_command)



with window('Window1'):
    add_button('open media folder',callback=open_folder)
    add_text('SelectedAudioFile')
    add_button('open_file',callback=file_picker)
    add_input_text('timestamps',multiline=True,height=600,width=700)
    add_button('split',callback=split_command)


set_main_window_size(700,900)
set_main_window_resizable(False)
set_main_window_title('Playlist Splitter')
THEMES='''Classic, Light, Grey, Dark Grey, Dark, Dark 2, Cherry, Purple, Gold, Red'''.split(', ')
set_theme(THEMES[2]) # 5
start_dearpygui(primary_window='Window1')
