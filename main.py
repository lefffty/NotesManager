import os
import json
import zipfile
import csv
import datetime
import platform
import shutil
import logging
import keyboard
import matplotlib.pyplot as plt
from enum import Enum
from collections import defaultdict, Counter
from _collections_abc import MutableMapping
from send2trash import send2trash
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


NOTES_DIR = 'notes'
BACKUP_DIR = 'backups'
CSV_DIR = 'csv'
JSON_DIR = 'json'
PDF_DIR = 'pdf'
ACTIONS_FILE = 'actions.txt'
TXT_EXTENSION = '.txt'
PLOTS_DIR = 'plots'


class Actions(Enum):
    CREATE = 1
    UPDATE = 2
    DELETE = 3


def ensure_directory_exists() -> None:
    """
    Checking directories
    """
    os.makedirs(NOTES_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(CSV_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)


def setup_logging() -> None:
    """
    Setting up logging
    """
    logging.basicConfig(
        filename='logs/basic_logging.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )


def log_note_action(action, note_title) -> None:
    """
    Function that logs user actions, such as creation of note,
    updation of note, deletion of note.

    Parameters
    ------------
    action : Actions
        Type of user action
    note_title : str
        Note`s title
    """
    logging.info(f'Action: {action} | Note: {note_title}')


def list_notes() -> None:
    """
    List of available notes
    """
    notes = [f.lower() for f in os.listdir(NOTES_DIR)
             if f.endswith(TXT_EXTENSION)]
    if not notes:
        print('There is no saved notes')
    else:
        print('===================')
        print('Existing notes:')
        for index, note in enumerate(notes):
            print(f'  {index + 1} - {note[:-4]}')
        print('===================')


def open_note() -> None:
    """
    Function that allows user to choose number of note which he wants to open

    Raises
    -------------
    ValueError
        If `note_number` cannot be converted into int
    """
    list_notes()
    note_number = input('  Enter note number: ')

    try:
        note_num = int(note_number)
        notes = [f for f in os.listdir(NOTES_DIR) if f.endswith(TXT_EXTENSION)]
        if 1 <= note_num <= len(notes):
            path = os.path.join(NOTES_DIR, notes[note_num - 1])
            with open(path, 'r') as file:
                title = notes[note_num - 1]
                content = file.read()
            print(f'\tNote title: {title}')
            print(f'\tNote content: {content}')
            keyboard.wait('esc')
        else:
            print(f'  Note number should be in ({1}, {len(notes)})')
    except ValueError:
        print('  Entered number is not integer!')


def search_note_by_keyword() -> None:
    """
    To search note by entered keyword
    """
    keyword: str = input('  Enter keyword: ').lower()
    found: bool = False

    for note in os.listdir(NOTES_DIR):
        if note.endswith(TXT_EXTENSION):
            with open(os.path.join(NOTES_DIR, note), 'r') as file:
                text = ''.join([line.lower() for line in file.readlines()])
                if keyword in text:
                    print(
                        (f'  Keyword "{keyword}" was found in '
                         f'"{note.removesuffix(TXT_EXTENSION)}" '
                         f'note: {text.count(keyword.lower())}'))
                    found = True

    if not found:
        print('There is no notes which includes entered keyword!')


def create_note() -> None:
    """
    Creation of new note
    """
    title = input('  Enter note title: ')
    content = input('  Enter note content: ')

    filename = os.path.join(NOTES_DIR, f'{title}.txt')

    if os.path.exists(filename):
        print('  Note with that title already exists!')

    with open(filename, 'w') as file:
        file.write(content)

    log_note_action(Actions.CREATE, title)


def update_note() -> None:
    """
    Update note which was chosen by user.

    Raises
    -------------
    ValueError
        If `note_number` cannot be converted into `int`
    """
    list_notes()
    note_number = input('  Enter note number: ')

    try:
        note_num = int(note_number)
        notes = [file for file in os.listdir(
            NOTES_DIR) if file.endswith(TXT_EXTENSION)]
        if 1 <= note_num <= len(notes):
            old_filename = os.path.join(NOTES_DIR, notes[note_num - 1])
            new_title = input('  Enter new note title: ')
            new_content = input('  Enter new note content: ')
            new_filename = os.path.join(NOTES_DIR, f'{new_title}.txt')
            os.rename(old_filename, new_filename)
            with open(new_filename, 'w') as file:
                file.write(new_content)
            log_note_action(Actions.UPDATE, new_title)
        else:
            print(f'Note number should be in ({1}, {len(notes)})')
    except ValueError:
        print('  Entered number is not integer!')


def delete_note() -> None:
    """
    Removing note which was chosen by user.

    Raises
    -------------
    ValueError
        If `note_number` cannot be converted into int
    """
    list_notes()
    note_number = input('  Enter note number: ')

    try:
        note_num = int(note_number)
        notes = [file for file in os.listdir(NOTES_DIR)]
        if 1 <= note_num <= len(notes):
            filename = os.path.join(NOTES_DIR, notes[note_num - 1])
            os.remove(filename)
            log_note_action(Actions.DELETE.name, notes[note_num - 1])
        else:
            print(f'Note number should be in ({1}, {len(notes)})')
    except ValueError:
        print('  Entered number is not integer!')


def send_note_to_trash() -> None:
    """
    Sending note to trash.

    Raises
    -------------
    ValueError
        If `note_number` cannot be converted into int
    """
    list_notes()

    note_number = input('  Enter note number: ')

    try:
        note_num = int(note_number)
        notes = [f for f in os.listdir(NOTES_DIR) if f.endswith(TXT_EXTENSION)]
        if 1 <= note_num <= len(notes):
            filename = os.path.join(NOTES_DIR, notes[note_num - 1])
            if platform.system() == 'Windows':
                send2trash(filename)
            else:
                trash_path = os.path.expanduser("~/.local/share/Trash/files/")
                os.makedirs(trash_path, exist_ok=True)
                shutil.move(filename, trash_path)
            print(f'  {filename} was sent to trash!')
        else:
            print(f'Note number should be in ({1}, {len(notes)})')
    except ValueError:
        print('Note number should be integer!')


def create_backup() -> None:
    """
    Create note`s backup
    """
    timestamp = datetime.datetime.now().date()
    backup_filename = os.path.join(BACKUP_DIR, f'notes_backup_{timestamp}.zip')

    with zipfile.ZipFile(backup_filename, 'w') as zip_file:
        for note in os.listdir(NOTES_DIR):
            if note.endswith(TXT_EXTENSION):
                zip_file.write(os.path.join(NOTES_DIR, note), arcname=note)

    print(f'  Backup {backup_filename} was created!')


def delete_old_backups() -> None:
    """
    Deleting old backups
    """
    now = datetime.datetime.now().date()

    for file in os.listdir(BACKUP_DIR):
        full_path = os.path.join(BACKUP_DIR, file)
        creation_time = os.path.getctime(full_path)
        creation_date = datetime.datetime.fromtimestamp(creation_time).date()
        if (now - creation_date).days >= 1:
            os.remove(full_path)

    print('  Old backups was deleted!')


def export_to_csv() -> None:
    """
    Exporting notes info CSV
    """
    timestamp = datetime.datetime.now().date()
    FILENAME = os.path.join(CSV_DIR, f'{timestamp}.csv')

    notes = []
    for _file in os.listdir(NOTES_DIR):
        if _file.endswith(TXT_EXTENSION):
            full_path = os.path.join(NOTES_DIR, _file)
            with open(full_path, 'r') as file:
                note_dict = defaultdict(str)
                note_dict['title'] = _file
                note_dict['content'] = file.read()
            notes.append(note_dict)

    with open(FILENAME, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['title', 'content'])
        for note in notes:
            writer.writerow(note)

    print('  Notes was exported into CSV')


def export_to_json() -> None:
    """
    Exporting notes info JSON
    """
    timestamp = datetime.datetime.now().date()
    FILENAME = os.path.join(JSON_DIR, f'{timestamp}.json')

    notes = defaultdict(str)
    for _file in os.listdir(NOTES_DIR):
        if _file.endswith(TXT_EXTENSION):
            with open(os.path.join(NOTES_DIR, _file), 'r') as file:
                notes[_file] = file.read()

    with open(FILENAME, 'w') as json_file:
        json.dump(notes, json_file, indent=4, ensure_ascii=False)

    print('  Notes was exported into JSON')


def words_frequency(buffer: str) -> MutableMapping[str, int]:
    """
    Created words frequency dictionary

    Parameters
    ------------
    buffer : str
        Note`s content

    Returns
    ------------
    words_dict : MutableMapping[str, int]
        Words frequency dictionary
    """
    words_dict: defaultdict[str, int] = defaultdict(int)
    words = buffer.split(' ')
    for word in words:
        words_dict[word] += 1
    return words_dict


def semantic_analysis():
    """
    Creates semantic analysis of chosen note

    Returns
    ------------
    words_freq : MutableMapping[str, int]
        Map which contains word frequency for chosen note
    title : str
        Title of note

    Raises
    ------------
    ValueError
        If `note_number` cannot be convert into `int`
    """
    list_notes()
    note_number = input('  Enter number of note you want to analyze: ')

    try:
        note_num = int(note_number)
        notes = [f for f in os.listdir(NOTES_DIR) if f.endswith(TXT_EXTENSION)]
        if 1 <= note_num <= len(notes):
            full_path = os.path.join(NOTES_DIR, notes[note_num - 1])
            title = notes[note_num - 1].removesuffix(TXT_EXTENSION)
            with open(full_path, 'r') as file:
                content = file.read()
            words_freq = words_frequency(content)
            return words_freq, title
        else:
            print(f'  Your number should be in range ({1}, {len(notes)})')
    except ValueError:
        print('  Your number should be integer!')


def export_to_pdf() -> None:
    """
    Converts notes to pdf
    """
    timestamp = datetime.datetime.now().date()
    filename = os.path.join(PDF_DIR, f'{timestamp}.pdf')
    canv = canvas.Canvas(filename, pagesize=A4)

    notes = [f for f in os.listdir(NOTES_DIR) if f.endswith('.txt')]

    x = 15
    y = 780
    dy = 40
    for note in notes:
        with open(os.path.join(NOTES_DIR, note)) as file:
            title = note.removesuffix(TXT_EXTENSION)
            content = file.read()
        canv.drawString(x, y, text=f'Title: {title}')
        canv.drawString(x, y+dy, text=f'Content: {content}')
        y += dy

    canv.save()


def statistics_by_date() -> Counter:
    """
    Creates dictionary of user activity

    Returns
    ------------
    counter : Counter
        User activity dictionary
    """
    notes = [f for f in os.listdir(NOTES_DIR) if f.endswith(TXT_EXTENSION)]
    dates = []
    for note in notes:
        path = os.path.join(NOTES_DIR, note)
        creation_date = datetime.datetime.fromtimestamp(
            os.path.getctime(path)).date()
        dates.append(str(creation_date))
    counter = Counter(dates)
    return counter


def plot_semantic_analysis() -> None:
    """
    Plots note`s semantic analysis
    """
    words_freq, title = semantic_analysis()
    plt.figure(figsize=(200, 100))
    plt.bar(words_freq.keys(), words_freq.values())
    plt.title(f'{title} analysis')
    plt.ylabel('Количество вхождений')
    plt.xlabel('Слово')
    plt.show()


def plot_user_statistics() -> None:
    """
    Plots user activity statictics
    """
    statistics = statistics_by_date()
    TITLE = 'User activity'
    XLABEL = 'Date'
    YLABEL = 'Created notes'
    plt.bar(statistics.keys(), statistics.values())
    plt.title(TITLE)
    plt.xlabel(XLABEL)
    plt.ylabel(YLABEL)
    plt.show()


def main_loop() -> None:
    """
    Main program loop
    """
    while True:
        print('1 - list of notes')
        print('2 - search note by keyword')
        print('3 - create note')
        print('4 - open note')
        print('5 - delete note permanently')
        print('6 - send note to trash')
        print('7 - update note')
        print('8 - create new backup')
        print('9 - delete old backups')
        print('10 - export to JSON')
        print('11 - export to CSV')
        print('12 - export to PDF')
        print('13 - note semantic analysis')
        print('14 - activity diagram')
        print('15 - EXIT')

        choice = (input('Enter your choice: '))
        try:
            _choice = int(choice)
        except ValueError:
            print('Your choice should be integer!')

        match _choice:
            case 1:
                list_notes()
            case 2:
                search_note_by_keyword()
            case 3:
                create_note()
            case 4:
                open_note()
            case 5:
                delete_note()
            case 6:
                send_note_to_trash()
            case 7:
                update_note()
            case 8:
                create_backup()
            case 9:
                delete_old_backups()
            case 10:
                export_to_json()
            case 11:
                export_to_csv()
            case 12:
                export_to_pdf()
            case 13:
                plot_semantic_analysis()
            case 14:
                plot_user_statistics()
            case 15:
                break
    print('Program has finished!')


def main():
    ensure_directory_exists()
    setup_logging()
    main_loop()


if __name__ == '__main__':
    main()
