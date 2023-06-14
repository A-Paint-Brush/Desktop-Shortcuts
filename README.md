# Desktop Shortcuts

![Screenshot](https://github.com/A-Paint-Brush/Desktop-Shortcuts/assets/96622265/d34d50d3-121e-4bf3-afd2-c720625518cf)

This is a virtual desktop program that allows you to configure the icon and command of each shortcut. The program window will cover the real desktop while still allowing other program windows to open normally.

## Installation

Run `pip3 install -r requirements.txt` to install necessary packages.

## How to Use

After launching the program, a directory named `.desktop_shortcuts` should be created in your home directory. Open the file `userconfig.xml` inside the directory, and edit it to change various settings. Note that there is no need to close this program while editing. Once you've saved your changes, go back to the virtual desktop. Right click anywhere and click the "Refresh Shortcuts" option to make your changes take effect. All on-screen elements except for the context menu will update to reflect the changes. To make changes to the context menu take effect, the program has to be restarted.

To exit the desktop, select the "Quit" option in the context menu. Say "yes" to the confirmation dialog, and the program will close.

### Config Format

The children of the `<settings>` tag are all visual attributes. The `<resolution>` tag controls the size of the virtual desktop window, and the format should be two numbers separated by the lowercase English 'X' character. Eg: `800x600`. Make sure to not set the resolution of the program to your full monitor resolution, as that might cause the bottom of the program window to be overlapped by the OS's taskbar.

The `<wallpaper>` tag should contain an absolute or relative path to an image file in a format supported by the `Pillow` module. `/` (slash) should be used as the path seperator, as this program will automatically convert path separators if on Windows.

The remaining tags in `<settings>` should contain an integer without any non-numeric characters.

The children of the `<shortcuts>` tag is where the actual shortcuts are defined. Shortcuts are defined by adding `<button>` elements to this tag. The `<button>` element should contain inner text and 2 attributes: `label_text`, and `icon_path`. The value of `label_text` will be displayed as the name of the shortcut, while `icon_path` will be used to load the icon of the shortcut. The inner text of the tag stores the command which will be run when the shortcut is clicked. Shortcuts that point to an invalid or non-existent image file will be skipped and have no icon. A warning will also be displayed when the icons are refreshed if missing icons are detected. The shortcuts will be loaded in the order they are defined in the config file.

### Commands

Because this program already runs from a console application (the Python interpreter), the output of shortcut commands will be displayed in the same terminal this program is running in. If you want a shortcut to run its command in a new terminal window, you'll have to call the OS's terminal emulator and pass the shell/executable command to it. The name of the terminal emulator and the syntax of passing a command to it will depend on the OS you use.

## Credits

I got the default icon from [IconFinder](https://www.iconfinder.com/), and the default wallpaper from [ReviOS](https://revi.cc/). The reason for that is because I developed most of this project on a public computer running ReviOS.
