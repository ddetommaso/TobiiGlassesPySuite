import json
import logging
import os
import entities

def load_json_from_file(source_dir, filename):
    logging.info('Importing from JSON file %s in %s' % (filename, source_dir))
    with open(os.path.join(source_dir, filename)) as f:
        res = json.load(f)
    return res

def get_all_projects(projects_dir):
    logging.info('Loading projects in %s' % projects_dir)
    projects = []
    for item in os.listdir (projects_dir):
        if os.path.isdir(os.path.join(projects_dir, item)):
            projects.append(entities.TobiiProject(projects_dir, item))
    return projects

def get_all_recordings(recordings_dir):
    logging.info('Loading recordings from %s' % recordings_dir)
    recordings = []
    for item in os.listdir (recordings_dir):
        if os.path.isdir(os.path.join(recordings_dir, item)):
            rec_dir = os.path.join(recordings_dir, item)
            recordings.append(entities.TobiiRecording(rec_dir))
    return recordings
