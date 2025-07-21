import os
# import json
import zipfile
# import csv
import datetime


NOTES_DIR = 'notes'
BACKUP_DIR = 'backups'
TXT_EXTENSION = '.txt'


def ensure_directory_exists() -> None:
    """
    To check dirs
    """
    os.makedirs(NOTES_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)


def list_notes() -> None:
    """
    List of notes
    """
    notes = sorted([f for f in os.listdir(NOTES_DIR)
                   if f.endswith(TXT_EXTENSION)], key=str.__len__, reverse=True)
    if not notes:
        print('There is no saved notes')
    else:
        print('===================')
        print('Existing notes:')
        for index, note in enumerate(notes):
            print(f'  {index + 1} - {note[:-4]}')
        print('===================')


def search_note_by_keyword() -> None:
    """
    To search note by entered keyword
    """
    keyword: str = input('  Enter keyword: ').lower()
    found: bool = False
    max_words = 25

    for note in os.listdir(NOTES_DIR):
        if note.endswith(TXT_EXTENSION):
            with open(note, 'r') as file:
                text = ''.join([line.lower() for line in file.readlines()])
                if keyword in text:
                    content = text.split()
                    print(
                        (f'  Keyword "{keyword}" was found in '
                         f'{note.removesuffix(TXT_EXTENSION)}" note'))
                    print(content[:max_words])
                    found = True

    if not found:
        print('There is no notes which includes entered keyword!')


def create_note():
    """
    Создание новой заметки
    """
    title = input('  Enter note title: ')
    content = input('  Enter note content: ')

    filename = os.path.join(NOTES_DIR, f'{title}.txt')

    if os.path.exists(filename):
        print('  Note with that title already exists!')

    with open(filename, 'w') as file:
        file.write(content)

    print(f'  Note "{title}" was created!')


def update_note() -> None:
    """
    Update note
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
            print(f'  File {notes[note_num - 1]} was successfully updated!')
    except ValueError:
        print('  Entered number is not integer!')


def delete_note() -> None:
    """
    To delete note
    """
    list_notes()
    note_number = input('  Enter note number: ')

    try:
        note_num = int(note_number)
        notes = [file for file in os.listdir(NOTES_DIR)]
        if 1 <= note_num <= len(notes):
            filename = os.path.join(NOTES_DIR, notes[note_num - 1])
            os.remove(filename)
            print(f'  {filename} was deleted!')
    except ValueError:
        print('  Entered number is not integer!')


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
    pass


def export_to_csv():
    pass


def export_to_json():
    pass


def main():
    ensure_directory_exists()
    while True:
        print('1 - list of notes')
        print('2 - search note by keyword')
        print('3 - create note')
        print('4 - delete note')
        print('5 - update note')
        print('6 - create new backup')
        print('7 - export to JSON')
        print('8 - export to CSV')
        print('9 - EXIT')

        choice = (input('Enter your choice: '))
        try:
            choice = int(choice)
        except ValueError:
            print('Your choice should be integer!')

        match choice:
            case 1:
                list_notes()
            case 2:
                search_note_by_keyword()
            case 3:
                create_note()
            case 4:
                delete_note()
            case 5:
                update_node()
            case 6:
                create_backup()
            case 7:
                export_to_json()
            case 8:
                export_to_csv()
            case 9:
                break
    print('Program has finished!')


if __name__ == '__main__':
    main()
