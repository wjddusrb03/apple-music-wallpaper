Set fso = CreateObject("Scripting.FileSystemObject")
Set WshShell = CreateObject("WScript.Shell")
strPath = fso.GetParentFolderName(WScript.ScriptFullName)
pidFile = strPath & "\server.pid"

If fso.FileExists(pidFile) Then
    Set f = fso.OpenTextFile(pidFile, 1)
    pid = Trim(f.ReadLine)
    f.Close

    ' Stop server
    WshShell.Run "taskkill /F /PID " & pid, 0, True
    fso.DeleteFile pidFile

    ' Stop Lively Wallpaper
    WshShell.Run "taskkill /F /IM Lively.exe", 0, True
    WshShell.Run "taskkill /F /IM Lively.UI.WinUI.exe", 0, True

    MsgBox "Apple Music Wallpaper stopped.", vbInformation, "Apple Music Wallpaper"
Else
    MsgBox "Server is not running.", vbInformation, "Apple Music Wallpaper"
End If
