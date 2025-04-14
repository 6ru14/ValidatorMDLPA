# Validator MDLPA
This is the repository that will contain the code for the MDLPA Website/Desktop validator

## Table of contents
- [Version 2.0.0](#version-200)

## Updates
### Version 2.0.0

- New Features (for both Desktop/Website):
    - Major overhaul of the way the validator works:
        - It is quicker because of the optimizations done to the code
        - The project has been spread into multiple folders:
            - app (contains the U.I. of the validator)
            - extras (contains the code behind the validation and login)
            - images (contains the images of the project)
            - settings (contains the file that store information about the validator and the style of the validator)
        - New functionality, now the user can update the validator without needing to download the version from the site, it will have a pop-up that will say a new version is up and it can be downloaded

- Bugs:
    - None.

- Bugs fixed:
    - None.

- Miscellaneous:
    - Scripts (the following .py files have been created):
        - 1_PyToExe.py 
            - This file will compile the 'main.py' into an .exe file.
        - 2_Review.py
            - This file will move all the files into the 'Review' folder and the validator will be checked.
        - 3_Dist.py
            - This file will move all the files into a folder named 'Validator_(version)'.
        - 4_ToZip.py
            - This file will zip the folder into an archive, ready to be exported.