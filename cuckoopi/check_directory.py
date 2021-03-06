import os


def check_directory(work_dir: str):
    
    """
    Checks if a specified bird species directory already exists. If not, one is created along with sub-folders
    for eventual audio and photo files.
    """ 
    if not os.path.isdir(work_dir):

        os.system(f"mkdir {work_dir}; chmod -R 777 {work_dir}")
        os.system(f"mkdir {work_dir}/audio; chmod -R 777 {work_dir}/audio")
        os.system(f"mkdir {work_dir}/photo; chmod -R 777 {work_dir}/photo")